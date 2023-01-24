from processors.pantherprocessor import PantherProcessor
import logging
import os

logger = logging.getLogger('peeling')


class WebPantherProcessor(PantherProcessor):
    # overide superclass method
    def __init__(self, organism_id, unique_id):
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

    
    # implement abstract method
    async def start(self):
        try:
            self._create_client()
            await self._run_enrichment()
        except Exception:
            raise
        finally:
            await self._close_client()

