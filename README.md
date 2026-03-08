# EC_codeximaging

## Overview

This repository contains a Python-based pipeline for preprocessing, cell segmentation, and cell phenotyping of multiplexed immunofluorescence whole-slide images (WSI) from endometrial cancer tissue.

The pipeline enables large-scale single-cell analysis of multiplexed imaging data by performing tile-based segmentation, marker quantification, and downstream clustering to identify cell phenotypes within the tumor microenvironment.

This codebase was used for image preprocessing, cell segmentation, and cell phenotyping in the manuscript:

**"The Spatial Immune Landscape of Mismatch Repair Deficient Endometrial Cancer: Implications for Clinical Outcomes"**, submitted to Modern Pathology.

Additional implementation details describing the scripts and workflow are provided in **Script Info.pdf**.

---

## Pipeline Overview

The pipeline performs the following major steps:

### 1. Tile preprocessing and E-cadherin intensity extraction

Whole-slide images are divided into tiles. For each tile, the mean intensity of the **top 5% of pixels in the E-cadherin channel** is calculated.

### 2. Tile clustering

Per-sample **k-means clustering (k = 3)** is applied to E-cadherin intensity values to identify epithelial and non-epithelial tissue regions.

Clusters with higher E-cadherin signal are classified as:

- **E-cadherin positive (Ecad⁺)**
- **E-cadherin negative (Ecad⁻)**

### 3. Segmentation strategy assignment

Different segmentation strategies are applied depending on tile classification:

- **Ecad⁺ tiles:** whole-cell segmentation  
- **Ecad⁻ tiles:** nuclear segmentation with pixel expansion

### 4. Cell segmentation

Segmentation generates:

- **cell-by-marker intensity matrix**
- **cell metadata including:**
  - centroid coordinates
  - area
  - perimeter
  - axis ratio
  - tile coordinates
  - slide/sample identifiers

Separate outputs are generated for Ecad⁺ and Ecad⁻ tiles and later concatenated into a unified dataset.

### 5. Marker thresholding and normalization

Cell lineage markers are thresholded using **k-means clustering** to identify marker-positive populations.

The marker matrix is then normalized per sample:

- biomarker values capped at the **99.9th percentile**
- **z-score normalization**
- **arcsinh transformation**

### 6. Dimensionality reduction and clustering

Cell phenotypes are identified through:

- **UMAP embedding**
- **k-means clustering**

Clustering results are used to define cell populations based on marker expression.

### 7. Downstream analysis and visualization

The pipeline generates:

- **UMAP visualizations**
- **marker expression heatmaps**
- **cluster composition plots**
- **quality control plots (e.g., sample batch effects)**

---

## Key Scripts

### Segmentation and preprocessing

`main_cell_segmentation.py`  
Performs tile clustering based on E-cadherin intensity and generates cell segmentations.

`run_preprocess.py`  
Prepares image tiles and preprocessing inputs.

### Image labeling and export

`main_label_images.py`  
Generates label images for segmented cells.

`main_label_images_to_omero.py`  
Uploads segmentation outputs to OMERO.

### Biomarker extraction

`main_biomarker_tables.py`  
Generates biomarker expression tables for downstream analysis.

`main_biomarker_tables_to_omero.py`  
Uploads biomarker tables to OMERO.

### Cell phenotyping

`main_cell_segmentation_analysis.py`  
Performs marker normalization, dimensionality reduction, and clustering.

`main_celltype_cluster_tables.py`  
Exports cluster assignments representing cell phenotypes.

---

## Environment

The pipeline was executed using Python within a conda environment.

Example environments used in the pipeline:


module load condaenvs/new/deepcell
conda activate omero


Dependencies include common scientific Python packages such as:

- numpy
- pandas
- scikit-learn
- matplotlib
- umap-learn

Additional dependencies may be required depending on the execution environment.

---

## Data Availability

Multiplexed immunofluorescence images analyzed in this study contain patient-derived data and cannot be publicly shared due to privacy and institutional restrictions.

Processed data and analysis outputs supporting the findings of the associated manuscript may be available from the corresponding author upon reasonable request.

---

## Notes

- Detailed documentation describing script functionality is available in **Script Info.pdf**.
- The repository reflects the code used for analysis in the associated manuscript and may contain 
