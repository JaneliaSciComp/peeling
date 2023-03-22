import argparse
import os
from datetime import datetime
import logging
import matplotlib.pyplot as plt
from peeling.cliuniprotcommunicator import CliUniProtCommunicator
from peeling.cliuserinputreader import CliUserInputReader
from peeling.cliprocessor import CliProcessor
from peeling.clipantherprocessor import CliPantherProcessor

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
    parser.add_argument("-n", "--nomap", action="store_true", help="no id mapping for local annotation files, true if specified")
    parser.add_argument("-a", "--cache", action="store_true", help="save the data retrieved from UniProt, true if specified")
    parser.add_argument("-f", "--format", choices=list(plt.gcf().canvas.get_supported_filetypes().keys()), help="the output format of plots, default is png")
    parser.add_argument("-p", "--panther", help="the organism from which the mass spec data is made, a required input for Panther enrichment analysis. Please refer to Panther's API page http://pantherdb.org/services/oai/pantherdb/supportedgenomes for supported organism. Choose the corresponding 'long_names', and wrap it by quotes, e.g. 'Homo sapiens'")

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
    plot_format = args.format if args.format is not None else 'png'
    no_id_mapping = args.nomap
    panther_organism = args.panther

    logger.info(f'{start_time} Analysis starts...')
    user_input_reader = CliUserInputReader(mass_filename, num_controls, num_replicates, output_directory, tolerance, ids_filename, annotation_surface_filename, annotation_cyto_filename, cache, plot_format, no_id_mapping)
    uniprot_communicator = CliUniProtCommunicator(cache)
    processor = CliProcessor(user_input_reader, uniprot_communicator)
    path = processor.start()

    if panther_organism is not None:
        panther_processor = CliPantherProcessor(panther_organism, path)
        panther_processor.start()

    logger.info(f'Results saved at {path}')
    end_time = datetime.now()
    logger.info(f'{end_time} Analysis finished! Time: {end_time - start_time}')

    

if __name__ == "__main__":
    main()