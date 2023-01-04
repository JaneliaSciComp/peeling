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


    # overriding super class method
    async def _retrieve_latest_id(self, old_ids, meta):
        results_df = await super()._retrieve_latest_id(old_ids, meta)
        if len(results_df)>0:
                results_df = results_df[['From', 'Entry']]
        return results_df


    # overriding abstract method
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
            no_mapping_ids = meta['no_id_mapping']
            no_mapping_ids = pd.DataFrame(list(no_mapping_ids), columns = ['From'])
            for col in retrieved_data.columns[1:]:
                no_mapping_ids[col] = np.NaN
            logger.debug(f'\n{retrieved_data.head()}')
            logger.debug(f'\n{no_mapping_ids.head()}')
            self.__ids = pd.concat([self.__ids, retrieved_data, no_mapping_ids])
            logger.info(f'after retrieve, cached ids: {len(self.__ids)}')
        return self.__ids[self.__ids['From'].isin(old_ids)]


    # overriding super class method
    async def _retrieve_annotation(self):
        await super()._retrieve_annotation()
        super()._shorten_annotation()
 

    async def update_data(self):
        start_time = datetime.now()
        logger.info('Updating data...')
        meta={}
        if self.__ids is not None:
            updated_ids = await self._retrieve_latest_id(list(self.__ids['From']), meta)
            num_diff = len(set(updated_ids['Entry']).difference(set(self.__ids['Entry'])))
            logger.info(f'{num_diff} ids are updated')
            self.__ids = updated_ids
        await self._retrieve_annotation()
        end_time = datetime.now()
        logger.info(f'Update is done. Time: {end_time-start_time}')
