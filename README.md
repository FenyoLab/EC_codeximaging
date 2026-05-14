# EC_codeximaging

## Overview

This repository contains a Python-based pipeline for preprocessing, cell segmentation, and cell phenotyping of multiplexed immunofluorescence whole-slide images (WSI) from endometrial cancer tissue.

The pipeline enables large-scale single-cell analysis of multiplexed imaging data by performing tile-based segmentation, marker quantification, and downstream clustering to identify cell phenotypes within the tumor microenvironment.

This codebase was used for image preprocessing, cell segmentation, and cell phenotyping in the manuscript:

**"The Spatial Immune Landscape of Mismatch Repair Deficient Endometrial Cancer: Implications for Clinical Outcomes"**

Additional implementation details describing the scripts and workflow are provided in **Script Info.pdf**.

---

## Pipeline Overview

The pipeline performs the following major steps:

### 1. Tile preprocessing and E-cadherin intensity extraction

Whole-slide images (downloaded from OMERO as QPTIFFs) are divided into tiles. For each tile, the mean intensity of the **top 5% of pixels in the E-cadherin channel** is calculated.

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

Lineage Cell phenotypes are identified through:

- **k-means clustering across all samples identifies main cell type groups**
- **mixed cluster phenotyping**

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

## Downstream analysis (`analysis/`)

The `analysis/` directory contains a config-driven pipeline for **downstream statistical and spatial analysis** of the cell-segmentation and phenotyping outputs. It expects per-cell metadata (e.g. `.feather`), a normalized counts matrix, and optional clinical data.

### Running the analysis

```bash
python analysis/main.py
```

All paths and which analyses to run are set in **`analysis/config.py`**. Update `RESULTS_DIR`, `METADATA_PATH`, and `CLINICAL_DIR` to match your data, then set the relevant `RUN_*` flags to `True` or `False`.

### Analysis modules

| Module | Config flag | Description |
|--------|-------------|-------------|
| **Proportions** | `RUN_GEN_PROPORTION_SUMMARY_TABLE` | Per-sample cell type proportions (total, T-cell–normalized, parent-type–normalized) and statistical tests vs. clinical variables. |
| **T cell / macrophage proportions** | `RUN_GEN_PROPORTION_TCELLS` | Proportion summaries focused on T cell and macrophage subsets. |
| **Cell type ratios** | `RUN_GEN_CELL_TYPE_RATIO_SUMMARY_TABLE` | User-defined ratios (e.g. CD8⁺/CD4⁺ T cells) per sample and region, with clinical association tests. |
| **Fraction intratumoral** | `RUN_GEN_FRACTION_INTRA_SUMMARY_TABLE` | Fraction of each cell type in intratumoral vs. peritumoral region and clinical associations. |
| **Median distance** | `RUN_GEN_MEDIAN_DISTANCE_SUMMARY_TABLE` | Median nearest-neighbor distance (µm) between cell type pairs per sample/region; optional self-interactions. |
| **Scimap neighborhoods** | `RUN_SCIMAP_NEIGHBORHOODS` | Spatial neighborhood analysis with [scimap]([https://github.com/labsyspharm/scimap]): spatial counts/expression, k-means neighborhood clusters, barplots, boxplots, and optional OMERO tables. Must run before the interaction summary. |
| **Scimap interactions** | `RUN_GEN_SCIMAP_INTERACTION_SUMMARY_TABLE` | Summary of cell–cell interactions (e.g. proportion of anchor cells near a target type within a radius) from scimap output. |

Outputs are written under `RESULTS_DIR` (e.g. `Summary_tables/`, proportion and ratio CSVs, boxplots). When boxplots are enabled, results are compared to clinical variables (e.g. recurrence, stage) with configurable statistical tests.

### Analysis dependencies

From `analysis/requirements.txt`:

- anndata  
- matplotlib  
- numpy  
- pandas  
- pyarrow  
- scipy  
- seaborn  

The scimap-based steps require **scimap** and **plotly** (for optional interactive plots). The pipeline also expects a small amount of project-specific structure (e.g. `utils.io`, `stats.tests`, `visualization.boxplots`); see the repository layout and `analysis/main.py` for import paths.

### Test data

The repository includes minimal **test data** in `test_data/` so that the downstream analysis pipeline can be run without access to the full study dataset. Included files:

| File | Description |
|------|-------------|
| `metadata.csv` | Per-cell metadata (cell type, centroid coordinates, slide ID, region `peri_intra_tumoral`, morphology, etc.) for a small number of cells across a few synthetic slides. |
| `matrix_raw.csv` | Raw cell-by-marker intensity matrix matching the metadata rows. |
| `EC_Clinical_Data.csv` | Slide-level clinical variables (e.g. `slide_id`, `Recurred`, `ICI response`) for the same slides. |

To run the analysis pipeline on this test data, set in `analysis/config.py`: `RESULTS_DIR` to the path to your results directory (e.g. the repo root or a copy of `test_data/`), `METADATA_PATH` to the relative path to the metadata file, and `CLINICAL_DIR` to the full path to `test_data/EC_Clinical_Data.csv`. The pipeline loads metadata via `read_feather`, so convert `metadata.csv` to `.feather` first if needed (e.g. `pd.read_csv('test_data/metadata.csv').to_feather('test_data/metadata.feather')`). The test set is small and intended only for verifying the code and workflow.

---

## Data Availability

Multiplexed immunofluorescence images will available on the NYU Langone OMERO Public server. 

---

## Notes

- Detailed documentation describing preprocessing, cell segmentation, and cell phenotyping is available in **Script Info.pdf**.
