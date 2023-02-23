from datamanagement.uniprotcommunicator import UniProtCommunicator
import pandas as pd
import numpy as np
from datetime import datetime
import logging
import asyncio

logger = logging.getLogger('peeling')


class WebUniProtCommunicator(UniProtCommunicator):
    def __init__(self, cache=False):
        super().__init__(cache)
        self.__ids = None
        self.__track_update = 0


    # overriding super class method
    # async def _retrieve_latest_id(self, old_ids, meta):
    #     results_df = await super()._retrieve_latest_id(old_ids, meta)
    #     if len(results_df)>0:
    #             results_df = results_df[['From', 'Entry']]
    #     return results_df


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
            # add ids that didn't find mapping data to cached ids, all fields are NaN
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


    # overriding super class method
    # async def _retrieve_annotation(self):
    #     await super()._retrieve_annotation()
    #     super()._shorten_annotation()
 

    async def __initialize(self):
        start_time = datetime.now()
        logger.info('Initializing ...')
        try:
            annotation_surface = pd.read_table('../retrieved_data/annotation_surface.tsv', sep='\t', header=0)
            logger.info(f'Read in {len(annotation_surface)} entries from archived annotation_surface file')
            self._set_annotation(annotation_surface, 'surface')
            annotation_cyto = pd.read_table('../retrieved_data/annotation_cyto.tsv', sep='\t', header=0)
            logger.info(f'Read in {len(annotation_cyto)} entries from archived annotation_cyto file')
            self._set_annotation(annotation_cyto, 'cyto')
        except Exception as e:
            logger.info(e)
            await self._retrieve_annotation()
            surface = await self.get_annotation('surface')
            surface.to_csv('../retrieved_data/annotation_surface.tsv', sep='\t', index=False)
            cyto = await self.get_annotation('cyto')
            cyto.to_csv('../retrieved_data/annotation_cyto.tsv', sep='\t', index=False)
            logger.info(f'Annotation files saved')
        
        try:
            self.__ids = pd.read_table('../retrieved_data/latest_ids.tsv', sep='\t', header=0)
            logger.info(f'Read in {len(self.__ids)} entries from archived latest_ids file')
        except Exception as e:
            logger.info(e)
        end_time = datetime.now()
        logger.info(f'Initialization is done. Time: {end_time-start_time}')


    async def update_data(self):
        start_time = datetime.now()
        if self.__track_update == 0:
            await self.__initialize()
            self.__track_update += 1
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
                surface = await self.get_annotation('surface')
                surface.to_csv('../retrieved_data/annotation_surface.tsv', sep='\t', index=False)
                cyto = await self.get_annotation('cyto')
                cyto.to_csv('../retrieved_data/annotation_cyto.tsv', sep='\t', index=False)
                logger.info(f'Annotation files saved')
                end_time = datetime.now()
                logger.info(f'Update is done. Time: {end_time-start_time}')
                self.__track_update += 1
            except Exception as e:
                logger.error(e)
                raise
        
    
    # called in main.py, to export cached ids by api instead of waiting for update
    def get_ids(self):
        return self.__ids