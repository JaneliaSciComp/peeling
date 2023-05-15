import os
from datetime import datetime
import pandas as pd
import logging
import asyncio
import matplotlib.pyplot as plt
from peeling.processor import Processor


logger = logging.getLogger('peeling')


class CliProcessor(Processor):
    def __init__(self, user_input_reader, uniprot_communicator):
        super().__init__(user_input_reader, uniprot_communicator)
        self.__ids = None
        self.__path = None


    # implement abstract method
    async def _get_id_mapping_data(self, mass_data):
        if self._get_user_input_reader().get_latest_ids_filename() is not None:
            # read in local ids file
            self.__ids = self._get_user_input_reader().get_latest_ids()
            #self.__ids = self.__ids.iloc[:, :2] # the first two columns should be old ids and new ids
            self.__ids.columns = ['From', 'Entry'] + list(self.__ids.columns[2:])
        else:
            # get latest ids by communicating with UniProt
            old_ids = list(mass_data.iloc[:, 0])
            if self.__ids is not None: # for annotation ids
                old_ids_set = set(old_ids)
                saved_ids_set = set(self.__ids['From'])
                # logger.debug(f'before retrieve: {len(self.__ids)}')
                to_retrieve = old_ids_set.difference(saved_ids_set)
                # logger.debug(f'to retrieve: {len(to_retrieve)}')

                if len(to_retrieve) > 0:
                    old_ids = list(to_retrieve)
            retrieved_data = await self._get_uniprot_communicator().get_latest_id(old_ids)
            self.__ids = pd.concat([self.__ids, retrieved_data])
            # logger.debug(f'after concat: {len(self.__ids)}')

        return self.__ids


    # implement abstract method
    async def _get_annotation_data(self, type):
        '''
        type: 'true_positive' or 'false_positive'
        '''
        if type == 'true_positive':
            if self._get_user_input_reader().get_true_positive_filename() is not None:
                annotation = self._get_user_input_reader().get_annotation_true_positive()
                annotation = pd.DataFrame(annotation.iloc[:, 0])
                if not self._get_user_input_reader().get_id_mapping():
                    annotation.columns = ['From']
                    id_mapping_data = await self._get_id_mapping_data(annotation)
                    annotation = self._merge_id(annotation, id_mapping_data)
                    annotation.reset_index(inplace=True)
                    annotation = pd.DataFrame(annotation.iloc[:, 0])
                annotation.columns = ['Entry']
            else: # retrieve annotation file from UniProt
                annotation = await self._get_uniprot_communicator().get_annotation('true_positive')
                annotation.dropna(subset=['Entry'], axis=0, how='any', inplace=True)
                if self._get_user_input_reader().get_save():
                    annotation.to_csv(f'{self.__path}/annotation_true_positive.tsv', sep='\t', index=False)
                annotation = annotation[['Entry']]
        else:
            if self._get_user_input_reader().get_false_positive_filename() is not None:
                annotation = self._get_user_input_reader().get_annotation_false_positive()
                annotation = pd.DataFrame(annotation.iloc[:, 0])
                if not self._get_user_input_reader().get_id_mapping():
                    annotation.columns = ['From']
                    id_mapping_data = await self._get_id_mapping_data(annotation)
                    annotation = self._merge_id(annotation, id_mapping_data)
                    annotation.reset_index(inplace=True)
                    annotation = pd.DataFrame(annotation.iloc[:, 0])
                annotation.columns = ['Entry']
            else: # retrieve annotation file from UniProt
                annotation = await self._get_uniprot_communicator().get_annotation('false_positive')
                annotation.dropna(subset=['Entry'], axis=0, how='any', inplace=True)
                if self._get_user_input_reader().get_save():
                    annotation.to_csv(f'{self.__path}/annotation_false_positive.tsv', sep='\t', index=False)
                annotation = annotation[['Entry']]

        return annotation


    # implement abstract method
    def _plot_supplemental(self, fig_name):
        plt.close()


    # implement abstract method
    def _construct_path(self):
        parent_path = os.path.join(self._get_user_input_reader().get_output_directory(), str(datetime.now()).replace(':','-').replace(' ','_'))
        if self._get_user_input_reader().get_save():
            retrieved_path = os.path.join(parent_path, "retrieved_data")
            try:
                os.makedirs(retrieved_path, exist_ok=True)
            except OSError as error:
                logger.error(error)
        else:
            retrieved_path = None
        self.__path = retrieved_path
        return parent_path


    def _write_args(self, path):
        super()._write_args(path)
        with open(os.path.join(path, 'log.txt'), 'a') as f:
            ids = self._get_user_input_reader().get_latest_ids_filename()
            if ids is not None:
                f.write(f'Latest_ids file: {ids}\n')

            true_positive = self._get_user_input_reader().get_true_positive_filename()
            if true_positive is not None:
                f.write(f'Annotation_true_positive file: {true_positive}\n')

            false_positive = self._get_user_input_reader().get_false_positive_filename()
            if false_positive is not None:
                f.write(f'Annotation_false_positive file: {false_positive}\n')

            no_id_mapping = self._get_user_input_reader().get_id_mapping()
            if (true_positive is not None) or (false_positive is not None):
                f.write(f'No id mapping for local annotations: {no_id_mapping}\n')


    # implement abstract method
    def start(self):
        data = self._get_user_input_reader().get_mass_data()
        parent_path = self._construct_path()
        data = self._mass_data_clean(data)
        asyncio.run(self._analyze(data, parent_path))
        if self._get_user_input_reader().get_save() and self._get_user_input_reader().get_latest_ids_filename() is None:
            self.__ids.to_csv(self.__path+'/latest_ids.tsv', sep='\t', index=False)
        self._write_args(parent_path)
        return parent_path


    def _set_true_positive_proteins_raw_data(self, df):
        return
