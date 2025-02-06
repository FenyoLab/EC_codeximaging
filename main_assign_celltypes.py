import os
import numpy as np
from types import SimpleNamespace
from utils import helper

#import config
config_yaml= 'config/config_cellsegmentation.yaml'
run_config = helper.load_yaml_file(config_yaml)
config = SimpleNamespace(**run_config)

#import python files
from src.celltypes import assign_celltypes_step1, assign_celltypes_step2, assign_celltypes_step3
from src.celltypes import celltype_distributions, compare_celltype_distributions
from src.celltypes.figures import visualize_cells
from src.celltypes import combine_metadata_with_celltypes

#assign celltypes step1
phenotype_clusters_path = os.path.join(config.out_dir, config.clustering_dir, f'{config.n_clusters_celltypes}_clusters/phenotype_clusters.csv')
thresholded_matrix_path = os.path.join(config.out_dir, config.thresholded_dir, 'matrix.npy')

assign_celltypes_step1.assign_celltypes(save_path = config.out_dir, thresholded_matrix_dir = thresholded_matrix_path,
                            n_clusters_celltypes = config.n_clusters_celltypes, cell_types_dict = config.cluster_celltype_labels, 
                            thresholding_dict = config.lineage_markers_cluster_dict, phenotype_clusters_path = phenotype_clusters_path,
                            channel_names = config.channel_names)

#assign celltypes step2
celltypes_dir = os.path.join(config.out_dir, config.celltypes_dir, f'{config.n_clusters_celltypes}_clusters')
thresholded_matrix_dir = os.path.join(config.out_dir, config.thresholded_dir)

assign_celltypes_step2.assign_mixed_celltypes_by_strict_thresholding(celltypes_dir = celltypes_dir, matrix_dir = thresholded_matrix_dir, 
                                                                mixed_celltypes = config.mixed_celltypes, channel_names = config.channel_names, 
                                                                threshold_dict = config.stricter_threshold_dict)


#create celltype distributions
celltype_distributions.plot_celltype_distributions(celltypes_dir = celltypes_dir, matrix_dir = thresholded_matrix_dir, 
                                                celltypes_dict = config.marker_celltype_dict, channel_names = config.channel_names)

#compare celltype distributions
distributions_dir = os.path.join(celltypes_dir, 'celltype_distributions')

compare_celltype_distributions.compare_celltype_distributions(celltypes_dir = celltypes_dir, matrix_dir = thresholded_matrix_dir, 
                                                        save_path = distributions_dir, mixed_celltypes = config.mixed_celltypes, 
                                                        channel_names = config.channel_names)

#visualize mixed cells
metadata_path = os.path.join(config.segmentation_data_dir, 'metadata.csv')
cell_types_df_path = os.path.join(cell_types_dir, 'cell_types_v2.csv')
    
visualize_cells.visualize_cells(distributions_dir = distributions_dir, metadata_path = metadata_path, cell_types_df_path = cell_types_df_path, 
                            image_dir = config.data_dir, markers = config.mixed_celltype_markers, channel_names = config.all_channel_names)

#assign celltypes step3
assign_celltypes_step3.assign_final_celltypes(celltypes_dir = celltypes_dir, mixed_celltypes = config.mixed_celltypes, 
                                            percentile_thresholds_dict = config.percentile_thresholds_dict)

#combine metadata with celltypes
celltypes_path = os.path.join(celltypes_dir, 'cell_types.csv')

combine_metadata_with_celltypes.combine_metadata_with_celltypes(metadata_path = metadata_path, celltypes_path = celltypes_path)