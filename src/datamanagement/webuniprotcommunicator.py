from datamanagement.uniprotcommunicator import UniProtCommunicator
import pandas as pd
from datetime import datetime
import logging
import asyncio

logger = logging.getLogger('peeling')


class WebUniProtCommunicator(UniProtCommunicator):
    def __init__(self, cache=False):
        super().__init__(cache)
        self.__ids = None


    # overriding super class method
    async def _retrieve_latest_id(self, old_ids):
        results_df = await super()._retrieve_latest_id(old_ids)
        if len(results_df)>0:
                results_df = results_df[['From', 'Entry']]
        return results_df


    # overriding abstract method
    async def get_latest_id(self, old_ids=None):
        if old_ids is not None: #for merge ids
            if self.__ids is None:
                self.__ids = await self._retrieve_latest_id(old_ids)
                return self.__ids
            else:
                old_ids_set = set(old_ids)
                saved_ids_set = set(self.__ids['From'])
                logger.info(f'before retrieve: {len(self.__ids)}')
                to_retrieve = old_ids_set.difference(saved_ids_set)
                logger.info(f'to retrieve: {len(to_retrieve)}')
                
                if len(to_retrieve) > 0:
                    retrieved_data = await self._retrieve_latest_id(list(to_retrieve))
                    self.__ids = pd.concat([self.__ids, retrieved_data])
                logger.debug(f'after retrieve: {len(self.__ids)}')
            return self.__ids[self.__ids['From'].isin(old_ids)]
        else: #for merge annotation
            return self.__ids


    # overriding super class method
    async def _retrieve_annotation(self):
        await super()._retrieve_annotation()
        super()._shorten_annotation()
 

    async def update_data(self):
        start_time = datetime.now()
        logger.info('Updating data...')
        if self.__ids is not None:
            updated_ids = await self._retrieve_latest_id(list(self.__ids['From']))
            num_diff = len(set(updated_ids['Entry']).difference(set(self.__ids['Entry'])))
            logger.info(f'{num_diff} ids are updated')
            self.__ids = updated_ids
        await self._retrieve_annotation()
        end_time = datetime.now()
        logger.info(f'Update is done. Time: {end_time-start_time}')
