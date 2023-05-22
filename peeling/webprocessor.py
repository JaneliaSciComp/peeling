import os
#import shutil
import uuid
import logging
import matplotlib.pyplot as plt
import pandas as pd
from peeling.processor import Processor


logger = logging.getLogger('peeling')


class WebProcessor(Processor):
    def __init__(self, *args):
        if len(args) == 2:
            user_input_reader, uniprot_communicator = args
            super().__init__(user_input_reader, uniprot_communicator)
            self.__uuid = None
            self.__web_plots_path = None
            self.__failed_id_mapping = 0
            self.__true_positive_proteins_raw_data = None
        elif len(args) == 3:
            unique_id, x, y = args
            self.__uuid = unique_id
            self.__x = x
            self.__y = y
        elif len(args) == 1:
            self.__uuid = args[0]


    #override superclass method
    def _mass_data_clean(self, data):
        data = super()._mass_data_clean(data)
        data.to_csv(f'../results/{self.__uuid}/mass_spec_data.tsv', sep='\t', index=False)
        return data


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
        type: 'true_positive' or 'false_positive'
        '''
        annotation = await self._get_uniprot_communicator().get_annotation(type)
        # logger.debug(f'\n{annotation.head()}')
        return annotation.copy()


    # implement abstract method
    def _plot_supplemental(self, fig_name): #plt,
        plt.savefig(f'{self.__web_plots_path}/{fig_name}.jpeg', dpi=130, bbox_inches='tight')
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
        data = self._mass_data_clean(data)
        columns = list(data.columns[1:])
        await self._analyze(data, results_path)
        self.__true_positive_proteins_raw_data.to_csv(f'../results/{self.__uuid}/post-cutoff-proteome_with_raw_data.tsv', sep='\t', index=False)
        self._write_args(results_path)
        logger.info(f'Results saved at {self.__uuid}')
        #shutil.make_archive(f'../results/{self.__uuid}/results', 'zip', root_dir=f'../results/{self.__uuid}/results')
        #shutil.rmtree(f'../results/{self.__uuid}/results')
        return  self.__uuid, self.__failed_id_mapping, columns


    def plot_scatter(self):
        try:
            parent_path = f'../results/{self.__uuid}'
            results_path = f'{parent_path}/results'
            results_plot_path = f'{parent_path}/results/plots'
            data_path = f'{parent_path}/mass_spec_data.tsv'
            web_plot_path = f'{parent_path}/web_plots'
            plot_format = self.__get_format_from_log(results_path)

            data = pd.read_table(data_path, sep='\t', header=0)

            corr = data[self.__x].corr(data[self.__y])
            # lower_bound = min(data[self.__x].min(), data[self.__y].min())-0.5
            # upper_bound = max(data[self.__x].max(), data[self.__y].max())+0.5
            # print(lower_bound, upper_bound)

            fig, ax = plt.subplots()
            ax.scatter(data[self.__x], data[self.__y], linewidths=0.5, edgecolors='white') #
            # ax.set_xlim(lower_bound, upper_bound)
            # ax.set_ylim(lower_bound, upper_bound)
            ax.set_aspect('equal')
            ax.annotate('Pearson r='+str(round(corr,3)), (ax.get_xlim()[0]+0.5, ax.get_ylim()[1]-1))
            ax.spines[['right', 'top']].set_visible(False)
            plt.xlabel(self.__x)
            plt.ylabel(self.__y)
            title = f'Correlation {self.__x} vs {self.__y}'
            plt.title(title)
            title = title.replace(" ", "_")
            plt.savefig(f'{results_plot_path}/{title}.{plot_format}', dpi=130)
            plt.savefig(f'{web_plot_path}/{title}.jpeg', dpi=130)
            plt.close()
        except Exception as e:
            logger.error(e)
            raise


    def __get_format_from_log(self, results_path):
        try:
            with open(f'{results_path}/log.txt', 'r') as f:
                format_line = f.readlines()[4]
                if format_line.find('Plot format') != -1:
                    format_line = format_line.strip()
                return format_line[13:]
        except Exception as e:
            logger.error(e)
            raise


    def _set_true_positive_proteins_raw_data(self, df):
        self.__true_positive_proteins_raw_data = df
