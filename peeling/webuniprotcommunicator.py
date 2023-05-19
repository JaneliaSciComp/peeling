import pandas as pd
import numpy as np
from datetime import datetime
import logging
import os
from peeling.uniprotcommunicator import UniProtCommunicator

logger = logging.getLogger('peeling')


class WebUniProtCommunicator(UniProtCommunicator):
    def __init__(self, cache, cellular_compartment, tp_data=None, fp_data=None):
        super().__init__(cache, cellular_compartment)
        self.__ids = None
        self.__track_update = 0
        if isinstance(tp_data, pd.DataFrame) and isinstance(fp_data, pd.DataFrame):
            self._annotation_true_positive = tp_data
            self._annotation_false_positive = fp_data
        else:
            self.__init_annotations()


    # implement abstract method
    async def get_latest_id(self, old_ids, meta):
        if self.__ids is None:
            to_retrieve = old_ids
            logger.info('before retrieve, cached ids: 0')

        else:
            old_ids_set = set(old_ids)
            saved_ids_set = set(self.__ids['From'])
            to_retrieve = old_ids_set.difference(saved_ids_set)
            logger.info(f'before retrieve, cached ids: {len(self.__ids)}')

        logger.info(f'to retrieve: {len(to_retrieve)}')
        if len(to_retrieve) > 0:
            retrieved_data = await self._retrieve_latest_id(list(to_retrieve), meta)
            retrieved_data = self.__add_no_mapping_ids(retrieved_data, meta)
            logger.debug(f'\n{retrieved_data.head()}')

            self.__ids = pd.concat([self.__ids, retrieved_data])
            logger.info(f'after retrieve, cached ids: {len(self.__ids)}')
        return self.__ids[self.__ids['From'].isin(old_ids)]


    def __add_no_mapping_ids(self, retrieved_data, meta):
        # add ids that didn't find mapping data to cached ids, all fields are NaN
        no_mapping_ids = meta['no_id_mapping']
        if len(no_mapping_ids) > 0:
            no_mapping_ids = pd.DataFrame(list(no_mapping_ids), columns = ['From'])
            for col in retrieved_data.columns[1:]:
                no_mapping_ids[col] = np.NaN
            retrieved_data = pd.concat([retrieved_data, no_mapping_ids])
            logger.debug(f'\n{no_mapping_ids.head()}')
        return retrieved_data


    def __init_annotations(self):
        annotation_types = ['true_positive', 'false_positive']
        for annotation_type in annotation_types:
            annotation_path = f'../retrieved_data/{self._cc_code}_annotation_{annotation_type}.tsv'
            if os.path.exists(annotation_path):
                annotation_data = pd.read_table(annotation_path, sep='\t', header=0)
                logger.info(f'Read in {len(annotation_data)} entries from cached {self._cc_code}_annotation_{annotation_type} file')
                self._set_annotation(annotation_data, annotation_type)
            else:
                logger.debug(f"*** didn't find cache in {annotation_path}")


    async def __initialize(self):
        start_time = datetime.now()
        logger.info('Initializing ...')
        annotation_types = ['true_positive', 'false_positive']
        try:
            has_data = True
            for annotation_type in annotation_types:
                annotation_path = f'../retrieved_data/{self._cc_code}_annotation_{annotation_type}.tsv'
                if os.path.exists(annotation_path):
                    annotation_data = pd.read_table(annotation_path, sep='\t', header=0)
                    logger.info(f'Read in {len(annotation_data)} entries from cached {self._cc_code}_annotation_{annotation_type} file')
                    self._set_annotation(annotation_data, annotation_type)
                else:
                    logger.debug(f"*** didn't find cache in {annotation_path}")
                    has_data = False

            if not has_data:
                await self._retrieve_annotation()
                for annotation_type in annotation_types:
                    annotation_data = await self.get_annotation(annotation_type)
                    annotation_data.to_csv(f'../retrieved_data/{self._cc_code}_annotation_{annotation_type}.tsv', sep='\t', index=False)
                logger.info(f'Annotation files saved')

            id_path = '../retrieved_data/latest_ids.tsv'
            if os.path.exists(id_path):
                self.__ids = pd.read_table(id_path, sep='\t', header=0)
                logger.info(f'Read in {len(self.__ids)} entries from archived latest_ids file')

            end_time = datetime.now()
            logger.info(f'Initialization is done. Time: {end_time-start_time}')

        except Exception as e:
            logger.error('Initialization failed')
            logger.info(e)
            raise



    async def update_data(self):
        start_time = datetime.now()
        if self.__track_update == 0:
            try:
                await self.__initialize()
                self.__track_update += 1
            except Exception as e:
                logger.error(e)
        else:
            logger.info('Updating data...')
            try:
                meta={}
                if self.__ids is not None:
                    updated_ids = await self._retrieve_latest_id(list(self.__ids['From']), meta)
                    updated_ids = self.__add_no_mapping_ids(updated_ids, meta)
                    num_diff = len(set(updated_ids['Entry']).difference(set(self.__ids['Entry'])))
                    logger.info(f'{num_diff} ids are updated')
                    self.__ids = updated_ids
                    self.__ids.to_csv('../retrieved_data/latest_ids.tsv', sep='\t', index=False)
                    logger.info('Latest_ids file saved')
                await self._retrieve_annotation()
                true_positive = await self.get_annotation('true_positive')
                true_positive.to_csv(f'../retrieved_data/{self._cc_code}_annotation_true_positive.tsv', sep='\t', index=False)
                false_positive = await self.get_annotation('false_positive')
                false_positive.to_csv(f'../retrieved_data/{self._cc_code}_annotation_false_positive.tsv', sep='\t', index=False)
                logger.info(f'Annotation files saved')
                end_time = datetime.now()
                logger.info(f'Update is done. Time: {end_time-start_time}')
                self.__track_update += 1
            except Exception as e:
                logger.error(e)


    # called in main.py, to export cached ids by api instead of waiting for update
    def get_ids(self):
        return self.__ids
