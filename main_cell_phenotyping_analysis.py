
import os
import numpy as np
from types import SimpleNamespace
from utils import helper
import pdb

#import config
config_yaml_cellseg= 'config/config_cellsegmentation.yaml'
run_config_cellseg = helper.load_yaml_file(config_yaml_cellseg)
config_cellseg = SimpleNamespace(**run_config_cellseg)

config_yaml_cellphen = 'config/config_cellphenotyping.yaml'
run_config_cellphen = helper.load_yaml_file(config_yaml_cellphen)
config_cellphen = SimpleNamespace(**run_config_cellphen)

#from src.clustering import kmeans 
from src.analysis import cell_type_analyses
from src.analysis import rdfpy_analysis

#kmeans.assign_cellphenotype(clustering_results_dir = config_cellseg.out_dir, n_clusters = config_cellseg.n_clusters, cluster_labels = config_cellphen.cluster_celltype_labels)
cell_type_analyses.cell_type_analysis(matrix_path = config_cellphen.matrix_raw, metadata_path = config_cellphen.metadata_celltypes, channels = config_cellseg.channel_names, clinical_dat = config_cellphen.clinical_data, cell_types = config_cellphen.celltypes, out_file = "/gpfs/data/proteomics/projects/mh6486/FenyoLab/Endometrial/EC_codeximaging/src/analysis/summary_celltypes.csv" )
#rdfpy_analysis.cell_type_analysis(matrix_path = config_cellphen.matrix_raw, metadata_path = config_cellphen.metadata_raw, channels = config_cellseg.channel_names, clinical_dat = config_cellphen.clinical_data, cell_types = config_cellphen.celltypes, out_file = "/gpfs/data/proteomics/projects/mh6486/FenyoLab/Endometrial/EC_codeximaging/src/analysis/summary_celltypes.csv" )