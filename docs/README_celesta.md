# Guide to CELESTA

See `README_celesta_env.md` for details on activating/setting up the `celesta` conda environment. If the environment exists and runs properly, you may proceed.

## Preparing CELESTA inputs

CELESTA requires the following:

1. **Prior marker info (CSV):** Contains cell type name, lineage levels, and marker expression probability 0/1 per cell type. Each row should correspond to a cell type.

2. **Imaging data (CSV):** Contains X/Y coordinates and "raw" expression levels per marker (you can input normalized expression here too). Each row should correspond to an individual cell.

You can prepare these inputs using `notebooks/celesta_data_prep.ipynb` (TODO: clean up this notebook!)

See https://github.com/plevritis-lab/CELESTA for more details.

## Running CELESTA

Clone the `CC_codeximaging` repo and navigate to `bash_scripts`. Note that whenever you run a bash script, there are arguments you will need to edit according to your needs.

You have two options when running CELESTA:

### A. *(Recommended)* **Run steps separately** 
This gives you more control over each step. Furthermore, this allows you to test a bunch of thresholds on an existing CELESTA object rather than having to build the object from scratch every time.

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
* `prior_marker_info`: Path to prior marker info CSV
* `imaging_data`: Path to imaging data CSV
* `results_dir`: Path to directory where you want *all* of your CELESTA results to go. The script will automatically create a subfolder named after `project_title` here.

#### 2. After the CELESTA object is created, run `celesta_plot_exp_prob.sh` to plot expression probability for each marker.

This will help you choose thresholds when assigning cell types. I've made my own script to plot expression probability because I think it looks better than CELESTA's plots.

You will need to edit these arguments:

```bash
--project_title "endometrial_1T_raw_noarcsinh" \
--results_dir "/gpfs/data/proteomics/home/yb2612/results/celesta" \
```

* `project_title:` Use same value as in `celesta_create_obj.sh`. This should be the name of the subfolder containing all results.
* `results_dir`: Use same value as in `celesta_create_obj.sh`. This should be the parent directory of the `project_title` subdir.

#### 3. After the CELESTA object is created, run `celesta_assign_cells.sh` to assign cell types at specified thresholds.

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
* `high_anchor`: Series of space-separated expression thresholds for anchor cells, in order of cell types listed in `prior_marker_info`. Can leave blank for CELESTA defaults (0.7 for all cell types).
* `high_iter`: Series of space-separated expression thresholds for iteration cells, in order of cell types listed in `prior_marker_info`. Can leave blank for CELESTA defaults (0.5 for all cell types).
* `low_anchor`: Series of space-separated expression thresholds for anchor cells, in order of cell types listed in `prior_marker_info`. Can leave blank for CELESTA defaults (0.9 for all cell types).
* `low_iter`: Series of space-separated expression thresholds for anchor cells, in order of cell types listed in `prior_marker_info`. Can leave blank for CELESTA defaults (1 for all cell types).

*Note: Output files will be saved with the full list of *

### B. Run the full pipeline with `celesta_full_pipeline.sh`
This creates a CELESTA object, assigns cells, plots expression probability, and plots cell assignments using built-in CELESTA functions. 

*Note: While this is the simplest option, this entails building an object from scratch and only one set of thresholds can be tested. Furthermore, the plots outputted by CELESTA don't always look the best.*

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

This will work if you have ground truth labels, i.e., from the manual cell phenotyping pipeline. 

Run `notebooks/celesta_evaluate_results.ipynb`. This generates the following:
* Spatial plots of expression probability per marker
* Spatial plot of cell type assignments
* Plots showing accuracy for selected cell types
* Classification report and graph of precision/recall/f1-score per cell type and overall
* Confusion matrix
* Plot of cell type proportions from  manual pipeline vs. CELESTA

