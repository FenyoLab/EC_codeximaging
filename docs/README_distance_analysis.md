# Distance analysis

This is a guide to running distance analysis. This step takes place after cell phenotyping in the `CC_codeximaging` pipeline.

## Pre-requisites
Before you begin, make sure you have done the following:

* Clone the `CC_codeximaging` repository and navigate to `bash_scripts`. You will have to run all scripts from within this directory for the relative paths to work.
* Have working `seurat_v5` (R) and `celesta` (python) environments. 
  * You can set these up with `config/celesta_env.yaml` and `config/seurat_v5_env.yaml`.
* Have a total metadata file containing all samples with barcoded cells. This is usually generated from Seurat analysis.

## Steps
1. Conduct distance analysis with `semla`.
```bash
$ sbatch semla_distance_analysis.sh
```
2. Plot radial distances and distance groups.
```bash
$ sbatch plot_radial_distances.sh
```
3. Prepare data for distance analysis.
```
notebooks/prep_data_for_dist_group_comparisons
```
4. Plot cell type proportions, distance groups, and slopes by response.
```bash
$ sbatch plot_celltype_proportions_by_response.sh
```
```bash
$ sbatch plot_dist_group_by_response.sh
```
```bash
$ sbatch plot_dist_group_slope_by_response.sh
```

## Notes
* To define paths and other specifics, directly edit the appropriate source code in `src/distance_analysis`. Each source code script will have the same name as its corresponding bash script.

## Citations

```bibtex
@article{larsson2023semla,
  title={Semla: a versatile toolkit for spatially resolved transcriptomics analysis and visualization},
  author={Larsson, Ludvig and Franz{\'e}n, Lovisa and St{\aa}hl, Patrik L and Lundeberg, Joakim},
  journal={Bioinformatics},
  volume={39},
  number={10},
  pages={btad626},
  year={2023},
  publisher={Oxford University Press}
}
```