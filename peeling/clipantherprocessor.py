import logging
import asyncio
from peeling.pantherprocessor import PantherProcessor

logger = logging.getLogger('peeling')


class CliPantherProcessor(PantherProcessor):
    def __init__(self, organism, path):
        self.__organism = organism
        super().__init__(path)


    def __check_organism(self, organism_dict):
        try:
            assert(self.__organism in organism_dict), 'Organism is not supported by Panther. Please use -h/--help or refer to the Readme file for supported organisms'
        except AssertionError as e:
            logger.error(e)
            raise
    
    
    #implement abstract method
    def _write_args(self): 
        with open(f'{self._get_path()}/log.txt', 'a') as f:
            f.write(f'Panther organism: {self.__organism}\n')

    
    async def _start(self):
        try:
            self._write_args()
            self._create_client()
            organism_dict = await self._retrieve_organisms()
            self.__check_organism(organism_dict)
            organism_id = organism_dict[self.__organism]
            self._set_organism_id(organism_id)
            await self._run_enrichment()  
        except Exception:
            raise
        finally:
            await self._close_client()


    # implement abstract method
    def start(self):
        asyncio.run(self._start())
