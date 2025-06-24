# Guide to CELESTA

All credit goes to the Plevritis Lab for this wonderful library! For more details, see https://github.com/plevritis-lab/CELESTA.

## Testing `celesta` environment

See `README_celesta_env.md` for details on activating/setting up the `celesta` conda environment.

You can test this with:

```bash
source bash_scripts/set_up_conda.sh
conda activate celesta
```

And in R,
```R
library(CELESTA)
```

## CELESTA inputs

CELESTA requires two main inputs in CSV format: **prior marker information** and **imaging data**. 

### 1. Prior marker info

Contains a matrix of cell types (rows) by name, lineage level, and expected expression probability (0/1) per biomarker (columns).
    
Sometimes it is easier to visualize it as a flowchart first:

![image](img/prior_marker_info_flowchart.png)

This is how it translates into tabular form:

![image](img/prior_marker_info.png)
    
### 2. Imaging data

Contains X/Y coordinates and raw expression levels per marker. Each row should correspond to an individual cell.

![image](img/imaging_data.png)

### 3. Thresholds

CELESTA requires high and low marker expression probability thresholds for anchor and iteration cells. Default thresholds may be used at first, but tuning high thresholds is recommended.

## Running CELESTA step-by-step 

Clone the `CC_codeximaging` repo and navigate to `bash_scripts`. Note that whenever you run a bash script, there are arguments you will need to edit according to your needs.

### 1. Prepare inputs

