# PEELing


### Introduction
In the evolutionary transition from unicellular to multicellular organisms, single cells assemble into highly organized tissues and cooperatively carry out physiological functions. To act as an integrated system, individual cells communicate with each other extensively through signaling at the cellular interface. Cell-surface signaling thus controls almost every aspect of the development, physiology, and pathogenesis of multicellular organisms. In situ cell-surface proteomics or `iPEEL` (in situ cell-surface proteome extraction by extracellular labeling; developed by [Li, Han et al., 2020](https://pubmed.ncbi.nlm.nih.gov/31955847/) — `PMID: 31955847` and [Shuster, Li et al., 2022](https://pubmed.ncbi.nlm.nih.gov/36220098/) — `PMID: 36220098`) provides a method for quantitatively profiling cell-surface proteomes in native tissues with cell-type and spatiotemporal specificities. 

This program (`PEELing`) provides an automated, standardized, and easy-to-use analysis pipeline for `iPEEL` or any other cell-surface proteomics data. `PEELing` evaluates data quality using curated UniProt references, performs cut-off analysis to remove contaminants, and generates data visualizations. Together with `iPEEL` transgenic tools (The Jackson Laboratory: 037697, 037699; Bloomington Drosophila Stock Center: 8763, 9906, 9908), PEELing enables a complete pipeline, from wet lab method to data analysis, for in situ cell-surface proteomics.

### Installation
Place Holder

### Basic Usage
```
python3 main.py mass_spec_dir num_of_controls num_of_replicates
```
#### Required Arguments
The order of the three required arguments should NOT be changed.
1. Mass Spec Data:    Tab-delimited (.tsv). The first column should contain UniProt IDs. The rest columns should contain ratios of experimental samples over controls. The columns should be ordered as in example below.
2. Number of Controls:    The number of controls for each condition
3. Number of Replicates:    The number of replicates for each control

##### Mass Spec Data Example
| UniProt_IDs  | Ratio_Condition1_Over_Ctrl1_Rep1 | Ratio_Condition1_Over_Ctrl1_Rep2 | Ratio_Condition1_Over_Ctrl2_Rep1 | Ratio_Condition1_Over_Ctrl2_Rep2 | Ratio_Condition2_... |
| ------------ | -------------------------------- | -------------------------------- | -------------------------------- | -------------------------------- | -------------------- |
| Content Cell |           Content Cell           |           Content Cell           |           Content Cell           |           Content Cell           |     Content Cell     |
| Content Cell |           Content Cell           |           Content Cell           |           Content Cell           |           Content Cell           |     Content Cell     |

#### Note
The basic usage will communicate with the UniProt website to map the IDs to the latest version, and get the annotation data of surface proteins (TP) and introcellular proteins (FP). As of our testing, it will take dozens of seconds to minutes for the process. 

Therefore, it is recommended to save the retrieved data when first time run it, and use the locally saved data for the following runs, which will reduce the run time to seconds. Remember to update the retrieved data periodically.
```
# To save the retrieved data, specify -s/--save
python3 main.py mass_spec_filename num_of_controls num_of_replicates --save

# To use locally saved data, specify the directories
python3 main.py mass_spec_filename num_of_controls num_of_replicates --ids latest_ids_dir --surface annotation_surface_dir --cyto annotation_cyto_dir
```

### Options
-h, --help    Show help message and exit

-t, --tolerance    Tolerance of non-included

-o, --output    Directory to store output results

-c, --conditions    Number of conditions

-i, --ids    Latest_ids file directory including filename

-u, --surface    Annotation_surface file directory including filename

-y, --cyto    Annotation_cyto file directory including filename

-s, --save    Save the data retrieved from UniProt, true if specified

