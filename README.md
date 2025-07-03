# CC_codeximaging
This repository contains a mixed Python and R pipeline for cell segmentation, phenotyping, and spatial analysis of whole slide [CODEX](https://github.com/nolanlab/CODEX) images of cervical cancer.

## Setting up
Clone the `CC_codeximaging` repository and navigate to `bash_scripts`. You will have to run all scripts from within this directory for the relative paths to work. 

All necessary conda environments have been set up on UltraViolet, NYU Langone's high-performance computing cluster. You must be in the `proteome` group to access them.

Also make sure you have access to the [NYU Langone OMERO](https://omero.nyumc.org/), as all images are hosted there.

## Overview

The pipeline consists of five main steps:

1. [Cell segmentation](#cell-segmentation)
2. [Label images](#label-images)
3. [Calculate biomarker means](#calculate-biomarker-means)
4. [Cell phenotyping](#cell-phenotyping)
5. [Spatial analysis](#spatial-analysis)

## Cell segmentation

We begin by using [Mesmer from DeepCell](https://deepcell.readthedocs.io/en/latest/app-gallery/mesmer.html) to segment cells in our CODEX images:

```bash
$ sbatch main_cell_segmentation.sh
```

* This script first clusters pixels on E-cadherin expression to determine what type of segmentation method to use. For Ecad+ clusters, we use whole-cell-segmentation. For Ecad- clusters, we perform nuclear segmentation with 2-pixel expansion. 
* Outputs a metadata file containing: `cell_label, centroid_x, centroid_y, area, perimeter, axis_ratio, tile_h, tile_w, slide_id, tissue_type` for all cells across all samples.
* See [Script Info.pdf](https://github.com/lp2700/CC_codeximaging/blob/main/Script%20Info.pdf) for more details.

## Label images

Next, we split segmentation outputs by sample:

```bash
$ sbatch main_cell_segmentation.sh
```
* Upload to OMERO with `main_label_images_to_omero.sh`.
* The order of cells per sample must be preserved throughout the rest of the pipeline, especially when uploading any tables to OMERO.
* See [Script Info.pdf](https://github.com/lp2700/CC_codeximaging/blob/main/Script%20Info.pdf) for more details.

## Calculate biomarker means

We then calculate the mean intensity of each channel (biomarker) within each cell in the sample:

```bash
$ sbatch main_biomarker_tables.sh
```
* Upload to OMERO with `main_biomarker_tables_to_omero.sh`.
* See [Script Info.pdf](https://github.com/lp2700/CC_codeximaging/blob/main/Script%20Info.pdf) for more details.

## Cell phenotyping 

We use [CELESTA from the Plevritis Lab](https://github.com/plevritis-lab/CELESTA) to identify cell types in each image based on the raw biomarker means:

```bash
$ sbatch main_celesta_run_full_pipeline.sh
```
* Upload to OMERO with `main_celesta_to_omero_prep.sh` followed by `main_celltype_tables.sh`.
* Further cell phenotyping can be done after this step (e.g., by k-means clustering on marker expression in Seurat). 
* See [docs/README_celesta.md](https://github.com/lp2700/CC_codeximaging/blob/main/docs/README_celesta.md) for detailed instructions.

## Spatial analysis

Finally, we conduct spatial analysis using [Semla](https://github.com/ludvigla/semla):

```bash
$ sbatch semla_distance_analysis.sh
```
* Results can be plotted with:
    * `plot_radial_distances.sh`
    * `plot_celltype_proportions_by_response.sh`
    * `plot_dist_group_by_response.sh`
    * `plot_dist_group_slope_by_response.sh`  
* See [docs/README_distance_analysis.md](https://github.com/lp2700/CC_codeximaging/blob/main/docs/README_distance_analysis.md) for detailed instructions.

## Citations

```bibtex
@article{goltsev2018deep,
  title={Deep profiling of mouse splenic architecture with CODEX multiplexed imaging},
  author={Goltsev, Yury and Samusik, Nikolay and Kennedy-Darling, Julia and Bhate, Salil and Hale, Matthew and Vazquez, Gustavo and Black, Sarah and Nolan, Garry P},
  journal={Cell},
  volume={174},
  number={4},
  pages={968--981},
  year={2018},
  publisher={Elsevier}
}
```

```bibtex
@article{allan2012omero,
  title={OMERO: flexible, model-driven data management for experimental biology},
  author={Allan, Chris and Burel, Jean-Marie and Moore, Josh and Blackburn, Colin and Linkert, Melissa and Loynton, Scott and MacDonald, Donald and Moore, William J and Neves, Carlos and Patterson, Andrew and others},
  journal={Nature methods},
  volume={9},
  number={3},
  pages={245--253},
  year={2012},
  publisher={Nature Publishing Group US New York}
}
```

```bibtex
@article{greenwald2022whole,
  title={Whole-cell segmentation of tissue images with human-level performance using large-scale data annotation and deep learning},
  author={Greenwald, Noah F and Miller, Geneva and Moen, Erick and Kong, Alex and Kagel, Adam and Dougherty, Thomas and Fullaway, Christine Camacho and McIntosh, Brianna J and Leow, Ke Xuan and Schwartz, Morgan Sarah and others},
  journal={Nature biotechnology},
  volume={40},
  number={4},
  pages={555--565},
  year={2022},
  publisher={Nature Publishing Group US New York}
}
```

```bibtex
@article{zhang2022identification,
  title={Identification of cell types in multiplexed in situ images by combining protein expression and spatial information using CELESTA},
  author={Zhang, Weiruo and Li, Irene and Reticker-Flynn, Nathan E and Good, Zinaida and Chang, Serena and Samusik, Nikolay and Saumyaa, Saumyaa and Li, Yuanyuan and Zhou, Xin and Liang, Rachel and others},
  journal={Nature methods},
  volume={19},
  number={6},
  pages={759--769},
  year={2022},
  publisher={Nature Publishing Group US New York}
}
```

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
