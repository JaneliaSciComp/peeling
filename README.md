# PEELing


### Introduction
Molecular compartmentalization is vital for cellular physiology. Spatially-resolved proteomics allows biologists to survey protein composition and dynamics with subcellular resolution. Here, we present **PEELing** (***p***roteome ***e***xtraction from ***e***nzymatic ***l***abel***ing*** data), an integrated package and user-friendly web service for analyzing spatially-resolved proteomics data. PEELing assesses data quality using curated or user-defined references, performs cutoff analysis to remove contaminants, connects to databases for functional annotation, and generates data visualizations—providing a streamlined and reproducible workflow to explore spatially-resolved proteomics data.

`PEELing` also provides a web portal. Please refer to [link](http://peeling.janelia.org)



### Citation
Manuscript preprint: [https://www.biorxiv.org/content/10.1101/2023.04.21.537871](https://www.biorxiv.org/content/10.1101/2023.04.21.537871)

Please note that this bioRxiv preprint will be updated as we add new functionalities to PEELing.



### Installation
```
pip install peeling
```


### Basic Usage
```
peeling mass_spec_dir num_of_nonlabelled_controls num_of_labelled_replicates
```


#### Required Arguments
The order of the three required arguments should NOT be changed.
1. Mass Spec Data:    Mass spec data directory, e.g. data/mass_spec_data.tsv. Tab-delimited (.tsv). The first column should contain UniProt IDs. The rest columns should contain ratios (or fold changes) of labelled samples over non-labelled controls. The columns should be ordered as in example below.
2. Number of Non-labelled Controls:    The number of non-labelled controls
3. Number of Labelled Replicates:    The number of labelled replicates

##### Mass Spec Data Example (e.g., 2 non-labelled controls and 3 labelled replicates)
| UniProt_IDs  | Ratio_Labelled-Rep1_Over_Ctrl1 | Ratio_Labelled-Rep2_Over_Ctrl1 | Ratio_Labelled-Rep3_Over_Ctrl1 | Ratio_Labelled-Rep1_Over_Ctrl2 | Ratio_Labelled-Rep2_Over_Ctrl2 | Ratio_Labelled-Rep3_Over_Ctrl2 |
| ------------ | ------------------------------ | ------------------------------ | ------------------------------ | ------------------------------ | ------------------------------ | ------------------------------ |
| Content Cell |          Content Cell          |          Content Cell          |          Content Cell          |          Content Cell          |          Content Cell          |          Content Cell          |
| Content Cell |          Content Cell          |          Content Cell          |          Content Cell          |          Content Cell          |          Content Cell          |          Content Cell          |

#### Note
The basic usage will communicate with the UniProt website to map the provided IDs to their latest version, and get the annotation data of true positive proteins (TP) and false positive proteins (FP). Our testing shows that this can take dozens of seconds or minutes to complete.

Therefore, it is recommended to save the retrieved data after the first run, and use the locally saved data for the following runs, which will reduce the run time to seconds. If using local annotation files, PEELing does id mapping by default. To disable id mapping for local annotation files specify -n/--nomap. Note: Remember to update the retrieved data periodically.
```
# To save the retrieved data, specify -a/--cache
peeling mass_spec_dir num_of_nonlabelled_controls num_of_labelled_replicates --cache

# To use locally saved data, specify the directories
peeling mass_spec_dir num_of_nonlabelled_controls num_of_labelled_replicates --ids latest_ids_dir --tp annotation_true_positive_dir --fp annotation_false_positive_dir --nomap
```


### Panther analysis
PEELing provides the functionality to perform protein ontology and pathway analyses of the post-cutoff proteome using the [Panther](http://www.pantherdb.org/) API. Top 10 terms based on false discovery rate (FDR) are listed for protein localization (Panther GO Slim Cellular Component), function (Panther GO Slim Biological Process), and pathway (Reactome).

To run this analysis, specify `-p/--panther` and provide the organism from which the mass spec data is made. Please refer to Panther's API [page](http://pantherdb.org/services/oai/pantherdb/supportedgenomes) for supported organism. Choose the corresponding 'long_names', and wrap it by quotes if there is white space inside the name, e.g. 'Homo sapiens'
```
peeling mass_spec_dir num_of_nonlabelled_controls num_of_labelled_replicates -p organism
```


### Options
-h, --help    Show help message and exit

-t, --tolerance    Tolerance of non-included ratios ratio, default is 0. (For example, in an experiment with 2 non-labelled controls and 3 labelled replicates, there are 6 replicate-to-control ratios. In the default algorithm, a protein must pass cutoff in all 6 ratios to be included in the final proteome. If the tolerance is set to 1, a protein is included in the final proteome if it passes cutoff in any 5 ratios. If the tolerance is set to 2, a protein is included in the final proteome if it passes cutoff in any 4 ratios.) 

-o, --output    Directory to store output results, default is the current work directory

-i, --ids    Latest_ids file directory including filename, e.g. data/id_mapping.tsv

--tp, --true-positive   path to true positive annotation file, e.g. data/annotation_true_positive.tsv

--fp, --false-positive  path to false positive annotation file, e.g. data/annotation_false_positive.tsv

-a, --cache    Save the data retrieved from UniProt on the local computer, true if specified

-f, --format    The format of the output plots, default is png. Supported formats depend on the computation platform, use -h/--help to see supported formats

-n, --nomap    No id mapping for local annotation files, true if specified

-p, --panther    The organism from which the mass spec data is made, a required input for Panther enrichment analysis. Please refer to Panther's API page http://pantherdb.org/services/oai/pantherdb/supportedgenomes for supported organism. Choose the corresponding 'long_names', and wrap it by quotes, e.g. 'Homo sapiens'

--cc, --cellular_compartment    Choose between: cs - cell surface [default], mt - mitochondria, nu - nucleus or ot - other. If other is chosen, the true positive (--tp) and false positive (--fp) files must be specified

-v --verbose    Enables verbose debugging output
