#from asyncio.log import logger
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import auc
import os
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger('peeling')


class Processor(ABC):
    def __init__(self, user_input_reader, uniprot_communicator):
        self.__user_input_reader = user_input_reader
        self.__uniprot_communicator = uniprot_communicator
        
    
    @abstractmethod
    def _get_id_mapping_data(self, data):
        raise NotImplemented()


    def _merge_id(self, mass_data, id_mapping_data):
        logger.debug(f'\n{id_mapping_data.head()}')
        id_mapping_data.drop_duplicates(subset=['From'], keep='first', inplace=True)
        id_mapping_data.set_index('From', inplace=True)

        mass_data = mass_data.merge(id_mapping_data, how='left', left_on = mass_data.columns[0], right_index=True)
        id_mapping_data.reset_index(inplace=True)
        logger.debug(f'len(data): {len(mass_data)}')
        logger.debug(f'\n{mass_data.head()}')
        logger.debug(f"No Id mapping data: {np.sum(np.sum(mass_data[['From', 'Entry']].isnull()))}")
        mass_data[['From', 'Entry']]=mass_data[['From', 'Entry']].fillna(axis=1, method='ffill')
        logger.debug(f"After fillna: {np.sum(np.sum(mass_data[['From', 'Entry']].isnull()))}")
        updated_ids=np.sum(mass_data['From']!=mass_data['Entry'])
        logger.info(f'Mapped ids: {updated_ids}')
        mass_data.drop([mass_data.columns[0]], axis=1, inplace=True)
        mass_data.set_index('Entry', inplace=True)
        logger.info('Id mapping is done') #To do
        return mass_data
    

    @abstractmethod
    def _get_annotation_data(self, type):
        raise NotImplemented()


    def __merge_annotation(self, mass_data, annotation, type):
        '''
        type: 'surface' or 'cyto'
        '''
        annotation['Add'] = 1
        #annotation = self._merge_id(annotation, id_mapping_data)
        #annotation.reset_index(inplace=True)
        annotation.drop_duplicates(keep='first', inplace=True)
        annotation.dropna(axis=0, how='any', inplace=True)
        annotation.set_index('Entry', inplace=True)
        
        mass_data = mass_data.merge(annotation, how='left', left_index=True, right_index=True)
        new_col_name = 'TP' if type=='surface' else 'FP'
        mass_data.rename(columns={'Add': new_col_name}, inplace=True)
        
        mass_data[new_col_name] = mass_data[new_col_name].fillna(0)
        logger.info(f'Adding annotation_{type} is done.') #To do
        return mass_data
    

    def __calculate_TPR_FPR_diff(self, data, col_to_sort):
        '''
        Sort data on col_to_sort in descending order, calculate accumulative TPR, FPR and TPR-FPR. 
        Input
        data: df
        col_to_sort: int, the index of the column to sort
        return df
        '''
        col_name = data.columns[col_to_sort]
        data.sort_values(by=[col_name], ascending=False, inplace=True)
        
        TPR_col_name = "TPR_" + col_name 
        FPR_col_name = "FPR_" + col_name
        data[[TPR_col_name, FPR_col_name]] = data[['TP', 'FP']].cumsum()
        data[TPR_col_name] = data[TPR_col_name] / data['TP'].sum()
        data[FPR_col_name] = data[FPR_col_name] / data['FP'].sum()
        data['TPR-FPR_'+col_name] = data[TPR_col_name] - data[FPR_col_name]
        return data
    

    def __plot_line(self, data, output_dir):
        '''
        Make line plot of the last three columns (TPR, FPR, TPR-FPR)
        '''
        col_list = data.columns[-3:]
        plt.figure()
        data[col_list].plot(use_index=False, ) #xticks = []
        
        plt.xlabel('Rank')
        plt.title('TPR, FPR, TPR-FPR_'+col_list[0][4:])
        fig_name = f'TPR_FPR_{col_list[0][4:]}'
        plt.savefig(f'{output_dir}/{fig_name}.{self.__user_input_reader.get_plot_format()}')
        return plt, fig_name
    

    @abstractmethod
    def _plot_supplemental(self, plt, fig_name):
        raise NotImplemented()
    

    def __filter_by_max_TPR_FPR_diff(self, data):
        '''
        Set cut-off point to be the point with the maximal TPR-FPR; Set include = True if before or at this pos, False otherwise
        Return FPR, TPR of the cut-off point
        '''
        cut_off_pos = data.iloc[:, -1].argmax()
        #print(cut_off_pos, data.iloc[cut_off_pos, -1])
        
        col_name = 'include_' + data.columns[-1][8:]
        data[col_name] = True
        data.iloc[cut_off_pos + 1:, -1] = False
        #print(data.head())
        return data.iloc[cut_off_pos, -3], data.iloc[cut_off_pos, -4]
    
    
    def __plot_roc(self, data, cutoff_fpr, cutoff_tpr, output_dir):
        '''
        Make ROC, calculate AUC, label the cut off point
        '''
        fig, ax = plt.subplots()
        ax.plot(data.iloc[:, -3], data.iloc[:, -4])
        ax.set_aspect('equal')
        plt.title('ROC_'+data.columns[-3][4:])
        plt.xlabel('FPR')
        plt.ylabel('TPR')
        plt.text(0, 0.9, 'AUC = ' + str(round(auc(data.iloc[:, -3], data.iloc[:, -4]), 2)))
        plt.plot(cutoff_fpr, cutoff_tpr, marker='o', color='r')
        ax.annotate('Cut-off Point\nFPR='+str(round(cutoff_fpr,3))+'\nTPR='+str(round(cutoff_tpr,3)), (cutoff_fpr+0.05, cutoff_tpr-0.15))
        fig_name = f'ROC_{data.columns[-3][4:]}'
        plt.savefig(f'{output_dir}/{fig_name}.{self.__user_input_reader.get_plot_format()}')
        return plt, fig_name
    

    def __get_surface_proteins(self, data, path, plots_path):
        '''
        If a protein is included in at least num_ctrl * num_rep - tolerance columns, output it as surface protein
        
        Output
        Accession ids of the surface proteins
        '''
        total_col = self.__user_input_reader.get_num_controls() * self.__user_input_reader.get_num_replicates()
        start_col = 0 #total_col * (self.__user_input_reader.get_num_conditions() - 1)
        threshold = total_col - self.__user_input_reader.get_tolerance()
        
        for i in range(start_col, start_col + total_col):
            self.__calculate_TPR_FPR_diff(data, i)
            plt, fig_name = self.__plot_line(data, plots_path)
            self._plot_supplemental(plt, fig_name)
            cutoff_fpr, cutoff_tpr = self.__filter_by_max_TPR_FPR_diff(data)
            plt, fig_name = self.__plot_roc(data, cutoff_fpr, cutoff_tpr, plots_path)
            self._plot_supplemental(plt, fig_name)
            data.drop(data.columns[-4:-1], axis=1, inplace=True)
        
        col_name = 'include_sum'
        data[col_name] = data.iloc[:, -total_col:].sum(axis=1)
        
        surface_proteins = pd.DataFrame(data[data[col_name] >= threshold].index).dropna(axis=0, how='any')
        surface_proteins.drop_duplicates(keep='first', inplace=True)
        logger.info(f'{len(surface_proteins)} surface proteins found')
        surface_proteins.to_csv(f'{path}/surface_proteins.tsv', sep='\t', index=False)
        

    @abstractmethod
    def _construct_path(self):
        raise NotImplemented()


    async def _analyze(self, data, parent_path):
       # num_conditions = self.__user_input_reader.get_num_conditions()
        id_col = data.columns[0]
        data.rename(columns={id_col: 'From'}, inplace=True)
        
        id_mapping_data = await self._get_id_mapping_data(data)
        data = self._merge_id(data, id_mapping_data)
        #id_mapping_data = self._get_id_mapping_data_annotation()
        annotation_surface = await self._get_annotation_data('surface')
        data = self.__merge_annotation(data, annotation_surface, 'surface')
        annotation_cyto = await self._get_annotation_data('cyto')
        data = self.__merge_annotation(data, annotation_cyto, 'cyto')
        
        plots_path = os.path.join(parent_path, "plots") 
        try: 
            os.makedirs(plots_path) 
        except OSError as error: 
            logger.debug(error)
        
        self.__get_surface_proteins(data, parent_path, plots_path)
    

    def _write_args(self, path):
        with open(os.path.join(path, 'log.txt'), 'w') as f:
            f.write('Mass spec file: ' + str(self.__user_input_reader.get_mass_spec_filename()) + '\n')
            f.write(f'Number of controls: {self.__user_input_reader.get_num_controls()}\n')
            f.write(f'Number of replicates: {self.__user_input_reader.get_num_replicates()}\n')
            f.write(f'Tolerance: {self.__user_input_reader.get_tolerance()}\n')
            f.write(f'Plot format: {self.__user_input_reader.get_plot_format()}\n')


    @abstractmethod
    def start(self):
        raise NotImplemented()


    def _get_user_input_reader(self):
        return self.__user_input_reader
    
    
    def _get_uniprot_communicator(self):
        return self.__uniprot_communicator