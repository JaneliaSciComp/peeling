import argparse
import os
from datetime import datetime
from datamanagement.uniprotcommunicator import UniProtCommunicator
from datamanagement.userinputreader import UserInputReader
from processor.processor import Processor


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mass", help="mass spec data directory including filename")
    parser.add_argument("controls", type=int, help="number of controls for each condition")
    parser.add_argument("replicates", type=int, help="number of replicates for each control")
    parser.add_argument("-t", "--tolerance", type=int, help="tolerance of non-included")
    parser.add_argument("-o", "--output", help=" directory to store output results")
    parser.add_argument("-c", "--conditions", type=int, help="number of conditions")
    parser.add_argument("-i", "--ids", help="latest_ids file directory including filename")
    parser.add_argument("-u", "--surface", help="annotation_surface file directory including filename")
    parser.add_argument("-y", "--cyto", help="annotation_cyto file directory including filename")
    parser.add_argument("-s", "--save", action="store_true", help="save the data retrieved from UniProt, true if specified")

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
    save = args.save
    
    try:
        assert(num_controls>=1 and num_replicates>=1 and num_conditions>=1 and tolerance>=0), 'Controls, replicates, (conditions) should not be less than 1, and tolerance should not be less than 0.'
    except AssertionError as e:
        print('Stopped!', e)
        return

    print('Analysis starts...')
    user_input_reader = UserInputReader(mass_filename, num_controls, num_replicates, output_directory, num_conditions, tolerance, ids_filename, annotation_surface_filename, annotation_cyto_filename, save)
    uniprot_communicator = UniProtCommunicator()
    processor = Processor(user_input_reader, uniprot_communicator)
    processor.analyze()

    end_time = datetime.now()
    print(f'Analysis finished! time: {end_time - start_time}')
    

if __name__ == "__main__":
    main()