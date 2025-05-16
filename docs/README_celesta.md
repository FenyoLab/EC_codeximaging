# Guide to CELESTA

All credit goes to the Plevritis Lab for this wonderful library! For more details, see https://github.com/plevritis-lab/CELESTA.

## Testing `celesta` environment

See `README_celesta_env.md` for details on activating/setting up the `celesta` conda environment. Hopefully the one I've created on the shared lab miniconda works for everyone.

You can test this with:

```bash
source bash_scripts/set_up_conda.sh
conda activate celesta
```

And in R,
```R
library(CELESTA)
```

## Preparing CELESTA inputs

CELESTA requires two main inputs in CSV format: **prior marker information** ([example spreadsheet](https://docs.google.com/spreadsheets/d/1xc_mcczZ0B0EAhWt6SpMEdjmpPlIWInAd9OLzNKNgkI/edit?usp=sharing)) and **imaging data** (`notebooks/celesta_data_prep.ipynb`). 

1. **Prior marker info (CSV):** Contains cell type name, lineage levels, and marker expression probability 0/1 per cell type. Each row should correspond to a cell type.
    
    Sometimes it is easier to visualize it as a flowchart first:

    ![image](img/prior_marker_info_flowchart.png)

    This is how it translates into tabular form:

    ![image](img/prior_marker_info.png)
    
2. **Imaging data (CSV):** Contains X/Y coordinates and "raw" expression levels per marker (you can input normalized expression here too). Each row should correspond to an individual cell.

    ![image](img/imaging_data.png)

Aside from these, you will also need to input high and low marker expression probability thresholds for anchor and iteration cells. Low thresholds can be set to 1 for all cells, but high thresholds need to be tuned. 

This [example spreadsheet](https://docs.google.com/spreadsheets/d/1xc_mcczZ0B0EAhWt6SpMEdjmpPlIWInAd9OLzNKNgkI/edit?usp=sharing) also contains a sheet where you can easily edit thresholds per cell type and output it into a format that CELESTA will accept:

![image](img/high_thresholds.png)

## Running CELESTA

Clone the `CC_codeximaging` repo and navigate to `bash_scripts`. Note that whenever you run a bash script, there are arguments you will need to edit according to your needs.

You have two options when running CELESTA:

### A. *(Recommended)* **Run steps separately** 
This gives you more control over each step. It also allows you to test a bunch of thresholds on an existing CELESTA object rather than having to build the object from scratch every time.

#### 1. First run `celesta_create_obj.sh` to create a CELESTA object.

This will also output a CSV file of marker expression probability.

You will need to edit these arguments:

```bash
--project_title "endometrial_1T_raw_noarcsinh" \
--prior_marker_info "/gpfs/data/proteomics/home/yb2612/data/celesta/endometrial_test/prior_marker_info_endometrial_noDAPI.csv" \
--imaging_data "/gpfs/data/proteomics/home/yb2612/data/celesta/endometrial_test/imaging_data_1T_raw_noDAPI.csv" \
--results_dir "/gpfs/data/proteomics/home/yb2612/results/celesta" \
--transform_type 0 \
```

* `project_title:` This will be the name of the subfolder containing all results, as well as the prefix for filenames.
* `prior_marker_info`: Path to prior marker info CSV.
* `imaging_data`: Path to imaging data CSV.
* `results_dir`: Path to directory where you want *all* of your CELESTA results to go. The script will automatically create a subfolder named after `project_title` here.

#### 2. After the CELESTA object is created, run `celesta_plot_exp_prob.sh` to plot expression probability for each marker.

This will help you choose thresholds when assigning cell types.

You will need to edit these arguments:

```bash
--project_title "endometrial_1T_raw_noarcsinh" \
--results_dir "/gpfs/data/proteomics/home/yb2612/results/celesta" \
```

* `project_title:` Use same value as in `celesta_create_obj.sh`. This should be the name of the subfolder containing all results.
* `results_dir`: Use same value as in `celesta_create_obj.sh`. This should be the parent directory of the `project_title` subdir.

I've made my own script to plot expression probability because I think it looks better than CELESTA's plots. Case in point:

![image](img/celesta_CD3e_exp_prob.png)
*CELESTA's expression probability plot for CD3e in one of our samples. From this it looks like most cells are <=0.5, but in truth they are just plotted on top of cells with higher probability. This plot can mislead us into setting a threshold that is too low for this marker.*

![image](img/yumi_CD3e_exp_prob.png)
*Yumi's expression probability plot for the same marker and sample. I make sure to plot cells in order of increasing probability. Notice how this reveals many more cells >0.9, which helps us set a better threshold.*

#### 3. After choosing thresholds, run `celesta_assign_cells.sh` to assign cell types.

You will need to edit these arguments:

```bash
--project_title "endometrial_1T_raw_noarcsinh" \
--results_dir "/gpfs/data/proteomics/home/yb2612/results/celesta" \
--high_anchor 0.9 0.9 0.9 0.9 0.9 0.9 0.9 0.9 0.9 0.9 \
--high_iter 0.8 0.8 0.8 0.8 0.8 0.8 0.8 0.8 0.8 0.8 \
--low_anchor 1 1 1 1 1 1 1 1 1 1 \
--low_iter 1 1 1 1 1 1 1 1 1 1
```

* `project_title:` Use same value as in `celesta_create_obj.sh`. This should be the name of the subfolder containing all results.
* `results_dir`: Use same value as in `celesta_create_obj.sh`. This should be the parent directory of the `project_title` subdir.
* `high_anchor`: Series of space-separated thresholds for high expression probability in anchor cells, in order of cell types listed in `prior_marker_info`. Can leave blank for CELESTA defaults (0.7 for all cell types).
* `high_iter`: Same as above, but for iteration cells. Default is 0.5 for all cell types.
* `low_anchor`: Same as above, but defines low expression probability for anchor cells. Default is 0.9 for all cell types.
* `low_iter`: Same as above, but for iteration cells. Default is 1 for all cell types.

For `high_anchor` and `high_iter`, you can use this [example spreadsheet](https://docs.google.com/spreadsheets/d/1xc_mcczZ0B0EAhWt6SpMEdjmpPlIWInAd9OLzNKNgkI/edit?usp=sharing) to edit thresholds and output them into the correct format for CELESTA. You can use this script to test a bunch of different thresholds, and all results will be saved with a unique filename.

*Note: Output filenames will contain the full lists of `high_anchor` and `high_iter` thresholds. There is probably a better way to do this, but this is how it is for now.*

### B. Run the full pipeline with `celesta_full_pipeline.sh`
This creates a CELESTA object, assigns cells, plots expression probability, and plots cell assignments using built-in CELESTA functions. 

*Note: While this is the simplest option, it isn't the fastest. It entails building the object from scratch, and only one set of thresholds can be tested at a time. Furthermore, the plots outputted by CELESTA don't always look the best.*

You will need to edit these arguments:

```bash
--project_title "endometrial_1T_raw_noarcsinh" \
--prior_marker_info "/gpfs/data/proteomics/home/yb2612/data/celesta/endometrial_test/prior_marker_info_endometrial_noDAPI.csv" \
--imaging_data "/gpfs/data/proteomics/home/yb2612/data/celesta/endometrial_test/imaging_data_1T_raw_noDAPI.csv" \
--results_dir "/gpfs/data/proteomics/home/yb2612/results/celesta" \
--transform_type 0 \
--high_anchor 1 0.8 0.9 0.7 0.7 0.7 0.7 0.5 0.5 0.8 \
--high_iter 1 0.7 0.8 0.6 0.6 0.6 0.6 0.5 0.5 0.7 \
--low_anchor 1 1 1 1 1 1 1 1 1 1 \
--low_iter 1 1 1 1 1 1 1 1 1 1
```

* `project_title:` This will be the name of the subfolder containing all results, as well as the prefix for filenames.
* `prior_marker_info`: Path to prior marker info CSV.
* `imaging_data`: Path to imaging data CSV.
* `results_dir`: Path to directory where you want *all* of your CELESTA results to go. The script will automatically create a subfolder named after `project_title` here.
* `high_anchor`: Series of space-separated expression thresholds for anchor cells, in order of cell types listed in `prior_marker_info`. Can leave blank for CELESTA defaults (0.7 for all cell types).
* `high_iter`: Series of space-separated expression thresholds for iteration cells, in order of cell types listed in `prior_marker_info`. Can leave blank for CELESTA defaults (0.5 for all cell types).
* `low_anchor`: Series of space-separated expression thresholds for anchor cells, in order of cell types listed in `prior_marker_info`. Can leave blank for CELESTA defaults (0.9 for all cell types).
* `low_iter`: Series of space-separated expression thresholds for anchor cells, in order of cell types listed in `prior_marker_info`. Can leave blank for CELESTA defaults (1 for all cell types).

### Inspecting CELESTA results

Results will be saved to `results_dir/project_title/` as specified in the bash script you ran (any in the above section).

1. `celesta_full_pipeline.sh` outputs:
    * CELESTA object without cell type assignments (RDS)
    * CELESTA object with cell type assignments (RDS)
    * Final cell assignments (CSV)
    * Cell assignment plot
    * Marker expression probability plots

2. `celesta_create_obj.sh` outputs:
    * CELESTA object without cell type assignments (RDS)
    * Marker expression probability (CSV)

3. `celesta_create_obj.sh` outputs:
    * Marker expression probability plots

4. `celesta_assign_cells.sh` outputs:
    * CELESTA object with cell type assignments (RDS)
    * Final cell assignments (CSV)

## Evaluating CELESTA performance

You can evaluate CELESTA results using `notebooks/celesta_evaluate_results.ipynb`. This will only work if you have ground truth labels, i.e., from the manual cell phenotyping pipeline. 

There are code blocks dedicated to plotting expression probability, in the same way that `celesta_plot_exp_prob.sh` does. This is just so you can see all plots at once, which can help when selecting thresholds.

I have also developed a rudimentary way of selecting the best thresholds. First run `celesta_assign_cells.sh` with all of the different thresholds you want to test. Then in the notebook, run the code blocks under:

* **Threshold search (mean of conf matrix diagonal):** Here our evaluation metric is the mean of the diagonal of the confusion matrix (with the option to exclude certain cell types). It is not weighted based on cell number. This is probably best for making sure CELESTA has balanced performance across all classes.
* **Threshold search (macro F1):** Here we use the macro F1 score (harmonic mean of precision and recall) as an alternative evaluation metric. I find this tends to favor better performance in more common cell types.

You will also see code blocks named **Best thresholds - full evaluation.** This takes results from the chosen best thresholds and displays the following:

* Spatial plot of cell type assignments
* Plots showing accuracy for selected cell types
* Classification report and graph of precision/recall/f1-score per cell type and overall
* Confusion matrix
* Plot of cell type proportions from  manual pipeline vs. CELESTA
