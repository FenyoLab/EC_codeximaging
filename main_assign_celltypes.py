import os
import numpy as np
from types import SimpleNamespace
from utils import helper

#import config
config_yaml= 'config/config_cellsegmentation.yaml'
run_config = helper.load_yaml_file(config_yaml)
config = SimpleNamespace(**run_config)

#import python files
from src.celltypes import assign_celltypes_test

phenotype_clusters_path = os.path.join(config.out_dir, config.clustering_dir, f'{config.n_clusters_celltypes}_clusters/phenotype_clusters.csv')
thresholded_matrix_path = os.path.join(config.out_dir, config.thresholded_dir, 'matrix.npy')

assign_celltypes_test.assign_celltypes(save_path = config.out_dir, thresholded_matrix_path = thresholded_matrix_path,
                            n_clusters_celltypes = config.n_clusters_celltypes, cell_types_dict = config.cluster_celltype_labels, 
                            thresholding_dict = config.lineage_markers_cluster_dict, phenotype_clusters_path = phenotype_clusters_path,
                            channel_names = config.channel_names)