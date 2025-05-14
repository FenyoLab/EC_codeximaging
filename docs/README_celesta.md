# Guide to CELESTA

See `README_celesta_env.md` for details on activating/setting up the `celesta` conda environment. If the environment exists and runs properly, you may proceed.

## Preparing CELESTA inputs

CELESTA requires the following:

1. **Prior marker info (CSV):** Contains cell type name, lineage levels, and marker expression probability 0/1 per cell type. Each row should correspond to a cell type.

2. **Imaging data (CSV):** Contains X/Y coordinates and "raw" expression levels per marker (you can input normalized expression here too). Each row should correspond to an individual cell.

You can prepare these inputs using `notebooks/celesta_data_prep.ipynb` (TODO: clean up this notebook!)

See https://github.com/plevritis-lab/CELESTA for more details.

## Running CELESTA

Clone the `CC_codeximaging` repo and navigate to `bash_scripts`. Note that whenever you run a shell script, there are arguments you will need to edit according to your needs.

You have two options when running CELESTA:

1. **Run the full pipeline:** Run `celesta_full_pipeline.sh`.
    * This creates a CELESTA object, assigns cells, plots expression probability, and plots cell assignments using built-in CELESTA functions. 
2. *(Recommended)* **Run steps separately:** 
    * First run `celesta_create_obj.sh` to create a CELESTA object.
    * After the CELESTA object is created, run `celesta_assign_cells.sh`.
    * I recommend this approach because creating a CELESTA object can often take a long time, but it does not depend on thresholds. So when testing out different thresholds, we can just create one CELESTA object and test a bunch of thresholds from there.

## Inspecting CELESTA results

Results will be saved to `output_dir/project_title/` as specified in the shell script you ran (any in the above section).

1. `celesta_full_pipeline.sh` outputs:
    * CELESTA object without cell type assignments (RDS)
    * CELESTA object with cell type assignments (RDS)
    * Final cell assignments (CSV)
    * Cell assignment plot
    * Expression probability plots

2. `celesta_create_obj.sh` outputs:
    * CELESTA object without cell type assignments (RDS)
    * Marker expression probability (CSV)

3. `celesta_assign_cells.sh` outputs:
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

