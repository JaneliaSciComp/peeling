from fastapi import UploadFile
import pandas as pd
import csv
from datamanagement.userinputreader import UserInputReader
import logging

logger = logging.getLogger('peeling')


class WebUserInputReader(UserInputReader):
    def __init__(self, mass_file:UploadFile, num_controls, num_replicates, num_conditions, tolerance, plot_format): #, ids_file, annotation_surface_file, annotation_cyto_file
        super().__init__(num_controls, num_replicates, num_conditions, tolerance, plot_format)
        self.__mass_file = mass_file
    

    async def __decode_uploadFile(self):
        bytes = await self.__mass_file.read()
        lines = [line for line in bytes.decode("utf-8").split("\n") if line]
        reader = csv.DictReader(lines, delimiter="\t", quotechar='"')
        df = pd.DataFrame(list(reader))
        logger.debug(f'\n{df.head()}')
        self._check_file(df)        
        return df


    # implement abstract method
    async def get_mass_data(self):
        data = await self.__decode_uploadFile()
        self._check_mass_spec_file(data)
        logger.info('Read in %d rows and %d columns from mass spec data' % data.shape)
        return data
    

    # implement abstract method
    def get_mass_spec_filename(self):
        return self.__mass_file.filename
    



    
    
