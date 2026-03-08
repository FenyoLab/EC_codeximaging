# =============================================================================
# config.py
# All parameters for the EC mIF analysis pipeline.
# Update paths and toggle analysis modules before running main.py.
# =============================================================================

# ---- Paths (update these to match your directory structure) ----
RESULTS_DIR = "/path/to/results"
METADATA_PATH = "/data/metadata_with_new_cell_types.feather"
CLINICAL_DIR = "/path/to/EC_Clinical_Data.csv"

# ---- Sample exclusions ----
SAMPLES_SKIP = [
    '20230922-7331-1J_Scan1',
    '20231003-0413-3C_Scan1',
    '20231019-4475-1E_Scan2',
    '20230908-1872-4C-1_Scan2'
]

# ---- Clinical variables to test ----
CLINICAL_VARS_LIST = ['Recurred']

# ---- Cell type column(s) to analyze ----
CELL_TYPE_COLUMNS = ['cell_type_Macrophages_CD4_rm']

# ---- Cell type definitions ----
ARTIFACT_CELLS = ['Artifact', 'artifact', 'artifact_new', 'artifact_IFNG']

BASIC_CELL_TYPES = [
    'CD163+ Macrophages', 'CD4⁺CD163⁺ Macrophages', 'CD4⁻CD163⁺ Macrophages',
    'CD163- Macrophages', 'CD4⁺CD163⁻ Macrophages', 'CD4⁻CD163⁻ Macrophages',
    'CD3+ CD4- CD8- T cells', 'CD4+ T cells', 'CD4⁺ T cells', 'CD8+ T cells',
    'CD8⁺ T cells', 'Endothelial cells', 'Neutrophils', 'Tumor cells',
    'Undefined cells', 'B cells', 'CD4+ and CD8+ T cells', 'CD20+ and CD4+ cells',
    'CD20+ and CD3e+ cells', 'CD20+ and CD8+ cells'
]

CELL_TYPES_REMOVE = [
    'CD4+ and CD8+ T cells', 'B cells', 'Undefined cells', 'CD20+ and CD8+ cells',
    'CD20+ and CD3e+ cells', 'CD20+ and CD4+ cells', 'Neutrophils',
    'CD3+ CD4- CD8- T cells', 'CD4⁺CD163⁺ Macrophages', 'CD4⁻CD163⁺ Macrophages',
    'CD4⁺CD163⁻ Macrophages', 'CD4⁻CD163⁻ Macrophages'
]

CELL_TYPES_RENAME = {
    'CD4+ T cells': 'CD4⁺ T cells',
    'CD8+ T cells': 'CD8⁺ T cells',
    'CD163+ Macrophages': 'CD163⁺ Macrophages',
    'CD163- Macrophages': 'CD163⁻ Macrophages',
    'CD3+ CD4- CD8- T cells': 'CD3⁺ CD4⁻ CD8⁻ T cells',
    'CD4⁺ T cells_PD1_+': 'PD1⁺CD4⁺ T cells',
    'CD8⁺ T cells_PD1_+': 'PD1⁺CD8⁺ T cells',
    'CD4⁺ T cells_PD1_L': 'PD1lowCD4⁺ T cells',
    'CD8⁺ T cells_PD1_L': 'PD1lowCD8⁺ T cells',
    'CD4⁺ T cells_PD1_H': 'PD1highCD4⁺ T cells',
    'CD8⁺ T cells_PD1_H': 'PD1highCD8⁺ T cells',
    'CD8⁺ T cells_Ki67_+': 'Ki67⁺CD8⁺ T cells'
}

CELL_TYPES_KEEP = [
    'CD4+ T cells', 'CD8+ T cells', 'Endothelial cells',
    'CD163+ Macrophages', 'CD163- Macrophages', 'CD3+ CD4- CD8- T cells', 'Tumor cells',
    'CD4⁺CD163⁺ Macrophages', 'CD4⁻CD163⁺ Macrophages',
    'CD4⁺CD163⁻ Macrophages', 'CD4⁻CD163⁻ Macrophages',
    'CD4⁺ T cells', 'CD8⁺ T cells', 'CD163⁺ Macrophages', 'CD163⁻ Macrophages',
    'CD3⁺ CD4⁻ CD8⁻ T cells', 'CD4⁺ T cells_PD1_+', 'CD8⁺ T cells_PD1_+',
    'CD4⁺ T cells_PD1_L', 'CD8⁺ T cells_PD1_L',
    'CD4⁺ T cells_PD1_H', 'CD8⁺ T cells_PD1_H'
]

# ---- Analysis modules to run (set True/False) ----
RUN_GEN_PROPORTION_SUMMARY_TABLE = True
RUN_GEN_PROPORTION_TCELLS = False
RUN_GEN_CELL_TYPE_RATIO_SUMMARY_TABLE = False
RUN_GEN_FRACTION_INTRA_SUMMARY_TABLE = False
RUN_GEN_MEDIAN_DISTANCE_SUMMARY_TABLE = False
RUN_GEN_SCIMAP_INTERACTION_SUMMARY_TABLE = False

# ---- Statistical testing ----
GEN_SUMMARY_CSV = True
GEN_NEW_MARKER_POSITIVITY_PROPORTION = False

