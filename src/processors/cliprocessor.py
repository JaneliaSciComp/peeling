from processors.processor import Processor
import os
from datetime import datetime
import pandas as pd


class CliProcessor(Processor):
    def __init__(self, user_input_reader, uniprot_communicator):
        super().__init__(user_input_reader, uniprot_communicator)
        self.__ids = None
        self.__path = None # path to save retrieved data


    # overriding abstract method
    def _get_id_mapping_data(self, mass_data):
        if self._get_user_input_reader().get_latest_ids_filename() is not None:
            # read in local ids file
            self.__ids = self._get_user_input_reader().get_latest_ids()
            self.__ids = self.__ids.iloc[:, :2] # the first two columns should be old ids and new ids
            self.__ids.columns = ['From', 'Entry']
        else:
            # get latest ids by communicating with UniProt
            old_ids = list(mass_data.iloc[:, 0])
            self.__ids = self._get_uniprot_communicator().get_latest_id(old_ids)
            if self._get_user_input_reader().get_save():
                self.__ids.to_csv(self.__path+'/latest_ids.tsv', sep='\t', index=False)
            self.__ids = self.__ids[['From', 'Entry']]
        return self.__ids


    # overriding abstract method
    def _get_id_mapping_data_annotation(self):
        return self.__ids

        
    # overriding abstract method
    def _get_annotation_data(self, type):
        '''
        type: 'surface' or 'cyto'
        '''
        if type == 'surface':
            if self._get_user_input_reader().get_annotation_surface_filename() is not None: # use local annotation file
                annotation = self._get_user_input_reader().get_annotation_surface() # the first column should be ids
                annotation = pd.DataFrame(annotation.iloc[:, 0])
                #annotation_surface['Add'] = 1
            else: # retrieve annotation file from UniProt
                annotation = self._get_uniprot_communicator().get_annotation_surface()
                annotation.dropna(subset=['Entry'], axis=0, how='any', inplace=True)
                if self._get_user_input_reader().get_save():
                    annotation.to_csv(f'{self.__path}/annotation_surface.tsv', sep='\t', index=False)
                #annotation_surface['Add'] = 1
                annotation = annotation[['Entry']]
        else:
            if self._get_user_input_reader().get_annotation_cyto_filename() is not None: # use local annotation file
                annotation = self._get_user_input_reader().get_annotation_cyto() # the first column should be ids
                annotation = pd.DataFrame(annotation.iloc[:, 0])
                #annotation_surface['Add'] = 1
            else: # retrieve annotation file from UniProt
                annotation = self._get_uniprot_communicator().get_annotation_cyto()
                annotation.dropna(subset=['Entry'], axis=0, how='any', inplace=True)
                if self._get_user_input_reader().get_save():
                    annotation.to_csv(f'{self.__path}/annotation_cyto.tsv', sep='\t', index=False)
                #annotation_surface['Add'] = 1
                annotation = annotation[['Entry']]
        annotation.columns = ['From']
        return annotation


    # overriding abstract method
    def _construct_path(self):
        parent_path = os.path.join(self._get_user_input_reader().get_output_directory(), str(datetime.now()).replace(':','-').replace(' ','_'))
        if self._get_user_input_reader().get_save():
            retrieved_path = os.path.join(parent_path, "retrieved_data")
            try: 
                os.makedirs(retrieved_path, exist_ok=True) 
            except OSError as error: 
                print(error)
        else:
            retrieved_path = None
        self.__path = retrieved_path
        return parent_path


    def _write_args(self, path):
        super()._write_args(path)
        with open(os.path.join(path, 'user_input.txt'), 'a') as f:
            ids = self._get_user_input_reader().get_latest_ids_filename()
            if ids is not None:
                f.write(f'Latest_ids file: {ids}\n')
            surface = self._get_user_input_reader().get_annotation_surface_filename()
            if surface is not None:
                f.write(f'Annotation_surface file: {surface}\n')
            cyto = self._get_user_input_reader().get_annotation_cyto_filename()
            if cyto is not None:
                f.write(f'Annotation_cyto file: {cyto}\n')
   

    # overriding super class method
    def start(self):
        data = self._get_user_input_reader().get_mass_data()
        parent_path = self._construct_path()
        self._analyze(data, parent_path)
        self._write_args(parent_path)
        print(f'Results saved at {parent_path}')

   