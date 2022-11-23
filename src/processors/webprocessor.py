#from multiprocessing import parent_process
from processors.processor import Processor
import os
import shutil
import uuid
import logging

logger = logging.getLogger('peeling')


class WebProcessor(Processor):
    def __init__(self, user_input_reader, uniprot_communicator):
        super().__init__(user_input_reader, uniprot_communicator)
        self.__uuid = None


    # overriding abstract method
    def _get_id_mapping_data(self, mass_data):
        old_ids = list(mass_data.iloc[:, 0])
        new_ids_df = self._get_uniprot_communicator().get_latest_id(old_ids).copy() 
        return new_ids_df


    # overriding abstract method
    def _get_id_mapping_data_annotation(self):
        return self._get_uniprot_communicator().get_latest_id().copy()


    # overriding abstract method
    def _get_annotation_data(self, type):
        '''
        type: 'surface' or 'cyto'
        '''
        annotation = self._get_uniprot_communicator().get_annotation_surface().copy() if type == 'surface' else self._get_uniprot_communicator().get_annotation_cyto().copy() 
        annotation.columns = ['From']
        return annotation
 

    # overriding super class method
    def _construct_path(self):
        unique_id = str(uuid.uuid4())
        self.__uuid = unique_id
        parent_path = os.path.join('../results/', unique_id)
        return parent_path

    
    # overriding super class method
    async def start(self):
        data = await self._get_user_input_reader().get_mass_data()
        parent_path = self._construct_path()
        self._analyze(data, parent_path)
        self._write_args(parent_path)
        logger.info(f'Results saved at {parent_path}')
        shutil.make_archive(f'../results/{self.__uuid}', 'tar', root_dir=f'../results/{self.__uuid}')
        #shutil.rmtree(f'../results/{self.__uuid}')
        return  self.__uuid


    

        