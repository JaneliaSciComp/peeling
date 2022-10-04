import pandas as pd
import numpy as np

class UserInputReader():
    def __init__(self, mass_filename, num_controls, num_replicates, output_directory, num_conditions, tolerance, ids_filename, annotation_surface_filename, annotation_cyto_filename, save):
        self.__mass_filename = mass_filename
        self.__num_conditions = num_conditions
        self.__num_controls = num_controls
        self.__num_replicates = num_replicates
        self.__output_directory = output_directory
        self.__tolerance = tolerance
        self.__ids_filename = ids_filename
        self.__annotation_surface_filename = annotation_surface_filename
        self.__annotation_cyto_filename = annotation_cyto_filename
        self.__save = save
    

    def _read_file(self, filename):
        try:
            df = pd.read_table(filename, sep='\t', header=0)
        except UnicodeDecodeError as e1:
            print('Stopped!', e1) #To do: replace print with log
            print('Check the input file is tab delimited (.tsv)')
            return
        except FileNotFoundError as e2:
            print(e2)
            return
        
        try:
            assert(len(df) >= 1), 'The file is empty'
        except AssertionError as e:
            print('Stopped!', e)
            return
        
        return df


    def get_mass_data(self):
        data = self._read_file(self.__mass_filename)
        try:
            assert(data.shape[1] == self.__num_conditions * self.__num_controls * self.__num_replicates + 1), 'The number of columns does not match the input numbers'
        except AssertionError as e:
            print('Stopped!', e)
            print('Check the input file is tab delimited (.tsv) and has correct data')
            return
            
        print('Read in %d rows and %d columns from mass spec data' % data.shape)
        return data
    

    def get_latest_ids_filename(self):
        return self.__ids_filename
    

    def get_annotation_surface_filename(self):
        return self.__annotation_surface_filename
    

    def get_annotation_cyto_filename(self):
        return self.__annotation_cyto_filename


    def get_latest_ids(self):
        df = self._read_file(self.__ids_filename)
        print('Read in %d rows from latest_ids file' % (len(df)))
        return df
       

    def get_annotation_surface(self):
        df = self._read_file(self.__annotation_surface_filename)
        print('Read in %d rows from annotation_surface file' % (len(df)))
        return df
       

    def get_annotation_cyto(self):
        df = self._read_file(self.__annotation_cyto_filename)
        print('Read in %d rows from annotation_cyto file' % (len(df)))
        return df
        

    def get_num_conditions(self):
        return self.__num_conditions
    

    def get_num_controls(self):
        return self.__num_controls
    

    def get_num_replicates(self):
        return self.__num_replicates
    

    def get_tolerance(self):
        return self.__tolerance
    
    
    def get_output_directory(self):
        return self.__output_directory
    

    def get_save(self):
        return self.__save