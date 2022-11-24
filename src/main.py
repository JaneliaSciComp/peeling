import argparse
import os
from datetime import datetime
import logging
import matplotlib.pyplot as plt
from datamanagement.cliuniprotcommunicator import CliUniProtCommunicator
from datamanagement.cliuserinputreader import CliUserInputReader
from processors.cliprocessor import CliProcessor

logger = logging.getLogger('peeling')
#TODO: set level based on verbose option
logger.setLevel(logging.INFO)
log_handler = logging.StreamHandler()
log_handler.setFormatter(logging.Formatter('%(asctime)s | %(levelname)s: %(message)s'))
logger.addHandler(log_handler)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mass", help="mass spec data directory including filename, e.g. data/mass_spec_data.tsv")
    parser.add_argument("controls", type=int, help="number of controls for each condition")
    parser.add_argument("replicates", type=int, help="number of replicates for each control")
    parser.add_argument("-t", "--tolerance", type=int, help="tolerance of non-included, default is 0")
    parser.add_argument("-o", "--output", help=" directory to store output results")
    parser.add_argument("-c", "--conditions", type=int, help="number of conditions")
    parser.add_argument("-i", "--ids", help="latest_ids file directory including filename, e.g. data/id_mapping.tsv")
    parser.add_argument("-u", "--surface", help="annotation_surface file directory including filename, e.g. data/annotation_surface.tsv")
    parser.add_argument("-y", "--cyto", help="annotation_cyto file directory including filename, e.g. data/annotation_cyto.tsv")
    parser.add_argument("-a", "--cache", action="store_true", help="save the data retrieved from UniProt, true if specified")
    parser.add_argument("-p", "--plot", choices=[list(plt.gcf().canvas.get_supported_filetypes().keys())], help="the output format of plots, default is png") #TODO

    args = parser.parse_args()

    start_time = datetime.now()

    mass_filename = args.mass
    num_controls = args.controls
    num_replicates = args.replicates
    tolerance = args.tolerance if args.tolerance is not None else 0
    output_directory = args.output if args.output is not None else os.getcwd()
    num_conditions = args.conditions if args.conditions is not None else 1
    ids_filename = args.ids 
    annotation_surface_filename = args.surface
    annotation_cyto_filename = args.cyto
    cache = args.cache
    plot_format = args.plot if args.plot is not None else 'png'
    
    try:
        assert(num_controls>=1 and num_replicates>=1 and num_conditions>=1 and tolerance>=0), 'Controls, replicates, (conditions) should not be less than 1, and tolerance should not be less than 0.'
    except AssertionError as e:
        logger.error('Stopped!', e)
        return

    logger.info(f'{start_time} Analysis starts...')
    user_input_reader = CliUserInputReader(mass_filename, num_controls, num_replicates, output_directory, num_conditions, tolerance, ids_filename, annotation_surface_filename, annotation_cyto_filename, cache, plot_format)
    uniprot_communicator = CliUniProtCommunicator(cache)
    processor = CliProcessor(user_input_reader, uniprot_communicator)
    processor.start()

    end_time = datetime.now()
    logger.info(f'{end_time} Analysis finished! Time: {end_time - start_time}')
    

if __name__ == "__main__":
    main()