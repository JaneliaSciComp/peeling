import pandas as pd
import numpy as np
from datamanagement.userinputreader import UserInputReader
import logging

logger = logging.getLogger('peeling')


class CliUserInputReader(UserInputReader):
    def __init__(self, mass_filename, num_controls, num_replicates, output_directory, tolerance, ids_filename, annotation_surface_filename, annotation_cyto_filename, cache, plot_format, no_id_mapping):
        super().__init__(num_controls, num_replicates, tolerance, plot_format)
        self.__mass_filename = mass_filename
        self.__output_directory = output_directory
        self.__ids_filename = ids_filename
        self.__annotation_surface_filename = annotation_surface_filename
        self.__annotation_cyto_filename = annotation_cyto_filename
        self.__save = cache
        self.__no_id_mapping = no_id_mapping


    def __read_file(self, filename):
        try:
            df = pd.read_table(filename, sep='\t', header=0)
        except UnicodeDecodeError as e1:
            logger.error('Stopped!', e1) 
            logger.error('Check the input file is tab delimited (.tsv)')
            return
        except FileNotFoundError as e2:
            logger.error(e2)
            return
        
        self._check_file(df)
        return df


    # implement abstract method
    def get_mass_data(self):
        data = self.__read_file(self.__mass_filename)
        self._check_mass_spec_file(data)
        logger.info('Read in %d rows and %d columns from mass spec data' % data.shape)
        return data
    

    # implement abstract method
    def get_mass_spec_filename(self):
        return self.__mass_filename
    

    def get_latest_ids_filename(self):
        return self.__ids_filename
    

    def get_annotation_surface_filename(self):
        return self.__annotation_surface_filename
    

    def get_annotation_cyto_filename(self):
        return self.__annotation_cyto_filename


    def get_latest_ids(self):
        df = self.__read_file(self.__ids_filename)
        logger.info('Read in %d rows from latest_ids file' % (len(df)))
        return df
       

    def get_annotation_surface(self):
        df = self.__read_file(self.__annotation_surface_filename)
        logger.info('Read in %d rows from annotation_surface file' % (len(df)))
        return df
       

    def get_annotation_cyto(self):
        df = self.__read_file(self.__annotation_cyto_filename)
        logger.info('Read in %d rows from annotation_cyto file' % (len(df)))
        return df

    
    def get_output_directory(self):
        return self.__output_directory


    def get_save(self):
        return self.__save
    

    def get_id_mapping(self):
        return self.__no_id_mapping