#################################
#   This is not for unit test   #
#################################

import unittest
import os, shutil
import pandas as pd


EXE_DIR = '../src/main.py'
OUTPUT_DIR = 'test_output/'
ANNO_SURFACE = '../data/annotation_surface.tsv'
ANNO_CYTO = '../data/annotation_cyto.tsv'
IDS = '../data/latest_ids_multiOrganisms.tsv'


class TestPeeling(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        for dir in os.listdir(OUTPUT_DIR):
            shutil.rmtree(OUTPUT_DIR+dir, ignore_errors=True)

    
    def test_local_ids_anno(self):
        # using local anno and ids files, local anno will be mapped on local ids file 
        print('\n\n\n')
        print('#########  local_ids_anno  #########')
        # execute peeling
        mass_data = '../data/mass_spec_data.tsv'
        ctrl = '2'
        rep = '3'
        output_dir = f'{OUTPUT_DIR}/local_ids_anno/'
        cmd = f'python3 {EXE_DIR} {mass_data} {ctrl} {rep} -s {ANNO_SURFACE} -c {ANNO_CYTO} --ids {IDS} -o {output_dir}'
        os.system(cmd)

        # check output 
        timestamp = os.listdir(output_dir)[-1]
        res_dir = output_dir + timestamp
        res_surface_prot = pd.read_table(f'{res_dir}/post-cutoff-proteome.tsv')
        print(res_surface_prot.head(3))
        self.assertTrue(len(res_surface_prot)>500, f'Found surface protein less than 500 ({len(res_surface_prot)})')
        

    def test_local_anno_remote_ids(self):
        # using local anno and ids files, local anno will be mapped 
        print('\n\n\n')
        print('#########  local_anno_remote_ids  #########')
        # execute peeling
        mass_data = '../data/mass_spec_data.tsv'
        ctrl = '2'
        rep = '3'
        output_dir = f'{OUTPUT_DIR}/local_anno_remote_ids/'
        cmd = f'python3 {EXE_DIR} {mass_data} {ctrl} {rep} -s {ANNO_SURFACE} -c {ANNO_CYTO} -o {output_dir}'
        os.system(cmd)

        # check output 
        timestamp = os.listdir(output_dir)[-1]
        res_dir = output_dir + timestamp
        res_surface_prot = pd.read_table(f'{res_dir}/post-cutoff-proteome.tsv')
        print(res_surface_prot.head(3))
        self.assertTrue(len(res_surface_prot)>500, f'Found surface protein less than 500 ({len(res_surface_prot)})')


    def test_local_anno_remote_ids_nomap(self):
        # using local anno and remote ids files, local anno should not be mapped 
        print('\n\n\n')
        print('#########  local_anno_remote_ids_nomap  #########')
        # execute peeling
        mass_data = '../data/mass_spec_data.tsv'
        ctrl = '2'
        rep = '3'
        output_dir = f'{OUTPUT_DIR}/local_anno_remote_ids_nomap/'
        nomap = '--nomap'
        cmd = f'python3 {EXE_DIR} {mass_data} {ctrl} {rep} -s {ANNO_SURFACE} -c {ANNO_CYTO} {nomap} -o {output_dir}'
        os.system(cmd)

        # check output 
        timestamp = os.listdir(output_dir)[-1]
        res_dir = output_dir + timestamp
        res_surface_prot = pd.read_table(f'{res_dir}/post-cutoff-proteome.tsv')
        print(res_surface_prot.head(3))
        self.assertTrue(len(res_surface_prot)>500, f'Found surface protein less than 500 ({len(res_surface_prot)})')


    def test_remote_anno_local_ids(self):
        # using remote anno files, and local ids files, remote anno will never be mapped 
        print('\n\n\n')
        print('#########  remote_anno_local_ids  #########')
        # execute peeling
        mass_data = '../data/mass_spec_data.tsv'
        ctrl = '2'
        rep = '3'
        output_dir = f'{OUTPUT_DIR}/remote_anno_local_ids/'
        cmd = f'python3 {EXE_DIR} {mass_data} {ctrl} {rep} --ids {IDS} -o {output_dir}'
        os.system(cmd)

        # check output 
        timestamp = os.listdir(output_dir)[-1]
        res_dir = output_dir + timestamp
        res_surface_prot = pd.read_table(f'{res_dir}/post-cutoff-proteome.tsv')
        print(res_surface_prot.head(3))
        self.assertTrue(len(res_surface_prot)>500, f'Found surface protein less than 500 ({len(res_surface_prot)})')


    def test_remote_anno_ids(self):
        # using remote anno and ids files, remote anno will never be mapped 
        print('\n\n\n')
        print('#########  remote_anno_ids  #########')
        # execute peeling
        mass_data = '../data/mass_spec_data.tsv'
        ctrl = '2'
        rep = '3'
        output_dir = f'{OUTPUT_DIR}/remote_anno_ids/'
        cmd = f'python3 {EXE_DIR} {mass_data} {ctrl} {rep} -o {output_dir}'
        os.system(cmd)

        # check output 
        timestamp = os.listdir(output_dir)[-1]
        res_dir = output_dir + timestamp
        res_surface_prot = pd.read_table(f'{res_dir}/post-cutoff-proteome.tsv')
        print(res_surface_prot.head(3))
        self.assertTrue(len(res_surface_prot)>500, f'Found surface protein less than 500 ({len(res_surface_prot)})')


    def test_panther(self):
        # using remote anno and ids files, remote anno will never be mapped 
        print('\n\n\n')
        print('#########  panther  #########')
        # execute peeling
        mass_data = '../data/mass_spec_data.tsv'
        ctrl = '2'
        rep = '3'
        output_dir = f'{OUTPUT_DIR}/panther/'
        panther_org = "'Mus musculus'"
        cmd = f'python3 {EXE_DIR} {mass_data} {ctrl} {rep} -s {ANNO_SURFACE} -c {ANNO_CYTO} --ids {IDS} -p {panther_org} -o {output_dir}'
        os.system(cmd)

        # check output 
        timestamp = os.listdir(output_dir)[-1]
        res_dir = output_dir + timestamp
        #names = []
        #self.assertTrue(len(res_surface_prot)>500, f'Found surface protein less than 500 ({len(res_surface_prot)})')
    
    
    #TODO
    # test user input, wrong rep/ctrl/panther_org, diff tolerance, format, empty/1col/1row/total wrong mass data


    # def test_test(self):
    #     self.assertTrue(2>1, 'false')
    #     self.assertTrue(1>2, 'failed')
        


if __name__ == '__main__':
    unittest.main()