* **Prior marker info**
    
    Prepare in a separate spreadsheet and save as CSV ([example spreadsheet](https://docs.google.com/spreadsheets/d/1xc_mcczZ0B0EAhWt6SpMEdjmpPlIWInAd9OLzNKNgkI/edit?usp=sharing)).

* **Imaging data**
    ```
    celesta_imaging_data_prep.sh
    ```
* **Thresholds**




### 2. Create CELESTA object
```
celesta_create_obj.sh
```

This will also output a CSV file of marker expression probability.

You will need to edit these arguments:

```bash
--project_title "cervical_10103_raw_arcsinh" \
--prior_marker_info "/gpfs/data/proteomics/home/yb2612/data/celesta/cervical/prior_marker_info_cervical.csv" \
--imaging_data "/gpfs/data/proteomics/home/yb2612/data/celesta/cervical/imaging_data_10103_raw.csv" \
--results_dir "/gpfs/data/proteomics/home/yb2612/results/celesta" \
--transform_type 1
```

* `project_title:` This will be the name of the subfolder containing all results, as well as the prefix for filenames.
* `prior_marker_info`: Path to prior marker info CSV.
* `imaging_data`: Path to imaging data CSV.
* `results_dir`: Path to directory where you want *all* of your CELESTA results to go. The script will automatically create a subfolder named after `project_title` here.

### 3. Plot expression probability
```
celesta_plot_exp_prob.sh
```

This will help you choose thresholds when assigning cell types.

You will need to edit these arguments:

```bash
--project_title "cervical_10103_raw_arcsinh" \
--results_dir "/gpfs/data/proteomics/home/yb2612/results/celesta"
```

* `project_title:` Use same value as in `celesta_create_obj.sh`. This should be the name of the subfolder containing all results.
* `results_dir`: Use same value as in `celesta_create_obj.sh`. This should be the parent directory of the `project_title` subdir.

<img src="img/plot_exp_prob.png" height="600"/>

### 4. Assign cell types
```
celesta_assign_cells.sh
```

You will need to edit these arguments:

```bash
--project_title "cervical_10103_raw_arcsinh" \
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

For `high_anchor` and `high_iter`, you can use this [example spreadsheet](https://docs.google.com/spreadsheets/d/1xc_mcczZ0B0EAhWt6SpMEdjmpPlIWInAd9OLzNKNgkI/edit?usp=sharing) to edit thresholds and output them into the correct format for CELESTA. 

![image](img/high_thresholds.png)

*Note: You can use this script to test a bunch of different thresholds. Output filenames will contain the full lists of `high_anchor` and `high_iter` thresholds.*

### 5. Plot results
```
celesta_plot_results.sh
```
This script generates a stacked bar plot of cell type proportions and a spatial plot of cell type assignments *for each* `final_cell_type_assignment.csv` file generated by the previous step. 
```
celesta_plot_interactive_assignments.sh
```
This script generates interactive spatial plots of cell type assignments.

For both scripts, you will need to edit these arguments:

```bash
--project_title "cervical_10103_raw_arcsinh" \
--results_dir "/gpfs/data/proteomics/home/yb2612/results/celesta"
```

* `project_title:` Use same value as in `celesta_create_obj.sh`. This should be the name of the subfolder containing all results.
* `results_dir`: Use same value as in `celesta_create_obj.sh`. This should be the parent directory of the `project_title` subdir.

Example plots: 

<p>
  <img src="img/plot_cell_proportions.png" alt="Cell Proportions" height="600" style="vertical-align: top;"/>
  <img src="img/plot_cell_assignments.png" alt="Cell Assignments" height="600" style="vertical-align: top;"/>
</p>

### 6. Upload results to OMERO.
```
celesta_to_omero_prep.sh
```

```
main_celltype_tables.sh
```

All CELESTA results should be uploaded to OMERO (https://omero.nyumc.org/) after completion. This will allow you to use the PathViewer tool to overlay assigned cell types onto the CODEX image and visually evaluate how well they overlap with marker expression. To upload results, follow these steps:

1. Open [notebooks/celesta_data_prep_cervical.ipynb](https://github.com/lp2700/CC_codeximaging/blob/feature/celesta_phenotyping/notebooks/celesta_data_prep_cervical.ipynb) and run the code blocks under "Upload cell types to OMERO". Adjust file names and paths as necessary.
2. Open `config/config_cellsegmentation.yaml` and set `celltypes_table_name` to the file name of the cell types table you exported in the previous step.
3. Create a `.env` file in `bash_scripts` directory. Enter your PASSWORD and KERBEROSID.
4. Run `main_celltype_tables.sh`.
5. The tables should now appear on OMERO.

## Running full native CELESTA pipeline (not recommended)
*Note: While this is the simplest option, it is not recommended. It entails building the object from scratch, and only one set of thresholds can be tested at a time. Plots outputted by CELESTA are also not easily customizable.*

```
celesta_full_pipeline.sh
```

This creates a CELESTA object, assigns cells, plots expression probability, and plots cell assignments using built-in CELESTA functions. 

You will need to edit these arguments:

```bash
--project_title "cervical_10103_raw_arcsinh" \
--prior_marker_info "/gpfs/data/proteomics/home/yb2612/data/celesta/cervical/prior_marker_info_cervical.csv" \
--imaging_data "/gpfs/data/proteomics/home/yb2612/data/celesta/cervical/imaging_data_10103_raw.csv" \
--results_dir "/gpfs/data/proteomics/home/yb2612/results/celesta" \
--transform_type 1 \
--high_anchor 0.9 0.9 0.9 0.9 0.9 0.9 0.9 0.9 0.9 0.9 \
--high_iter 0.8 0.8 0.8 0.8 0.8 0.8 0.8 0.8 0.8 0.8 \
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

## CELESTA outputs

Outputs will be saved to `results_dir/project_title/` as specified in the bash script.

1. `celesta_full_pipeline.sh` outputs:
    * CELESTA object without cell type assignments (RDS)
    * CELESTA object with cell type assignments (RDS)
    * Final cell assignments (CSV)
    * Cell assignment plot (PNG)
    * Marker expression probability plots (PNG)

2. `celesta_create_obj.sh` outputs:
    * CELESTA object without cell type assignments (RDS)
    * Marker expression probability (CSV)

3. `celesta_create_obj.sh` outputs:
    * Marker expression probability plots (PNG)

4. `celesta_assign_cells.sh` outputs:
    * CELESTA object with cell type assignments (RDS)
    * Final cell assignments (CSV)

5. `celesta_plot_results.sh` outputs:
    * Cell type proportions stacked bar plot for each `final_cell_type_assignment.csv` file (PNG)
    * Spatial plot of cell type assignments for each `final_cell_type_assignment.csv` file (PNG)

6. `celesta_plot_interactive_assignments.sh` outputs:
    * Interactive spatial plot of cell type assignments for each `final_cell_type_assignment.csv` file (HTML)

## Evaluating CELESTA performance

### Computational evaluation with Jupyter notebook
You can also evaluate CELESTA results using `notebooks/celesta_evaluate_results_cervical.ipynb`. This contains the following code blocks:

* **arcsinh_exp_prob:** Plots expression probability, in the same way that `celesta_plot_exp_prob.sh` does. This is so you can see all plots at once, which can help when selecting thresholds. 

* **Violin plots and Spatial plots:** For visual comparison of raw biomarker means and marker expression probability.

* **Threshold search (mean of conf matrix diagonal):** If you have ground truth labels, you can evaluate threshold performance using the mean of the diagonal of the confusion matrix. This is best for making sure CELESTA has balanced performance across all classes. Make sure you have run `celesta_assign_cells.sh` with all of the different thresholds you want to test. 

* **Best thresholds - full evaluation.** This takes results from the chosen best thresholds and displays the following:

    * Plots showing accuracy for selected cell types
    * Classification report and graph of precision/recall/f1-score per cell type and overall
    * Confusion matrix
    * Plot of cell type proportions from  manual pipeline vs. CELESTA
    * Spatial plot of cell type assignments

There is also a notebook `notebooks/celesta_broad_vs_detailed_cervical.ipynb` to compare results from broad cell types to detailed cell types.

# Notes

1. I first ran CELESTA on two endometrial cancer samples: 1T (22k cells) and 3P (1M cells). 
    * For the imaging data, I used raw biomarker means with no further transformation. 
    * Both samples had manual annotations, which were treated as ground truth labels. 
    * I tested multiple thresholds and used `notebooks/celesta_evaluate_results_cervical.ipynb` to select the best thresholds (see "Evaluating CELESTA performance" section above).
3. I then ran the full CELESTA pipeline on all 14 cervical cancer samples. 
    * For the imaging data, I used raw biomarker means with CELESTA's built-in arcsinh transformation. 
    * Initially, default thresholds were used for all samples.
    * Thresholds will be tuned as described in the "Evaluating CELESTA performance" section above.
    * Three samples (10103, 34933, and 29973) had manual annotations, which were used for evaluation.
