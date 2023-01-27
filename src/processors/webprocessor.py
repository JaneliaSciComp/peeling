#from multiprocessing import parent_process
from processors.processor import Processor
import os
import shutil
import uuid
import logging
import matplotlib.pyplot as plt


logger = logging.getLogger('peeling')


class WebProcessor(Processor):
    def __init__(self, user_input_reader, uniprot_communicator):
        super().__init__(user_input_reader, uniprot_communicator)
        self.__uuid = None
        self.__web_plots_path = None
        self.__failed_id_mapping = 0


    # implement abstract method
    async def _get_id_mapping_data(self, mass_data):
        old_ids = list(mass_data.iloc[:, 0])
        meta={}
        new_ids_df = await self._get_uniprot_communicator().get_latest_id(old_ids, meta)
        if 'failed_id_mapping' in meta.keys(): # false if no id needs mapping
            self.__failed_id_mapping = meta['failed_id_mapping']
        return new_ids_df.copy()


    # implement abstract method
    async def _get_annotation_data(self, type):
        '''
        type: 'surface' or 'cyto'
        '''
        annotation = await self._get_uniprot_communicator().get_annotation(type) 
        #annotation.columns = ['From']
        logger.debug(f'\n{annotation.head()}')
        return annotation.copy()
    

    # implement abstract method
    def _plot_supplemental(self, fig_name): #plt, 
        plt.savefig(f'{self.__web_plots_path}/{fig_name}.png', dpi=130)
        plt.close()
 

    # implement abstract method
    def _construct_path(self):
        unique_id = str(uuid.uuid4())
        self.__uuid = unique_id
        parent_path = os.path.join('../results/', unique_id)
        results_path = os.path.join(parent_path, 'results')
        web_plots_path = os.path.join(parent_path, "web_plots")
        self.__web_plots_path = web_plots_path
        try: 
            os.makedirs(web_plots_path, exist_ok=True) 
        except OSError as error: 
            logger.error(error)
        return results_path
    

    # overriding method of super class
    def _write_args(self, path):
        super()._write_args(path)
        with open(os.path.join(path, 'log.txt'), 'a') as f:
            f.write('Failed id mapping: ' + str(self.__failed_id_mapping) + '\n')

    
    # implement abstract method
    async def start(self):
        data = await self._get_user_input_reader().get_mass_data()
        results_path = self._construct_path()
        await self._analyze(data, results_path)
        self._write_args(results_path)
        logger.info(f'Results saved at {self.__uuid}')
        shutil.make_archive(f'../results/{self.__uuid}/results', 'zip', root_dir=f'../results/{self.__uuid}/results')
        #shutil.rmtree(f'../results/{self.__uuid}/results')
        return  self.__uuid, self.__failed_id_mapping


    

        