from re import sub
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import auc
import os
from datetime import datetime


class Processor():
    def __init__(self, user_input_reader, uniprot_communicator):
        self.__user_input_reader = user_input_reader
        self.__uniprot_communicator = uniprot_communicator
        self.__ids = None


    def _merge_id(self, data):
        if self.__ids is not None:
            new_ids_df = self.__ids.copy()
            new_ids_df = new_ids_df.iloc[:, :2]
            new_ids_df.columns = ['From', 'Entry']
        elif self.__user_input_reader.get_latest_ids_filename() is not None:
            # read in local ids file
            new_ids_df = self.__user_input_reader.get_latest_ids()
            self.__ids = new_ids_df.copy()
            new_ids_df = new_ids_df.iloc[:, :2] # the first two columns should be old ids and new ids
            new_ids_df.columns = ['From', 'Entry']
        else:
            # get latest ids by communicating with UniProt
            old_ids = list(data.iloc[:, 0])
            new_ids_df = self.__uniprot_communicator.get_latest_id(old_ids)
            self.__ids = new_ids_df.copy()
            new_ids_df = new_ids_df[['From', 'Entry']]
        
        new_ids_df.drop_duplicates(subset=['From'], keep='first', inplace=True)
        new_ids_df.set_index('From', inplace=True)

        data = data.merge(new_ids_df, how='left', left_on = data.columns[0], right_index=True)
        col_to_drop = data.columns[0]
        data.drop([col_to_drop], axis=1, inplace=True)
        for name in data.columns:
            if name[-2] == '_':
                data.rename(columns={name:name[:-2]}, inplace=True)
        data.set_index('Entry', inplace=True)
        # print(data.head())
        print('Id mapping is done') #To do

        return data
    

    def _merge_annotation(self, data, retrieved_path):
        if self.__user_input_reader.get_annotation_surface_filename() is not None: # use local annotation file
            annotation_surface = self.__user_input_reader.get_annotation_surface() # the first column should be ids
            annotation_surface = pd.DataFrame(annotation_surface.iloc[:, 0])
            annotation_surface['Add'] = 1
        else: # retrieve annotation file from UniProt
            annotation_surface = self.__uniprot_communicator.get_annotation_surface()
            if retrieved_path is not None:
                annotation_surface.dropna(subset=['Entry'], axis=0, how='any', inplace=True)
                annotation_surface.to_csv(retrieved_path+'/annotation_surface.tsv', sep='\t', index=False)
            annotation_surface['Add'] = 1
            annotation_surface = annotation_surface[['Entry', 'Add']]
        annotation_surface = self._merge_id(annotation_surface)
        annotation_surface.reset_index(inplace=True)
            
        if self.__user_input_reader.get_annotation_cyto_filename() is not None: # use local annotation file
            annotation_cyto = self.__user_input_reader.get_annotation_cyto()
            annotation_cyto = pd.DataFrame(annotation_cyto.iloc[:, 0])
            annotation_cyto['Add'] = 1
        else: # retrieve annotation file from UniProt
            annotation_cyto = self.__uniprot_communicator.get_annotation_cyto()
            if retrieved_path is not None:
                annotation_cyto.dropna(subset=['Entry'], axis=0, how='any', inplace=True)
                annotation_cyto.to_csv(retrieved_path+'/annotation_cyto.tsv', sep='\t', index=False)
            annotation_cyto['Add'] = 1
            annotation_cyto = annotation_cyto[['Entry', 'Add']]
        annotation_cyto = self._merge_id(annotation_cyto)
        annotation_cyto.reset_index(inplace=True)
            
        annotation_surface.drop_duplicates(keep='first', inplace=True)
        annotation_surface.dropna(axis=0, how='any', inplace=True)
        annotation_surface.set_index('Entry', inplace=True)
        annotation_cyto.drop_duplicates(keep='first', inplace=True)
        annotation_cyto.dropna(axis=0, how='any', inplace=True)
        annotation_cyto.set_index('Entry', inplace=True)
        data = data.merge(annotation_surface, how='left', left_index=True, right_index=True)
        data.rename(columns={'Add': 'TP'}, inplace=True)
        data = data.merge(annotation_cyto, how='left', left_index=True, right_index=True)
        data.rename(columns={'Add': 'FP'}, inplace=True)
        
        data['TP'] = data['TP'].fillna(0)
        data['FP'] = data['FP'].fillna(0)

        print('Adding annotation is done.') #To do
        return data
    

    def _calculate_TPR_FPR_diff(self, data, col_to_sort):
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
    

    def _plot_line(self, data, output_dir):
        '''
        Make line plot of the last three columns (TPR, FPR, TPR-FPR)
        '''
        col_list = data.columns[-3:]
        plt.figure()
        data[col_list].plot(use_index=False, xticks = []) 
        
        plt.title('TPR, FPR, TPR-FPR_'+col_list[0][4:])
        plt.savefig(f'{output_dir}/TPR_FPR_{col_list[0][4:]}.pdf')
    

    def _filter_by_max_TPR_FPR_diff(self, data):
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
    
    
    def _plot_roc(self, data, cutoff_fpr, cutoff_tpr, output_dir):
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
        plt.savefig(f'{output_dir}/ROC_{data.columns[-3][4:]}.pdf')
    

    def _get_surface_proteins(self, data, condition, path, plots_path):
        '''
        If a protein is included in at least num_ctrl * num_rep - tolerance columns, output it as surface protein
        
        Output
        Accession ids of the surface proteins
        '''
        total_col = self.__user_input_reader.get_num_controls() * self.__user_input_reader.get_num_replicates()
        start_col = total_col * (self.__user_input_reader.get_num_conditions() - 1)
        threshold = total_col - self.__user_input_reader.get_tolerance()
        
        for i in range(start_col, start_col + total_col):
            self._calculate_TPR_FPR_diff(data, i)
            self._plot_line(data, plots_path)
            cutoff_fpr, cutoff_tpr = self._filter_by_max_TPR_FPR_diff(data)
            self._plot_roc(data, cutoff_fpr, cutoff_tpr, plots_path)
            data.drop(data.columns[-4:-1], axis=1, inplace=True)
        
        col_name = 'include_sum_' + str(condition)
        data[col_name] = data.iloc[:, -total_col:].sum(axis=1)
        
        surface_proteins = pd.DataFrame(data[data[col_name] >= threshold].index).dropna(axis=0, how='any')
        surface_proteins.drop_duplicates(keep='first', inplace=True)
        print(f'{len(surface_proteins)} surface proteins found')
        surface_proteins.to_csv(f'{path}/surface_proteins.tsv', sep='\t', index=False)
        print(f'Results of condition{condition} are saved at {path}')
        

    def analyze(self):
        num_conditions = self.__user_input_reader.get_num_conditions()
        data = self.__user_input_reader.get_mass_data()
        parent_path = os.path.join(self.__user_input_reader.get_output_directory(), str(datetime.now()).replace(':','-'))
        
        if self.__user_input_reader.get_save():
            retrieved_path = os.path.join(parent_path, "retrieved_data")
            try: 
                os.makedirs(retrieved_path, exist_ok=True) 
            except OSError as error: 
                print(error)
        else:
            retrieved_path = None
        data = self._merge_id(data)
        data = self._merge_annotation(data, retrieved_path)
        if self.__user_input_reader.get_save():
            self.__ids.to_csv(retrieved_path+'/latest_ids.tsv', sep='\t', index=False)

        for i in range(1, num_conditions+1):
            path = os.path.join(parent_path, "condition" + str(i))
            plots_path = os.path.join(path, "plots") 
            try: 
                os.makedirs(plots_path) 
            except OSError as error: 
                print(error)  #To do
            
            self._get_surface_proteins(data, i, path, plots_path)
