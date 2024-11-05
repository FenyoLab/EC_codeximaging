import os
import numpy as np
from types import SimpleNamespace
from utils import helper

#import config
config_yaml= 'config/config_cellsegmentation.yaml'
run_config = helper.load_yaml_file(config_yaml)
config = SimpleNamespace(**run_config)

#import python files
from src.clustering import assign_celltypes

phenotype_clusters_path = os.path.join(config.out_dir, config.clustering_dir, f'{config.n_clusters_celltypes}_clusters/phenotype_clusters.csv')
thresholded_matrix_path = os.path.join(config.out_dir, config.thresholded_dir, 'matrix.npy')
cluster_arr_path = os.path.join(config.out_dir, config.celltypes_dir, f'{config.n_clusters_celltypes}_clusters/cd3e_3clusters_info.npy')

assign_celltypes.assign_celltypes(save_path = config.out_dir, n_clusters = config.n_clusters_celltypes, 
                            thresholding_dict = config.lineage_markers_cluster_dict, thresholded_matrix_path = thresholded_matrix_path,
                            cell_types_dict = config.cluster_celltype_labels, phenotype_clusters_path = phenotype_clusters_path,
                            cluster_arr_path = cluster_arr_path, channel_names = config.channel_names)