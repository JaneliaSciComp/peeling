from processors.pantherprocessor import PantherProcessor
import logging
import os

logger = logging.getLogger('peeling')


class WebPantherProcessor(PantherProcessor):
    # overide superclass method
    def __init__(self, organism_id, unique_id):
        if unique_id is not None and organism_id is not None:
            path = '../results/' + unique_id + '/results'
            super().__init__(path)
            self._set_organism_id(organism_id)


    async def retrieve_organisms(self):
        try:
            self._create_client()
            organism_dict = await super()._retrieve_organisms()
            return organism_dict
        except Exception:
            raise
        finally:
            await self._close_client()


    def __reformat_enrich(self, results_dict):
        results_dict_reformat = {}
        for category, df in results_dict.items():
            results_dict_reformat[category] = dict(zip(df['Term'], df['FDR']))
        return results_dict_reformat


    #implement abstract method
    def __write_args(self): 
        with open(f'{self._get_path()}/log.txt', 'w') as f:
            f.write(f'Panther organism: {self._get_organism_id()}\n')

    
    # implement abstract method
    async def start(self):
        try:
            self.__write_args()
            self._create_client()
            results_dict = await self._run_enrichment()
            results_dict = self.__reformat_enrich(results_dict)
            return results_dict
        except Exception:
            raise
        finally:
            await self._close_client()

