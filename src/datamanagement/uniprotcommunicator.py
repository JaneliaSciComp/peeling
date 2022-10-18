import re
import time
import zlib
from urllib.parse import urlparse, parse_qs, urlencode
import requests
from requests.adapters import HTTPAdapter, Retry
import csv
import pandas as pd


POLLING_INTERVAL = 3
API_URL = "https://rest.uniprot.org"
SURFACE_URL = "https://rest.uniprot.org/uniprotkb/search?compressed=true&fields=accession%2Creviewed%2Cid%2Cgene_names%2Corganism_name%2Ccc_subcellular_location&format=tsv&query=%28%28%28cc_scl_term%3ASL-0112%29%20OR%20%28cc_scl_term%3ASL-0243%29%20OR%20%28keyword%3AKW-0732%29%20OR%20%28cc_scl_term%3ASL-9906%29%20OR%20%28cc_scl_term%3ASL-9907%29%29%20AND%20%28reviewed%3Atrue%29%29&size=500"
CYTO_URL = "https://rest.uniprot.org/uniprotkb/search?compressed=true&fields=accession%2Creviewed%2Cid%2Cgene_names%2Corganism_name%2Ccc_subcellular_location&format=tsv&query=%28%28%28%28cc_scl_term%3ASL-0091%29%20OR%20%28cc_scl_term%3ASL-0173%29%20OR%20%28cc_scl_term%3ASL-0191%29%29%20AND%20%28reviewed%3Atrue%29%29%20NOT%20%28%28%28cc_scl_term%3ASL-0112%29%20OR%20%28cc_scl_term%3ASL-0243%29%20OR%20%28keyword%3AKW-0732%29%20OR%20%28cc_scl_term%3ASL-9906%29%20OR%20%28cc_scl_term%3ASL-9907%29%29%20AND%20%28reviewed%3Atrue%29%29%29&size=500"
# SURFACE_URL = "https://rest.uniprot.org/uniprotkb/search?compressed=true&fields=accession&format=tsv&query=%28%28%28cc_scl_term%3ASL-0112%29%20OR%20%28cc_scl_term%3ASL-0243%29%20OR%20%28keyword%3AKW-0732%29%20OR%20%28cc_scl_term%3ASL-9906%29%20OR%20%28cc_scl_term%3ASL-9907%29%29%20AND%20%28reviewed%3Atrue%29%29&size=500"
# CYTO_URL = "https://rest.uniprot.org/uniprotkb/search?compressed=true&fields=accession&format=tsv&query=%28%28%28%28cc_scl_term%3ASL-0091%29%20OR%20%28cc_scl_term%3ASL-0173%29%20OR%20%28cc_scl_term%3ASL-0191%29%29%20AND%20%28reviewed%3Atrue%29%29%20NOT%20%28%28%28cc_scl_term%3ASL-0112%29%20OR%20%28cc_scl_term%3ASL-0243%29%20OR%20%28keyword%3AKW-0732%29%20OR%20%28cc_scl_term%3ASL-9906%29%20OR%20%28cc_scl_term%3ASL-9907%29%29%20AND%20%28reviewed%3Atrue%29%29%29&size=500"


