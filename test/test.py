#################################
#   This is not for unit test   #
#################################

import unittest
import os, shutil
import pandas as pd


EXE_DIR = '../peeling/main.py'
OUTPUT_DIR = './test_output'
ANNO_SURFACE = '../data/annotation_surface.tsv'
ANNO_CYTO = '../data/annotation_cyto.tsv'
IDS = '../data/latest_ids_multiOrganisms.tsv'


class TestPeeling(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        for dir in os.listdir(OUTPUT_DIR):
            shutil.rmtree(f'{OUTPUT_DIR}/{dir}', ignore_errors=True)

    
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
        

    # def test_local_anno_remote_ids(self):
    #     # using local anno and remote ids files, local anno will be mapped 
    #     print('\n\n\n')
    #     print('#########  local_anno_remote_ids  #########')
    #     mass_data = '../data/mass_spec_data.tsv'
    #     ctrl = '2'
    #     rep = '3'
    #     output_dir = f'{OUTPUT_DIR}/local_anno_remote_ids/'
    #     cmd = f'python3 {EXE_DIR} {mass_data} {ctrl} {rep} -s {ANNO_SURFACE} -c {ANNO_CYTO} -o {output_dir}'
    #     os.system(cmd)

    #     # check output 
    #     timestamp = os.listdir(output_dir)[-1]
    #     res_dir = output_dir + timestamp
    #     res_surface_prot = pd.read_table(f'{res_dir}/post-cutoff-proteome.tsv')
    #     print(res_surface_prot.head(3))
    #     self.assertTrue(len(res_surface_prot)>500, f'Found surface protein less than 500 ({len(res_surface_prot)})')


    # def test_local_anno_remote_ids_nomap(self):
    #     # using local anno and remote ids files, local anno should not be mapped 
    #     print('\n\n\n')
    #     print('#########  local_anno_remote_ids_nomap  #########')
    #     mass_data = '../data/mass_spec_data.tsv'
    #     ctrl = '2'
    #     rep = '3'
    #     output_dir = f'{OUTPUT_DIR}/local_anno_remote_ids_nomap/'
    #     nomap = '--nomap'
    #     cmd = f'python3 {EXE_DIR} {mass_data} {ctrl} {rep} -s {ANNO_SURFACE} -c {ANNO_CYTO} {nomap} -o {output_dir}'
    #     os.system(cmd)

    #     # check output 
    #     timestamp = os.listdir(output_dir)[-1]
    #     res_dir = output_dir + timestamp
    #     res_surface_prot = pd.read_table(f'{res_dir}/post-cutoff-proteome.tsv')
    #     print(res_surface_prot.head(3))
    #     self.assertTrue(len(res_surface_prot)>500, f'Found surface protein less than 500 ({len(res_surface_prot)})')


    # def test_remote_anno_local_ids(self):
    #     # using remote anno files, and local ids files, remote anno will never be mapped 
    #     print('\n\n\n')
    #     print('#########  remote_anno_local_ids  #########')
    #     mass_data = '../data/mass_spec_data.tsv'
    #     ctrl = '2'
    #     rep = '3'
    #     output_dir = f'{OUTPUT_DIR}/remote_anno_local_ids/'
    #     cmd = f'python3 {EXE_DIR} {mass_data} {ctrl} {rep} --ids {IDS} -o {output_dir}'
    #     os.system(cmd)

    #     # check output 
    #     timestamp = os.listdir(output_dir)[-1]
    #     res_dir = output_dir + timestamp
    #     res_surface_prot = pd.read_table(f'{res_dir}/post-cutoff-proteome.tsv')
    #     print(res_surface_prot.head(3))
    #     self.assertTrue(len(res_surface_prot)>500, f'Found surface protein less than 500 ({len(res_surface_prot)})')


    def test_remote_anno_ids(self):
        # using remote anno and ids files, remote anno will never be mapped 
        print('\n\n\n')
        print('#########  remote_anno_ids  #########')
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


# All tests below are using local anno and ids files for convenience

    def test_panther(self):
        print('\n\n\n')
        print('#########  panther  #########')
        mass_data = '../data/mass_spec_data.tsv'
        ctrl = '2'
        rep = '3'
        output_dir = f'{OUTPUT_DIR}/panther/'
        panther_org = "'Mus musculus'"
        panther_org_id = '10090'
        cmd = f'python3 {EXE_DIR} {mass_data} {ctrl} {rep} -s {ANNO_SURFACE} -c {ANNO_CYTO} --ids {IDS} -p {panther_org} -o {output_dir}'
        os.system(cmd)

        # check output 
        timestamp = os.listdir(output_dir)[-1]
        res_dir = output_dir + timestamp
        names = ['Reactome_Pathway', 'Panther_GO_Slim_Cellular_Component', 'Panther_GO_Slim_Biological_Process']
        for name in names:
            res_file_dir = f'{res_dir}/post-cutoff-proteome_{panther_org_id}_{name}.tsv'
            self.assertTrue(os.path.exists(res_file_dir), f'{name} result file does not exist')
            df = pd.read_table(res_file_dir, sep='\t', header=0)
            self.assertEqual(len(df), 10, 'The number of terms is less than 10')
            self.assertEqual(len(df.columns), 2, 'The number of columns is less than 2')
    

#  # The following four tests test cache in different scenarios, do not need to be run for every change   
#     def test_cache_annotation(self):
#         mass_data = '../data/mass_spec_data.tsv'
#         ctrl = '2'
#         rep = '3'

#         # use local anno_cyto and latest_ids, retrieve remote anno_surface, save anno_surface
#         print('\n\n')
#         print(f'######### cache anno_surface  #########')
#         output_dir = f'{OUTPUT_DIR}/test_cache/anno_surface/'
#         cmd = f'python3 {EXE_DIR} {mass_data} {ctrl} {rep} -c {ANNO_CYTO} --ids {IDS} -o {output_dir} --cache'
#         os.system(cmd)
#         # check output 
#         timestamp = os.listdir(output_dir)[-1]
#         cache_file_dir = f'{output_dir}{timestamp}/retrieved_data/annotation_surface.tsv'
#         self.assertTrue(os.path.exists(cache_file_dir), f'anno_surface is not saved')
        
#         # use local anno_surface and latest_ids, retrieve remote anno_cyto, save anno_cyto
#         print('\n\n')
#         print(f'######### cache anno_cyto  #########')
#         output_dir = f'{OUTPUT_DIR}/test_cache/anno_cyto/'
#         cmd = f'python3 {EXE_DIR} {mass_data} {ctrl} {rep} -s {ANNO_SURFACE} --ids {IDS} -o {output_dir} --cache'
#         os.system(cmd)
#         # check output 
#         timestamp = os.listdir(output_dir)[-1]
#         cache_file_dir = f'{output_dir}{timestamp}/retrieved_data/annotation_cyto.tsv'
#         self.assertTrue(os.path.exists(cache_file_dir), f'anno_cyto is not saved')
        
#         # use local latest_ids, retrieve remote anno_surface and anno_cyto, save both
#         print('\n\n')
#         print(f'######### cache anno_surface and anno_cyto  #########')
#         output_dir = f'{OUTPUT_DIR}/test_cache/anno_surface_cyto/'
#         cmd = f'python3 {EXE_DIR} {mass_data} {ctrl} {rep} --ids {IDS} -o {output_dir} --cache'
#         os.system(cmd)

#          # check output 
#         timestamp = os.listdir(output_dir)[-1]
#         cache_dir = f'{output_dir}{timestamp}/retrieved_data'
#         for i in ['annotation_surface', 'annotation_cyto']:
#             cache_file_dir = f'{cache_dir}/{i}.tsv'
#             self.assertTrue(os.path.exists(cache_file_dir), f'{i} is not saved')


#     def test_cache_ids(self):
#         mass_data = '../data/mass_spec_data.tsv'
#         ctrl = '2'
#         rep = '3'
        
#         print('\n\n')
#         print(f'######### cache latestids  #########')
#         output_dir = f'{OUTPUT_DIR}/test_cache/latestids/'
#         cmd = f'python3 {EXE_DIR} {mass_data} {ctrl} {rep} -s {ANNO_SURFACE} -c {ANNO_CYTO} -o {output_dir} --cache'
#         os.system(cmd)

#          # check output 
#         timestamp = os.listdir(output_dir)[-1]
#         cache_file_dir = f'{output_dir}{timestamp}/retrieved_data/latest_ids.tsv'
#         self.assertTrue(os.path.exists(cache_file_dir), 'latest_ids is not saved')


#     def test_cache_ids_anno(self):
#         mass_data = '../data/mass_spec_data.tsv'
#         ctrl = '2'
#         rep = '3'
        
#         print('\n\n')
#         print(f'######### cache latest_ids and annotations  #########')
#         output_dir = f'{OUTPUT_DIR}/test_cache/latestids_annotations/'
#         cmd = f'python3 {EXE_DIR} {mass_data} {ctrl} {rep} -o {output_dir} --cache'
#         os.system(cmd)

#          # check output 
#         timestamp = os.listdir(output_dir)[-1]
#         cache_dir = f'{output_dir}{timestamp}/retrieved_data'
#         for i in ['annotation_surface', 'annotation_cyto', 'latest_ids']:
#             cache_file_dir = f'{cache_dir}/{i}.tsv'
#             self.assertTrue(os.path.exists(cache_file_dir), f'{i} is not saved')


#     def test_cache_with_local_files(self):
#         mass_data = '../data/mass_spec_data.tsv'
#         ctrl = '2'
#         rep = '3'
        
#         print('\n\n')
#         print(f'######### cache with local files  #########')
#         output_dir = f'{OUTPUT_DIR}/test_cache/with_local_files/'
#         cmd = f'python3 {EXE_DIR} {mass_data} {ctrl} {rep} -s {ANNO_SURFACE} -c {ANNO_CYTO} --ids {IDS} -o {output_dir} --cache'
#         os.system(cmd)

#          # check output 
#         timestamp = os.listdir(output_dir)[-1]
#         cache_dir = f'{output_dir}{timestamp}/retrieved_data'
#         for i in ['annotation_surface', 'annotation_cyto', 'latest_ids']:
#             cache_file_dir = f'{cache_dir}/{i}.tsv'
#             self.assertFalse(os.path.exists(cache_file_dir), f'{i} is saved')


    # test different tolerance, does not need to be run for every change
    # def test_tolerance(self):
    #     mass_data = '../data/mass_spec_data.tsv'
    #     ctrl = '2'
    #     rep = '3'
    #     for t in range(7):
    #         print('\n\n')
    #         print(f'######### Tolerance = {t}  #########')
    #         output_dir = f'{OUTPUT_DIR}/test_tolerance/tolerance={t}/'
    #         cmd = f'python3 {EXE_DIR} {mass_data} {ctrl} {rep} -t {t} -s {ANNO_SURFACE} -c {ANNO_CYTO} --ids {IDS} -o {output_dir}'
    #         os.system(cmd)
    

    # # test different formats, does not need to be run for every change
    # def test_format(self):
    #     mass_data = '../data/mass_spec_data.tsv'
    #     ctrl = '2'
    #     rep = '3'
    #     for f in ['png', 'jpg', 'jpeg', 'tif', 'tiff', 'svg', 'pdf']:
    #         print('\n\n')
    #         print(f'######### format = {f}  #########')
    #         output_dir = f'{OUTPUT_DIR}/test_format/format={f}/'
    #         cmd = f'python3 {EXE_DIR} {mass_data} {ctrl} {rep} -f {f} -s {ANNO_SURFACE} -c {ANNO_CYTO} --ids {IDS} -o {output_dir}'
    #         os.system(cmd)

    #         # check output 
    #         timestamp = os.listdir(output_dir)[-1]
    #         res_dir = f'{output_dir}{timestamp}/plots/'
    #         plot_list = os.listdir(res_dir)
    #         self.assertTrue(len(plot_list)>=13, f'The number of plots is less than 13 ({len(plot_list)})')
    #         random_plot = plot_list[-1]
    #         self.assertEqual(random_plot[-len(f):], f, f'Saved format ({random_plot[-len(f):]}) does not match input format ({f})')
    
    
# # test empty/1col/1row/total wrong mass data, does not need to be run for every change
    # def test_mass_spec_file(self):
    #     for f in ['mass_spec_data_allones.tsv','mass_spec_data_allmissing.tsv',
    #     'mass_spec_data_notnumber.tsv','mass_spec_data_1row.tsv',
    #     'mass_spec_data_empty_noheader.tsv', 'mass_spec_data_empty_withheader.tsv']:
    #         print('\n\n')
    #         print(f'#########  {f[:-4]}  #########')
    #         # execute peeling
    #         mass_data = f'./data/{f}'
    #         ctrl = '2'
    #         rep = '3'
    #         output_dir = f'{OUTPUT_DIR}/test_mass_spec_file/{f[:-4]}/'
    #         cmd = f'python3 {EXE_DIR} {mass_data} {ctrl} {rep} -s {ANNO_SURFACE} -c {ANNO_CYTO} --ids {IDS} -o {output_dir}'
    #         os.system(cmd)
    
    #     f = 'mass_spec_data_1col.tsv'
    #     print('\n\n')
    #     print(f'#########  {f[:-4]}  #########')
    #     mass_data = f'./data/{f}'
    #     ctrl = '1'
    #     rep = '1'
    #     output_dir = f'{OUTPUT_DIR}/test_mass_spec_file/{f[:-4]}/'
    #     cmd = f'python3 {EXE_DIR} {mass_data} {ctrl} {rep} -s {ANNO_SURFACE} -c {ANNO_CYTO} --ids {IDS} -o {output_dir}'
    #     os.system(cmd)


# # Tests below are testing cli args handling, don't need to be tested for every change 
    
    # def test_wrong_ctrl_or_rep(self):
    #     mass_data = '../data/mass_spec_data.tsv'
    #     for n in [-1, 0, 1.2, 5, 'a']:
    #         print('\n\n')
    #         print(f'######### ctrl = {n}  #########')            
    #         ctrl = str(n)
    #         rep = '3'
    #         output_dir = f'{OUTPUT_DIR}/test_wrong_ctrl/ctrl={n}/'
    #         cmd = f'python3 {EXE_DIR} {mass_data} {ctrl} {rep} -s {ANNO_SURFACE} -c {ANNO_CYTO} --ids {IDS} -o {output_dir}'
    #         os.system(cmd)

    #         print('\n\n')
    #         print(f'######### rep = {n}  #########')  
    #         ctrl = 2
    #         rep = n
    #         output_dir = f'{OUTPUT_DIR}/test_wrong_rep/rep={n}/'
    #         cmd = f'python3 {EXE_DIR} {mass_data} {ctrl} {rep} -s {ANNO_SURFACE} -c {ANNO_CYTO} --ids {IDS} -o {output_dir}'
    #         os.system(cmd)
    

    # def test_wrong_tolerance(self):
    #     mass_data = '../data/mass_spec_data.tsv'
    #     ctrl = '2'
    #     rep = '3'
    #     for t in [-1, 1.2, 8, 'a']:
    #         print('\n\n')
    #         print(f'######### Wrong Tolerance = {t}  #########')
    #         output_dir = f'{OUTPUT_DIR}/test_wrong_tolerance/tolerance={t}/'
    #         cmd = f'python3 {EXE_DIR} {mass_data} {ctrl} {rep} -t {t} -s {ANNO_SURFACE} -c {ANNO_CYTO} --ids {IDS} -o {output_dir}'
    #         os.system(cmd)
    

    # def test_wrong_panther(self):
    #     mass_data = '../data/mass_spec_data.tsv'
    #     ctrl = '2'
    #     rep = '3'
    #     for org in ['"Homo sapiens"', 'Mus']: # Homo sapiens is an existing org but not match the data, Mus is not an existing org
    #         print('\n\n')
    #         print(f'#########  Wrong panther Organism ({org}) #########')
    #         output_dir = f'{OUTPUT_DIR}/test_wrong_panther/{org}'
    #         cmd = f'python3 {EXE_DIR} {mass_data} {ctrl} {rep} -s {ANNO_SURFACE} -c {ANNO_CYTO} --ids {IDS} -p {org} -o {output_dir}'
    #         os.system(cmd)



if __name__ == '__main__':
    unittest.main()