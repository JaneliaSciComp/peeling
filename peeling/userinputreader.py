from abc import ABC, abstractmethod
import logging
import matplotlib.pyplot as plt

logger = logging.getLogger('peeling')


class UserInputReader(ABC):
    def __init__(self, num_controls, num_replicates, tolerance, plot_format, cellular_compartment):
        self.__num_controls = num_controls
        self.__num_replicates = num_replicates
        self.__tolerance = tolerance
        self.__plot_format = plot_format
        self.__cellular_compartment = 'cs' if cellular_compartment is None else cellular_compartment
        self.__check_init()


    def __check_init(self):
        try:
            assert(self.__num_controls >= 1), '# Controls should be a positive integer'
            assert(self.__num_replicates >= 1), '# Replicates should be a positive integer'
            assert(self.__tolerance >= 0 and self.__tolerance <= self.__num_controls*self.__num_replicates), 'Tolerance should be an integer in [0, #controls * #replicates)'
            assert(self.__plot_format in set(plt.gcf().canvas.get_supported_filetypes().keys())), 'The plot format is invalid'
        except AssertionError as e:
            logger.error(e)
            raise


    def _check_file(self, df):
        try:
            assert(len(df) >= 1), 'The file is empty'
        except AssertionError as e:
            logger.error(e)
            raise


    def _check_mass_spec_file(self, df):
        try:
            assert(df.shape[1] == self.__num_controls * self.__num_replicates + 1), 'The number of columns does not equal #replicates * #controls '
        except AssertionError as e:
            logger.error(e)
            logger.error('Check the input file is tab delimited (.tsv) and has correct data')
            raise


    @abstractmethod
    def get_mass_data(self):
        raise NotImplementedError()


    @abstractmethod
    def get_mass_spec_filename(self):
        raise NotImplementedError()


    def get_num_controls(self):
        return self.__num_controls


    def get_num_replicates(self):
        return self.__num_replicates


    def get_tolerance(self):
        return self.__tolerance


    def get_plot_format(self):
        return self.__plot_format

    def get_cellular_compartment(self):
        return self.__cellular_compartment
