# Guide to CELESTA

*All credit for CELESTA goes to the Plevritis Lab. For more details, see https://github.com/plevritis-lab/CELESTA.*

This is a guide to running CELESTA as an integrated part of the `CC_codeximaging` pipeline.

## Contents

1. CELESTA inputs

2. Instructions for running full workflow
    
    a. Prepare inputs

    b. Run CELESTA pipeline (or individual steps)
    
    c. Summary of outputs for CELESTA pipeline

    c. Prepare OMERO tables

    d. Upload to OMERO

3. Details on individual steps

4. Evaluating CELESTA performance

# CELESTA inputs

CELESTA requires two main inputs: a prior marker info matrix and an imaging data matrix. Refer to the [CELESTA GitHub](https://github.com/plevritis-lab/CELESTA?tab=readme-ov-file#inputs) for more detailed information.

### A. Prior marker info

Matrix of cell types (rows) by name, lineage level, and expected expression probability per marker (columns). Sometimes it is easier to visualize as a flowchart:

![image](img/prior_marker_info_flowchart.png)

This is how it translates into tabular form:

![image](img/prior_marker_info.png)

### B. Imaging data

Contains X/Y coordinates and raw expression levels per marker. Each row should correspond to an individual cell.

![image](img/imaging_data.png)

# Instructions for running full workflow

Before you begin, make sure you have done the following:

* Clone the `CC_codeximaging` repo and navigate to `bash_scripts`. You will have to run all scripts from within this directory for the relative paths to work.
* Have a working `celesta` environment (see `README_celesta_env.md` for details on setting up and activating the conda environment).

## Step 1: Prepare inputs

### A. Prior marker info
Prepare in a separate spreadsheet and save as CSV ([example spreadsheet](https://docs.google.com/spreadsheets/d/1xc_mcczZ0B0EAhWt6SpMEdjmpPlIWInAd9OLzNKNgkI/edit?usp=sharing)). Under each marker column, enter 0 for low expression probability, 1 for high expression probability, and NA if the marker is irrelevant for the given cell type.
    
### B. Imaging data
```
sbatch celesta_imaging_data_prep.sh
```
* You can directly edit `celesta_imaging_data_prep.py` to specify the following:
    * `markers`: list of markers to include
    * `metadata_dir`: directory containing metadata files used to construct imaging data (the script will loop over all subfolders here)
    * `imaging_data_dir`: directory to output all imaging data files
* Imaging data files will be named `imaging_data_{sample}.csv`.

### C. Configuration file

Edit this file in `CC_codeximaging/configs/`:
```
config_celesta_pipeline.yaml
```
This file determines all parameters to be used when running the full pipeline. Below are the parameters to edit:
* `paths`:
    * `prior_marker_info`: Path to prior marker info CSV.
    * `imaging_data`: Path to imaging data directory (should contain files named `imaging_data_{sample}.csv` for all samples).
    * `results_dir`: Path to directory where you want all CELESTA results to go.

* `project_title_prefix`: Used to construct a project title for each sample, i.e., `{project_title_prefix}_{sample}`. A subfolder with this name will be made for each sample in `results_dir`.
* `transform_type`: 1 for arcsinh normalization (recommended), 0 for no normalization.
* `thresholds:`
    * `high_anchor`: Series of comma-separated thresholds for high expression probability in anchor cells, in order of cell types listed in prior marker info CSV. Can leave blank for CELESTA defaults (0.7 for all cell types).*
    * `high_iter`: Same as above, but for iteration cells. Default is 0.5 for all cell types.*
    * `low_anchor`: Same as above, but defines low expression probability for anchor cells. Default is 0.9 for all cell types.*
    * `low_iter`: Same as above, but for iteration cells. Default is 1 for all cell types.*

## Step 2a: Run CELESTA pipeline (or individual steps)

To run the CELESTA pipeline for each sample in parallel:
```
source main_celesta_run_full_pipeline.sh
```
* Edit the sample list and log directory as desired.

The pipeline consists of the following steps:

1. `celesta_create_obj.sh`
2. `celesta_plot_exp_prob.sh`
3. `celesta_assign_cells.sh`
4. `celesta_plot_results.sh`
5. `celesta_plot_interactive_assignments.sh`

See section "Details on individual steps" for more information.

To run an individual step from the pipeline for each sample in parallel:
```
source main_celesta_run_individual_step.sh
```
* Edit the sample list and log directory as desired.
* Input the individual step to run as `script_name`.

It is recommended to first run the CELESTA pipeline using default thresholds. Afterwards, tune thresholds by running `celesta_assign_cells` as an individual step with many different threshold configurations.

## Step 2b: Summary of outputs for CELESTA pipeline

Outputs will be saved to `results_dir/project_title/` as specified in `config_celesta_pipeline.yaml`.

1. `celesta_create_obj.sh` outputs:
    * CELESTA object without cell type assignments (RDS)
    * Marker expression probability (CSV)

2. `celesta_create_obj.sh` outputs:
    * Marker expression probability plots (PNG)

3. `celesta_assign_cells.sh` outputs:
    * CELESTA object with cell type assignments (RDS)
    * Final cell assignments (CSV)

4. `celesta_plot_results.sh` outputs:
    * Cell type proportions stacked bar plot for each `final_cell_type_assignment.csv` file (PNG)
    * Spatial plot of cell type assignments for each `final_cell_type_assignment.csv` file (PNG)

5. `celesta_plot_interactive_assignments.sh` outputs:
    * Interactive spatial plot of cell type assignments for each `final_cell_type_assignment.csv` file (HTML)

## Step 3: Prepare OMERO tables

Edit this file in `CC_codeximaging/configs/`:
```
config_celesta_to_omero.yaml
```
* `paths`:
    * `phenotype_clusters`: Path to CSV containing phenotype clusters, with all cells in the correct order for uploading.
    * `celesta_results_dir`: Path to directory where all CELESTA results are located.
    * `output_dir`: Path to directory where you want OMERO tables to go.
* `thresholds_dict`
* `tables_to_upload`: Names of tables (keys from `thresholds_dict`) to be uploaded to OMERO.

Then run:
```
sbatch celesta_to_omero_prep.sh
```

## Step 4: Upload to OMERO

Create a `.env` file in `CC_codeximaging/bash_scripts/` containing your `PASSWORD` and `KERBEROSID`. You may also have to add these environment variables to your `~/.bashrc` for this to work.

Then run:

```
sbatch main_celltype_tables.sh
```
* Uploads all tables specified in `tables_to_upload` above.

# Details on individual steps

## 1. Create CELESTA object

Outputs a CELESTA RDS object along with a CSV file of marker expression probability.

## 2. Plot expression probability

Outputs expression probability plots for each sample that will help you choose thresholds when assigning cell types.

<img src="img/plot_exp_prob.png" height="600"/>

## 3. Assign cell types
Outputs an updated CELESTA RDS object with cell type assignments along with a CSV file. Output filenames will contain the full lists of `high_anchor` and `high_iter` thresholds, so results from every unique run will be saved.

### Note on choosing thresholds
CELESTA requires high and low marker expression probability thresholds for anchor and iteration cells. Default thresholds may be used at first, but tuning high thresholds is recommended. Low thresholds typically do not need to be tuned.

For `high_anchor` and `high_iter`, you can use this [example spreadsheet](https://docs.google.com/spreadsheets/d/1xc_mcczZ0B0EAhWt6SpMEdjmpPlIWInAd9OLzNKNgkI/edit?usp=sharing) to edit thresholds and output them into the correct format for CELESTA. 

![image](img/high_thresholds.png)

## 4. Plot results
*Generates stacked bar plots of cell type proportions and static/interactive spatial plots of cell type assignments for each `final_cell_type_assignment.csv` file generated by the previous step.*

Example plots: 

<p>
  <img src="img/plot_cell_proportions.png" alt="Cell Proportions" height="600" style="vertical-align: top;"/>
  <img src="img/plot_cell_assignments.png" alt="Cell Assignments" height="600" style="vertical-align: top;"/>
</p>

# Evaluating CELESTA performance

You can evaluate CELESTA results using `notebooks/celesta_evaluate_results_cervical.ipynb`. This contains the following code blocks:

* **Violin plots:** For visual comparison of raw biomarker means and marker expression probability.

* **Threshold search (mean of conf matrix diagonal):** If you have ground truth labels, you can evaluate threshold performance using the mean of the diagonal of the confusion matrix. This is best for making sure CELESTA has balanced performance across all classes. Make sure you have run `celesta_assign_cells.sh` with all of the different thresholds you want to test. 

* **Best thresholds - full evaluation.** This takes results from the chosen best thresholds and displays the following:

    * Plots showing accuracy for selected cell types
    * Classification report and graph of precision/recall/f1-score per cell type and overall
    * Confusion matrix
    * Plot of cell type proportions from  manual pipeline vs. CELESTA
    * Spatial plot of cell type assignments