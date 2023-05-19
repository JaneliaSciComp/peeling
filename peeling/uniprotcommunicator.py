import re
from datetime import datetime
import zlib
from urllib.parse import urlparse, parse_qs, urlencode
import httpx
import asyncio
import csv
import pandas as pd
from abc import ABC, abstractmethod
import logging
from peeling.cellular_compartments import cellular_compartments

logger = logging.getLogger('peeling')


# surface = true positive
# cyto = false positive

TIME_OUT = 600
MAX_KEEPALIVE_CONNECTIONS=10
MAX_CONNECTIONS=15
CONNECT_RETRY = 5
MAX_CHECK_RETRY = 10
POLLING_INTERVAL = 5
API_URL = "https://rest.uniprot.org"

CHUNK_SIZE = 2000 #TODO: tune CHUNK_SIZE

class UniProtCommunicator(ABC):
    def __init__(self, cache=False, cellular_compartment='cs'):
        self.__save = cache
        self.__client = None
        self._annotation_true_positive = None
        self._annotation_false_positive = None
        self.__cellular_compartment = cellular_compartments.get(cellular_compartment, None)
        self._cc_code = cellular_compartment


    def __create_client(self):
        limits = httpx.Limits(max_keepalive_connections=MAX_KEEPALIVE_CONNECTIONS, max_connections=MAX_CONNECTIONS)
        transport = httpx.AsyncHTTPTransport(retries=CONNECT_RETRY)
        self.__client = httpx.AsyncClient(http2=True, timeout=TIME_OUT, limits=limits, transport=transport, event_hooks={'response': [self.__check_response]})


    async def __check_response(self, response):
        try:
            await response.aread()
            if response.status_code == 303:
                return
            response.raise_for_status()
        except httpx.HTTPStatusError:
            logger.info(response.json())
            raise


    async def __submit_id_mapping(self, ids):
        response = await self.__client.post(
            f"{API_URL}/idmapping/run",
            data={"from": 'UniProtKB_AC-ID', "to": 'UniProtKB', "ids": ",".join(ids)},
        )
        return response.json()["jobId"]


    def __get_next_link(self, headers):
        re_next_link = re.compile(r'<(.+)>; rel="next"')
        if "Link" in headers:
            match = re_next_link.match(headers["Link"])
            if match:
                return match.group(1)


    async def __check_id_mapping_results_ready(self, job_id):
        trial = 0
        while trial < MAX_CHECK_RETRY:
            trial += 1
            response = await self.__client.get(f"{API_URL}/idmapping/status/{job_id}")
            if response.status_code == 303:
                return response.headers.get('location')
            j = response.json()
            if "jobStatus" in j:
                if j["jobStatus"] == "RUNNING":
                    logger.debug(f"{job_id}: Retrying in {POLLING_INTERVAL}s")
                    await asyncio.sleep(POLLING_INTERVAL)
                else:
                    raise Exception(j["jobStatus"])
            else:
                return bool(j["results"] or j["failedIds"])
        raise Exception('Reach max trials for check job status')


    async def __get_batch(self, batch_response, compressed):
        batch_url = self.__get_next_link(batch_response.headers)
        while batch_url:
            batch_response = await self.__client.get(batch_url)
            yield self.__decode_results(batch_response, compressed)
            batch_url = self.__get_next_link(batch_response.headers)


    def __combine_batches(self, all_results, batch_results):
        return all_results + batch_results[1:]


    # async def __get_id_mapping_results_link(self, job_id):
    #     url = f"{API_URL}/idmapping/details/{job_id}"
    #     response = await self.__client.get(url)
    #     return response.json()["redirectURL"]


    def __decode_results(self, response, compressed):
        if compressed:
            decompressed = zlib.decompress(response.content, 16 + zlib.MAX_WBITS)
            return [line for line in decompressed.decode("utf-8").split("\n") if line]
        else:
            return [line for line in response.text.split("\n") if line]


    async def __get_id_mapping_results_search(self, url):
        parsed = urlparse(url)
        query = parse_qs(parsed.query)
        file_format = "tsv"
        query['format'] = file_format
        size = 500
        query["size"] = size
        compressed = True
        query['compressed'] = compressed
        parsed = parsed._replace(query=urlencode(query, doseq=True))
        url = parsed.geturl()
        response = await self.__client.get(url)
        results = self.__decode_results(response, compressed)
        async for batch in self.__get_batch(response, compressed):
            results = self.__combine_batches(results, batch)
        return results


    async def __get_annotation_results_search(self, url):
        logger.debug(f'fetching data from: {url}')
        response = await self.__client.get(url)
        results = self.__decode_results(response, True)
        async for batch in self.__get_batch(response, True):
            results = self.__combine_batches(results, batch)
        return results


    def __get_data_frame_from_tsv_results(self, tsv_results):
        reader = csv.DictReader(tsv_results, delimiter="\t", quotechar='"')
        return pd.DataFrame(list(reader))


    async def _retrieve_latest_id(self, old_ids, meta):
        start_time = datetime.now()

        if self.__client is None:
            self.__create_client()

        try:
            # divide old_ids into chunks
            num_chunks = len(old_ids) // CHUNK_SIZE
            residual = len(old_ids) % CHUNK_SIZE
            num_chunks += 1 if residual>0 else 0
            chunks = [old_ids[CHUNK_SIZE*i:CHUNK_SIZE*(i+1)] if i<(num_chunks-1) else old_ids[CHUNK_SIZE*i:] for i in range(num_chunks)]
            logger.info(f'{len(old_ids)} ids are divided into {num_chunks} chunks with size {CHUNK_SIZE}')
            logger.info('Communicating with UniProt for id mapping...')

            results_list = await asyncio.gather(*map(self.__retrieve_latest_id_chunk, chunks))

            failed_ids = 0
            no_mapping_ids_set = set()
            retrieved_ids = 0
            results_list_filtered = []
            for i, item in enumerate(results_list): #item may be list df or integer (len(chunk)) if mapping failed
                if isinstance(item, int):
                    failed_ids += item
                else:
                    retrieved_ids += len(item)
                    results_list_filtered.append(item)
                    if len(chunks[i]) > len(item): # there are ids that didn't find mapping data
                        if len(item)>0:
                            no_mapping_ids_set = no_mapping_ids_set.union(set(chunks[i]).difference(set(item.iloc[:, 0])))
                        else: #all ids in this chunk didn't find mapping data
                            no_mapping_ids_set = no_mapping_ids_set.union(set(chunks[i]))

            meta['failed_id_mapping'] = failed_ids
            meta['no_id_mapping'] = no_mapping_ids_set
            logger.info(f'Retrieved {retrieved_ids} ids, {len(no_mapping_ids_set)} ids didn\'t find id mapping data, {failed_ids} ids failed for id mapping')
            logger.info(f'{datetime.now()-start_time} for id mapping')

            return pd.concat(results_list_filtered)
        except Exception:
            raise
        finally:
            if self.__client is not None:
                await self.__client.aclose()
                self.__client = None


    async def __retrieve_latest_id_chunk(self, chunk):
        try:
            job_id = await self.__submit_id_mapping(chunk)
            # if await self.__check_id_mapping_results_ready(job_id):
            #     link = await self.__get_id_mapping_results_link(job_id)
                # print(f'slow link: {link}')
            link = await self.__check_id_mapping_results_ready(job_id)
            results = await self.__get_id_mapping_results_search(link)
            results_df = self.__get_data_frame_from_tsv_results(results)
            if len(results_df)>0:
                results_df.drop(['Entry Name', 'Reviewed'], axis=1, inplace=True)
            logger.debug(f'retrieved: {len(results_df)}')
            # if not self.__save and len(results_df)>0:
            #     results_df = results_df[['From', 'Entry']]
            return results_df
        except Exception as e:
            logger.error(e)
            return len(chunk)


    @abstractmethod
    def get_latest_id(self):
        raise NotImplementedError()


    def __get_uniprot_url(self, type):
        if not self.__cellular_compartment:
            return None

        if type == 'true_positive':
            if self.__save:
                logger.debug(f'using true_positive cache url for {self.__cellular_compartment.get("long_name")}')
                return self.__cellular_compartment.get('true_positive_cache')
            logger.debug(f'using true_positive url for {self.__cellular_compartment.get("long_name")}')
            return self.__cellular_compartment.get('true_positive')
        elif type == 'false_positive':
            if self.__save:
                logger.debug(f'using false_positive cache url for {self.__cellular_compartment.get("long_name")}')
                return self.__cellular_compartment.get('false_positive_cache')
            logger.debug(f'using false_positive url for {self.__cellular_compartment.get("long_name")}')
            return self.__cellular_compartment.get('false_positive')
        else:
            raise Exception('__get_uniprot_url expects a type of either true_positive or false_positive')


    async def __retrieve_annotation_true_positive(self):
        try:
            logger.info('Retrieving annotation_true_positive file from UniProt...')
            url = self.__get_uniprot_url('true_positive')
            results = await self.__get_annotation_results_search(url)
            results = self.__get_data_frame_from_tsv_results(results)
            logger.info(f'Retrieved {len(results)} entries for annotation_true_positive')
            self._annotation_true_positive = results
        except Exception as e:
            logger.error(e)
            logger.info(f'Retrieving annotation_true_positive failed')
            raise


    async def __retrieve_annotation_false_positive(self):
        try:
            logger.info('Retrieving annotation_false_positive file from UniProt...')
            url = self.__get_uniprot_url('false_positive')
            results = await self.__get_annotation_results_search(url)
            results = self.__get_data_frame_from_tsv_results(results)
            logger.info(f'Retrieved {len(results)} entries for annotation_false_positive')
            self._annotation_false_positive = results
        except Exception as e:
            logger.error(e)
            logger.info(f'Retrieving annotation_false_positive failed')
            raise


    async def _retrieve_annotation(self):
        start_time = datetime.now()

        if self.__client is None:
            self.__create_client()
        try:
            await asyncio.gather(self.__retrieve_annotation_true_positive(), self.__retrieve_annotation_false_positive())
            if not self.__save:
                self.__shorten_annotation()
            logger.info(f'{datetime.now()-start_time} for retrieving annotations')
        except Exception:
            raise
        finally:
            if self.__client is not None:
                await self.__client.aclose()
                self.__client = None


    async def get_annotation(self, type):
        if self._annotation_true_positive is None or self._annotation_false_positive is None:
                await self._retrieve_annotation()
        if type=='true_positive':
            return self._annotation_true_positive
        elif type=='false_positive':
            return self._annotation_false_positive


    def __shorten_annotation(self):
        self._annotation_true_positive = self._annotation_true_positive[['Entry']]
        self._annotation_false_positive = self._annotation_false_positive[['Entry']]


    def _set_annotation(self, data, type):
        if type=='true_positive':
            self._annotation_true_positive = data
        elif type=='false_positive':
            self._annotation_false_positive = data
