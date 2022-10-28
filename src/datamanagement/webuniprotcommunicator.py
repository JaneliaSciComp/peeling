from datamanagement.uniprotcommunicator import UniProtCommunicator
import pandas as pd
from datetime import datetime

class WebUniProtCommunicator(UniProtCommunicator):
    def __init__(self, cache=False):
        super().__init__(cache)
        self.__ids = None
        self.__annotation_surface = None
        self.__annotation_cyto = None


    # overriding super class method
    def _retrieve_latest_id(self, old_ids):
        results_df = super()._retrieve_latest_id(old_ids)
        if len(results_df)>0:
                results_df = results_df[['From', 'Entry']]
        return results_df


    # overriding abstract method
    def get_latest_id(self, old_ids=None):
        if old_ids is not None: #for merge ids
            if self.__ids is None:
                self.__ids = self._retrieve_latest_id(old_ids)
                return self.__ids
            else:
                old_ids_set = set(old_ids)
                saved_ids_set = set(self.__ids['From'])
                print('before retrieve: ', len(self.__ids))
                to_retrieve = old_ids_set.difference(saved_ids_set)
                print('to retrieve: ', len(to_retrieve), to_retrieve)
                
                if len(to_retrieve) > 0:
                    retrieved_data = self._retrieve_latest_id(list(to_retrieve))
                    self.__ids = pd.concat([self.__ids, retrieved_data])
                print('after concat: ', len(self.__ids))
            return self.__ids[self.__ids['From'].isin(old_ids)]
        else: #for merge annotation
            return self.__ids


    # overriding super class method
    def _retrieve_annotation_surface(self):
        #TODO
        results = super()._retrieve_annotation_surface()
        self.__annotation_surface = results
        # self.__annotation_surface = pd.read_table('../retrieved_data/annotation_surface.tsv', sep='\t')
        # self.__annotation_surface = self.__annotation_surface[['Entry']]
    

    # overriding super class method
    def _retrieve_annotation_cyto(self):
        #TODO
        results = super()._retrieve_annotation_cyto()
        self.__annotation_cyto = results
        # self.__annotation_cyto = pd.read_table('../retrieved_data/annotation_cyto.tsv', sep='\t')
        # self.__annotation_cyto = self.__annotation_cyto[['Entry']]


    # overriding abstract method
    def get_annotation_surface(self):
        return self.__annotation_surface
    

    # overriding abstract method
    def get_annotation_cyto(self):
        return self.__annotation_cyto
    

    def update_data(self):
        start_time = datetime.now()
        print('Updating data. ', start_time)
        if self.__ids is not None:
            updated_ids = self._retrieve_latest_id(list(self.__ids['From']))
            num_diff = len(set(updated_ids['Entry']).difference(set(self.__ids['Entry'])))
            print(f'{num_diff} ids are updated')
            self.__ids = updated_ids
        self._retrieve_annotation_surface()
        self._retrieve_annotation_cyto()
        end_time = datetime.now()
        print('Update is done.', end_time-start_time)
