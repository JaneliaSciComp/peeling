# PEELing


### Introduction
In the evolutionary transition from unicellular to multicellular organisms, single cells assemble into highly organized tissues and cooperatively carry out physiological functions. To act as an integrated system, individual cells communicate with each other extensively through signaling at the cellular interface. Cell-surface signaling thus controls almost every aspect of the development, physiology, and pathogenesis of multicellular organisms. In situ cell-surface proteomics or `iPEEL` (in situ cell-surface proteome extraction by extracellular labeling; developed by [Li, Han et al., 2020](https://pubmed.ncbi.nlm.nih.gov/31955847/) — `PMID: 31955847` and [Shuster, Li et al., 2022](https://pubmed.ncbi.nlm.nih.gov/36220098/) — `PMID: 36220098`) provides a method for quantitatively profiling cell-surface proteomes in native tissues with cell-type and spatiotemporal specificities. 

This program (`PEELing`) provides an automated, standardized, and easy-to-use analysis pipeline for `iPEEL` or any other cell-surface proteomics data. `PEELing` evaluates data quality using curated UniProt references, performs cut-off analysis to remove contaminants, and generates data visualizations. Together with `iPEEL` transgenic tools (The Jackson Laboratory: 037697, 037698; Bloomington Drosophila Stock Center: 8763, 9906, 9908), PEELing enables a complete pipeline, from wet lab method to data analysis, for in situ cell-surface proteomics.

### Installation
Place Holder

### Basic Usage
```
python3 main.py mass_spec_dir num_of_nonlabelled_controls num_of_labelled_replicates
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
The basic usage will communicate with the UniProt website to map the IDs to the latest version, and get the annotation data of surface proteins (TP) and introcellular proteins (FP). As of our testing, it will take dozens of seconds to minutes for the process. 

Therefore, it is recommended to save the retrieved data when first time run it, and use the locally saved data for the following runs, which will reduce the run time to seconds. You can also provide your own annotation files. If the local annotation files are from Uniprot (saved by using -c/--cache), there is no need to do id mapping for them. To disable id mapping for local annotation files specify -n/--nomap. Remember to update the retrieved data periodically.
```
# To save the retrieved data, specify -a/--cache
python3 main.py mass_spec_dir num_of_nonlabelled_controls num_of_labelled_replicates --cache

# To use locally saved data, specify the directories
python3 main.py mass_spec_dir num_of_nonlabelled_controls num_of_labelled_replicates --ids latest_ids_dir --surface annotation_surface_dir --cyto annotation_cyto_dir --nomap
```

### Options
-h, --help    Show help message and exit

-t, --tolerance    Tolerance of non-included ratios ratio, default is 0. (For example, in an experiment with 2 non-labelled controls and 3 labelled replicates, there are 6 replicate-to-control ratios. In the default algorithm, a protein must pass cutoff in all 6 ratios to be included in the final proteome. If the tolerance is set to 1, a protein is included in the final proteome if it passes cutoff in any 5 ratios. If the tolerance is set to 2, a protein is included in the final proteome if it passes cutoff in any 4 ratios.) 

-o, --output    Directory to store output results, default is the current work directory

-i, --ids    Latest_ids file directory including filename, e.g. data/id_mapping.tsv

-s, --surface    Annotation_surface file directory including filename, e.g. data/annotation_surface.tsv

-c, --cyto    Annotation_cyto file directory including filename, e.g. data/annotation_cyto.tsv

-a, --cache    Save the data retrieved from UniProt on the local computer, true if specified

-p, --plot    The format of the output plots, default is png. Supported formats depend on the computation platform, use -h/--help to see supported formats

-n, --nomap    No id mapping for local annotation files, true if specified