class UniProtCommunicator():
    def __init__(self) -> None:
        retries = Retry(total=5, backoff_factor=0.25, status_forcelist=[500, 502, 503, 504])
        self.__session = requests.Session()
        self.__session.mount("https://", HTTPAdapter(max_retries=retries))
    

    def _check_response(self, response):
        try:
            response.raise_for_status()
        except requests.HTTPError:
            print(response.json())
            raise


    def _submit_id_mapping(self, ids):
        response = requests.post(
            f"{API_URL}/idmapping/run",
            data={"from": 'UniProtKB_AC-ID', "to": 'UniProtKB', "ids": ",".join(ids)},
        )
        self._check_response(response) 
        return response.json()["jobId"]


    def _get_next_link(self, headers):
        re_next_link = re.compile(r'<(.+)>; rel="next"')
        if "Link" in headers:
            match = re_next_link.match(headers["Link"])
            if match:
                return match.group(1)


    def _check_id_mapping_results_ready(self, job_id):
        while True:
            response = self.__session.get(f"{API_URL}/idmapping/status/{job_id}")
            self._check_response(response)
            j = response.json() 
            if "jobStatus" in j:
                if j["jobStatus"] == "RUNNING":
                    print(f"Retrying in {POLLING_INTERVAL}s")
                    time.sleep(POLLING_INTERVAL)
                else:
                    raise Exception(response["jobStatus"])
            else:
                return bool(j["results"] or j["failedIds"]) #bool()return false if aug is 0,empty,None,false, otherwise true


    def _get_batch(self, batch_response, file_format, compressed):
        batch_url = self._get_next_link(batch_response.headers) # this step is repeated until there is no batch_url
        while batch_url:
            batch_response = self.__session.get(batch_url)
            self._check_response(batch_response) #batch_response.raise_for_status()
            yield self._decode_results(batch_response, file_format, compressed) #yield is similar to return, but next time the func is called, it will start from here, usually this func will be called in a loop
            batch_url = self._get_next_link(batch_response.headers) # repeats


    def _combine_batches(self, all_results, batch_results, file_format):
        return all_results + batch_results[1:]


    def _get_id_mapping_results_link(self, job_id):
        url = f"{API_URL}/idmapping/details/{job_id}"
        response = self.__session.get(url)
        self._check_response(response) 
        return response.json()["redirectURL"]


    def _decode_results(self, response, file_format, compressed):
        if compressed:
            decompressed = zlib.decompress(response.content, 16 + zlib.MAX_WBITS)
            return [line for line in decompressed.decode("utf-8").split("\n") if line]
        else:
            return [line for line in response.text.split("\n") if line]



    def _get_id_mapping_results_search(self, url):
        parsed = urlparse(url) 
        query = parse_qs(parsed.query)
        file_format = "tsv" 
        query['format'] = file_format
        size = 500 
        query["size"] = size
        compressed = True
        query['compressed'] = compressed
        #query['fields'] = 'accession'  # may be good for the web version, the response data will be less 
        parsed = parsed._replace(query=urlencode(query, doseq=True))
        url = parsed.geturl()
        #print(url)
        response = self.__session.get(url)
        self._check_response(response)
        results = self._decode_results(response, file_format, compressed)
        for i, batch in enumerate(self._get_batch(response, file_format, compressed), 1):
            results = self._combine_batches(results, batch, file_format)
        return results
    

    def _get_annotation_results_search(self, url):
        response = self.__session.get(url)
        self._check_response(response)
        results = self._decode_results(response, 'tsv', True)
        for i, batch in enumerate(self._get_batch(response, 'tsv', True), 1):
            results = self._combine_batches(results, batch, 'tsv')
        return results


    def _get_data_frame_from_tsv_results(self, tsv_results):
        reader = csv.DictReader(tsv_results, delimiter="\t", quotechar='"')
        return pd.DataFrame(list(reader))


    def get_latest_id(self, old_ids):
        print('Communicating with UniProt for id mapping...') #To do
        job_id = self._submit_id_mapping(old_ids)
        if self._check_id_mapping_results_ready(job_id):
            link = self._get_id_mapping_results_link(job_id)
        results = self._get_id_mapping_results_search(link)
        results_df = self._get_data_frame_from_tsv_results(results)
        return results_df

    
    def get_annotation_surface(self):
        print('Retrieving annotation_surface file from UniProt...') #To do
        results = self._get_annotation_results_search(SURFACE_URL)
        results_df = self._get_data_frame_from_tsv_results(results)
        return results_df


    def get_annotation_cyto(self):
        print('Retrieving annotation_cyto file from UniProt...') #To do
        results = self._get_annotation_results_search(CYTO_URL)
        results_df = self._get_data_frame_from_tsv_results(results)
        return results_df