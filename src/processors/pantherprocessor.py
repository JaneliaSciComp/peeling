from abc import ABC, abstractmethod
import logging
from datetime import datetime
import httpx
import asyncio
from urllib.parse import urlparse, parse_qs, urlencode
import pandas as pd

logger = logging.getLogger('peeling')

CONNECT_RETRY=5
API_RETRY = 3
TIME_OUT = None

#corresponding to "PANTHER GO Slim Cellular Location", "PANTHER GO Slim Biological Process", "ANNOT_TYPE_REACTOME_PATHWAY"
ENRICH_CATEGORIES = {'ANNOT_TYPE_ID_PANTHER_GO_SLIM_CC':'Panther_GO_Slim_Cellular_Componet', 'ANNOT_TYPE_ID_PANTHER_GO_SLIM_BP':'Panther_GO_Slim_Biological_Process', "ANNOT_TYPE_ID_REACTOME_PATHWAY":'Reactom_Pathway'}


class PantherProcessor(ABC):
    def __init__(self, path):
        self.__path = path
        self.__client = None
        self.__proteins = None
        self.__organism_id = None
    

    def _create_client(self):
        transport = httpx.AsyncHTTPTransport(retries=CONNECT_RETRY)
        self.__client = httpx.AsyncClient(http2=True, timeout=TIME_OUT, transport=transport, event_hooks={'response': [self.__check_response]})

        
    async def __check_response(self, response):
        try:
            await response.aread()
            response.raise_for_status()
        except httpx.HTTPStatusError:
            logger.info(response.json())
            raise
    

    def __make_url_enrich(self, annot_dataset):
        base_url = "http://pantherdb.org/services/oai/pantherdb/enrich/overrep?"
        parsed = urlparse(base_url) 
        query = parse_qs(parsed.query)
        query['geneInputList'] = self.__proteins
        query['organism'] = self.__organism_id
        query['annotDataSet'] = annot_dataset
        query['enrichmentTestType'] = 'FISHER'
        query['correction'] = 'FDR'
        parsed = parsed._replace(query=urlencode(query, doseq=True))
        url = parsed.geturl()
        #print(url[:100])
        return url
    

    async def __submit(self, url):
        retry = 0
        while retry < API_RETRY:
            retry += 1
            try:
                response = await self.__client.get(url)
                return response
            except Exception as e:
                logger.error(e)
        raise Exception('Reached maximal Panther API trail')
    

    def __format_enrich(self, response):
        try:
            results_json = response.json()['results']['result']
            df = pd.json_normalize(results_json)
            logger.debug(df.head())
            
            logger.debug(len(df))
            df = df[df['plus_minus'] == '+']
            logger.debug(len(df))
            df = df.sort_values(by=['fdr'])
            
            df.rename(columns={'term.label': 'Term', 'fdr':'FDR'}, inplace=True)
            df = df[['Term', 'FDR']]
            df = df.iloc[:10, :]
            return df
        except Exception as e:
            logger.error(e)
            raise
    

    def __get_proteins(self):
        try:
            with open(f'{self.__path}/post-cutoff-proteome.txt', 'r') as f:
                proteins = f.readline()
            #print(proteins[:20])
            return proteins
        except Exception as e:
            logger.error(e)
            raise


    async def _retrieve_organisms(self):
        start_time = datetime.now()
        logger.debug('Communicating with Panther for supported organisms ...')
        try:
            url = 'http://pantherdb.org/services/oai/pantherdb/supportedgenomes'
            response = await self.__submit(url)
            organism_dict = self.__format_organism(response)
            logger.info(f'Retriving organisms is done. Time: {datetime.now()-start_time}')
            return organism_dict
        except Exception:
            raise
    

    def __format_organism(self, response):
        try:
            results_json = response.json()['search']['output']['genomes']['genome']
            df = pd.json_normalize(results_json)
            df = df[['long_name', 'taxon_id']]
            org_dict = dict(zip(df['long_name'], df['taxon_id']))
            return org_dict
        except Exception as e:
            logger.error(e)
            raise

    
    async def _run_enrichment(self):
        start_time = datetime.now()
        try:
            self.__proteins = self.__get_proteins()
            results_tuples = await asyncio.gather(*map(self.__run_enrichment_each, ENRICH_CATEGORIES.keys()))
            results_dict = dict(results_tuples)
            logger.info(f'Panther enrichment is done. Time: {datetime.now()-start_time}')
            return results_dict
        except Exception:
            raise


    async def __run_enrichment_each(self, annot_dataset):
        start_time = datetime.now()
        logger.info(f'Communicating with Panther for {annot_dataset}...')
        try:
            url = self.__make_url_enrich(annot_dataset)
            response = await self.__submit(url)
            results_df = self.__format_enrich(response)
            results_df.to_csv(f'{self.__path}/post-cutoff-proteome_{ENRICH_CATEGORIES[annot_dataset]}.tsv', sep='\t', index=False)
            logger.info(f'{annot_dataset} is done. Time: {datetime.now()-start_time}')
            return (annot_dataset, results_df)
        except Exception as e:
            logger.error(f'{annot_dataset} failed.')
            logger.error(e)
            return (annot_dataset, 'failed')


    @abstractmethod
    def start(self):
        raise NotImplemented()
    

    def _set_organism_id(self, id):
        self.__organism_id = id
    

    async def _close_client(self):
        await self.__client.aclose()