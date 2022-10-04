# SurfaceProteinFinder


### Introduction
Place holder

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


### Reference
Place holder