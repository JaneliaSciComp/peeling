import argparse
import os
from datetime import datetime
import logging
import matplotlib.pyplot as plt
from peeling.cliuniprotcommunicator import CliUniProtCommunicator
from peeling.cliuserinputreader import CliUserInputReader
from peeling.cliprocessor import CliProcessor
from peeling.clipantherprocessor import CliPantherProcessor
from peeling.cellular_compartments import cellular_compartments

logger = logging.getLogger('peeling')
logger.setLevel(logging.INFO)
log_handler = logging.StreamHandler()
log_handler.setFormatter(logging.Formatter('%(asctime)s | %(levelname)s: %(message)s'))
logger.addHandler(log_handler)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mass", help="mass spec data file, e.g. data/mass_spec_data.tsv")
    parser.add_argument("controls", type=int, help="number of controls")
    parser.add_argument("replicates", type=int, help="number of replicates for each control")
    parser.add_argument("-t", "--tolerance", type=int, help="tolerance of non-included, default is 0")
    parser.add_argument("-o", "--output", help=" directory to store output results")
    parser.add_argument("-i", "--ids", help="latest_ids file directory, e.g. data/id_mapping.tsv")
    parser.add_argument(
        "--cc",
        "--cellular_compartment",
        choices=['cs', 'nu', 'mt', 'ot'],
        help="Choose between: cs - cell surface [default], mt - mitochondria, nu - nucleus or ot - other. If other is chosen, the true positive (--tp) and false positive (--fp) files must be specified.",
        default="cs"
    )
    parser.add_argument("--tp", "--true-positive", help="true positive annotation file, e.g. data/annotation_true_positive.tsv")
    parser.add_argument("--fp", "--false-positive", help="false positive annotation file, e.g. data/annotation_false_positive.tsv")
    parser.add_argument("-n", "--nomap", action="store_true", help="no id mapping for local annotation files, true if specified")
    parser.add_argument("-a", "--cache", action="store_true", help="save the data retrieved from UniProt, true if specified")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("-f", "--format", choices=list(plt.gcf().canvas.get_supported_filetypes().keys()), help="the output format of plots, default is png")
    parser.add_argument("-p", "--panther", help="the organism from which the mass spec data is made, a required input for Panther enrichment analysis. Please refer to Panther's API page http://pantherdb.org/services/oai/pantherdb/supportedgenomes for supported organism. Choose the corresponding 'long_names', and wrap it by quotes, e.g. 'Homo sapiens'")

    args = parser.parse_args()

    if args.cc not in cellular_compartments :
        # Set 'tp' and 'fp' as required
        if not args.tp or not args.fp:
            parser.error("The 'true positive' and 'false positive' arguments are required when 'cellular compartment' is set to 'other'.")

    if args.verbose:
        logger.setLevel(logging.DEBUG)



    start_time = datetime.now()

    mass_filename = args.mass
    num_controls = args.controls
    num_replicates = args.replicates
    tolerance = args.tolerance if args.tolerance is not None else 0
    output_directory = args.output if args.output is not None else os.getcwd()
    ids_filename = args.ids 
    true_positive_filename = args.tp
    false_positive_filename = args.fp
    cellular_compartment = args.cc
    cache = args.cache
    plot_format = args.format if args.format is not None else 'png'
    no_id_mapping = args.nomap
    panther_organism = args.panther

    if cellular_compartment in cellular_compartments:
        logger.info(f'Running analysis for {cellular_compartments.get(cellular_compartment).get("long_name")} proteins')
    else:
        logger.info(f'Running analysis for custom cellular compartment')

    logger.info(f'{start_time} Analysis starts...')
    user_input_reader = CliUserInputReader(
        mass_filename,
        num_controls,
        num_replicates,
        output_directory,
        tolerance,
        ids_filename,
        true_positive_filename,
        false_positive_filename,
        cache,
        plot_format,
        no_id_mapping,
        cellular_compartment
    )
    uniprot_communicator = CliUniProtCommunicator(cache, cellular_compartment)
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
