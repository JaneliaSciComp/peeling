from abc import ABC, abstractmethod
import logging

logger = logging.getLogger('peeling')


class UserInputReader(ABC):
    def __init__(self, num_controls, num_replicates, tolerance, plot_format):
        self.__num_controls = num_controls
        self.__num_replicates = num_replicates
        self.__tolerance = tolerance
        self.__plot_format = plot_format
    
    
    def _check_file(self, df):
        try:
            assert(len(df) >= 1), 'The file is empty'
        except AssertionError as e:
            logger.error('Stopped!', e)
            return
    

    def _check_mass_spec_file(self, df):
        try:
            assert(df.shape[1] == self.__num_controls * self.__num_replicates + 1), 'The number of columns does not match the input numbers'
        except AssertionError as e:
            logger.error('Stopped!', e)
            logger.error('Check the input file is tab delimited (.tsv) and has correct data')
            return
    

    @abstractmethod
    def get_mass_data(self):
        raise NotImplemented()


    @abstractmethod
    def get_mass_spec_filename(self):
        raise NotImplemented()
    

    def get_num_controls(self):
        return self.__num_controls
    

    def get_num_replicates(self):
        return self.__num_replicates
    

    def get_tolerance(self):
        return self.__tolerance
    

    def get_plot_format(self):
        return self.__plot_format
    
    
    
    

    