# ---- Boxplot settings ----
RUN_GEN_BOXPLOTS = True
ADD_PLOT_TITLE = False
SAMPLE_LABEL = False
ADD_COLOR_POINTS_STAGE = True
TITLE_FONT_SIZE = 16
SUBTITLE_FONT_SIZE = 12
Y_TICK_FONT_SIZE = 15
X_TICK_FONT_SIZE = 18
P_VALUE_TICK_FONT_SIZE = 15
X_TICK_LABELS_DICT = {
    'Stage': ['Low Stage', 'High Stage'],
    'Recurred': ['Non-Recurrent', 'Recurrent'],
    'IO response': ['ICI Non-Responder', 'ICI Responder']
}
BOXPLOT_SHAPES = {"Stage": "s", "Recurred": "o", "IO response": "^"}

# ---- Cell type ratios ----
RATIOS_TO_CHECK = [
    {
        "name": "CD8⁺/CD4⁺ T-cell ratio",
        "num": "CD8⁺ T cells",
        "den": "CD4⁺ T cells",
        "use_pattern": False
    }
]

# ---- Spatial interaction settings ----
SCIMAP_DATA_PATH = "/scimap/Neighborhood_Analysis_marker_combos/cell_type/"
OUT_SCIMAP_INTERACTION_SUMMARY_TABLE = f"Summary_tables/{SCIMAP_DATA_PATH}"
INTERACTION_RADIUS_PX = 30
UM_PER_PX = 0.5
INTERACTION_RADIUS_UM = int(INTERACTION_RADIUS_PX * UM_PER_PX)
INTERACTION_TYPE = 'mean_proportion_interacting_cell_type'
ANCHOR_CELL_TYPE = 'CD8+ T cells'
INTERACTING_CELL_TYPE = 'Tumor cells'
REGION = 'whole_tissue'

SCIMAP_DATA_PATH_TEST = "scimap/Neighborhood_Analysis"
OUT_SCIMAP_INTERACTION_SUMMARY_TABLE_TEST = f"Summary_tables/{SCIMAP_DATA_PATH_TEST}"
GEN_INTERACTION_SUMMARY_TABLE = True
GEN_NULL_DISTRIBUTION = True

# ---- Median distance settings ----
SELF_INTERACTIONS = True

# =============================================================================
# Scimap Neighborhood Analysis
# Must be run before RUN_GEN_SCIMAP_INTERACTION_SUMMARY_TABLE.
# Outputs adata_all_combos.h5ad which the interaction summary table reads.
# =============================================================================

# ---- Input data (can share with above paths or point to separate files) ----
MATRIX_RAW = "/path/to/matrix.npy"          # counts matrix (.npy or .feather)
CELL_TYPE_COL_PARAM = 'cell_type'  # column in metadata to use as phenotype

# ---- Scimap output directory ----
OUTPUT_DIR_SCIMAP = f"{RESULTS_DIR}/scimap/Neighborhood_Analysis"

# ---- Slide filtering ----
SLIDES = None          # list of slide IDs to include, or None for all
SLIDES_RM = SAMPLES_SKIP  # reuse the existing exclusion list

# ---- Spatial analysis parameters ----
SPATIAL_ANALYSIS_LIST = ['spatial_count']       # 'spatial_count', 'spatial_expression', 'spatial_lda'
SPATIAL_METHOD_LIST   = ['radius']              # 'radius' or 'knn'
N_KNN_LIST            = [20]                    # k values for knn method
N_RADIUS_LIST         = [30]                    # radius values in pixels
N_KMEANS_LIST         = [10]                    # number of neighborhood clusters

# ---- T cell types for PD1 phenotype renaming ----
T_CELL_TYPES = [
    'CD4+ T cells', 'CD8+ T cells', 'CD4⁺ T cells', 'CD8⁺ T cells',
    'CD3+ CD4- CD8- T cells', 'CD3⁺ CD4⁻ CD8⁻ T cells',
    'Helper T cells', 'Cytotoxic T cells', 'T cells (other)'
]

# ---- Cell types to exclude from spatial clustering (kept in Omero tables) ----
CELLTYPES_RM_SCIMAP = ARTIFACT_CELLS  # reuse artifact cell list

# ---- Cell type subsets for separate barplot panels ----
CELLTYPE_SUBSET = None   # e.g. [['CD8+ T cells', 'CD4+ T cells']] or None
IMMUNE_SUBSET   = True   # generate immune-only barplots (no Tumor/Stromal/Endothelial)
PD1_PHENOTYPES  = True   # append PD1+High / PD1+Low suffix to T cell phenotype names

# ---- Omero image dict: {slide_id: {'roi_id': <int>}} ----
OMERO_IMAGE_DICT = {}    # fill in if using Omero table export

# ---- Scimap run flags ----
RUN_SCIMAP_NEIGHBORHOODS          = False  # Step 1: run spatial analysis + k-means (REQUIRED first)
RUN_SCIMAP_GEN_OMERO_TABLES       = False  # export per-sample Omero CSV tables
RUN_SCIMAP_GEN_BARPLOTS           = False  # stacked bar plots of cell type per neighborhood
RUN_SCIMAP_GEN_BOXPLOTS           = False  # clinical association boxplots per neighborhood
RUN_SCIMAP_GEN_PIEPLOTS           = False  # pie charts per neighborhood
RUN_SCIMAP_CORRELATION_PLOT       = False  # scimap groupCorrelation plots
SCIMAP_SAMPLE_LABELS              = False  # annotate boxplot points with sample IDs
