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
    parser.add_argument("mass", help="mass spec data directory, e.g. data/mass_spec_data.tsv")
    parser.add_argument("controls", type=int, help="number of controls")
    parser.add_argument("replicates", type=int, help="number of replicates for each control")
    parser.add_argument("-t", "--tolerance", type=int, help="tolerance of non-included, default is 0")
    parser.add_argument("-o", "--output", help=" directory to store output results")
    parser.add_argument("-i", "--ids", help="latest_ids file directory, e.g. data/id_mapping.tsv")
    parser.add_argument("-s", "--surface", help="annotation_surface file directory, e.g. data/annotation_surface.tsv")
    parser.add_argument("-c", "--cyto", help="annotation_cyto file directory, e.g. data/annotation_cyto.tsv")
    parser.add_argument("-a", "--cache", action="store_true", help="save the data retrieved from UniProt, true if specified")
    parser.add_argument("-p", "--plot", choices=[list(plt.gcf().canvas.get_supported_filetypes().keys())], help="the output format of plots, default is png") #TODO
    parser.add_argument("-n", "--nomap", action="store_true", help="no id mapping for local annotation files, true if specified")

    args = parser.parse_args()

    start_time = datetime.now()

    mass_filename = args.mass
    num_controls = args.controls
    num_replicates = args.replicates
    tolerance = args.tolerance if args.tolerance is not None else 0
    output_directory = args.output if args.output is not None else os.getcwd()
    ids_filename = args.ids 
    annotation_surface_filename = args.surface
    annotation_cyto_filename = args.cyto
    cache = args.cache
    plot_format = args.plot if args.plot is not None else 'png'
    no_id_mapping = args.nomap
    
    try:
        assert(num_controls>=1 and num_replicates>=1 and tolerance>=0 and tolerance<num_controls*num_replicates), 'Controls, replicates, (conditions) should not be less than 1, and tolerance should not be less than 0.'
    except AssertionError as e:
        logger.error('Stopped!', e)
        return

    logger.info(f'{start_time} Analysis starts...')
    user_input_reader = CliUserInputReader(mass_filename, num_controls, num_replicates, output_directory, tolerance, ids_filename, annotation_surface_filename, annotation_cyto_filename, cache, plot_format, no_id_mapping)
    uniprot_communicator = CliUniProtCommunicator(cache)
    processor = CliProcessor(user_input_reader, uniprot_communicator)
    processor.start()

    end_time = datetime.now()
    logger.info(f'{end_time} Analysis finished! Time: {end_time - start_time}')
    

if __name__ == "__main__":
    main()