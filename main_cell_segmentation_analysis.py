import os
import numpy as np
from types import SimpleNamespace
from utils import helper

#import config
config_yaml= '/gpfs/home/as18894/projects/as18894/FenyoLab/Endometrial/EC_codeximaging/config/config_cellsegmentation.yaml'
run_config = helper.load_yaml_file(config_yaml)
config = SimpleNamespace(**run_config)

#import python files
from src.cell_segmentation import get_cell_segmentations
from src.normalize_matrix import get_normalized_matrix
from src.umap_reduction import gen_umap_embedding 
from src.clustering import kmeans
from src.analysis import color_by_sample, color_by_marker, color_by_cluster, sample_per_cluster, expression_per_cluster

normal_matrix_path = os.path.join(config.out_dir, config.matrix_normal_path)
normal_matrix_filtered_path = os.path.join(config.out_dir, config.matrix_normal_filtered_path)
umap_coord_path = os.path.join(config.out_dir, config.umap_coord_path)
kmeans_labels_path = os.path.join(config.out_dir, config.kmeans_labels_path)
metadata_filtered_path = os.path.join(config.out_dir, config.metadata_filtered_path)
figures_dir = os.path.join(config.out_dir, config.figures_dir)
cluster_centroids_df_path = os.path.join(config.out_dir, config.figures_dir, 'cluster_centroids_df.csv')
sample_names_path = os.path.join(config.out_dir, 'normalized_matrix', 'cell_sample_names_filtered.npy')

#call segmentation function 
get_cell_segmentations(data_path = config.data_dir, tile_size = config.tile_size, batch_size = config.batch_size, 
                       save_path = config.segementation_data_dir, num_biomarkers = config.num_channels)
#call normalization function 
get_normalized_matrix(save_path = config.out_dir, cell_marker_matrix_dir = config.segementation_data_dir, channel_names = config.channel_names, filtered_channel_names = config.filtered_channel_names) 
#call umap function 
gen_umap_embedding.plot_umap(emb_path = normal_matrix_filtered_path, umap_emb_path = umap_coord_path, save_path = config.out_dir)
#call kmeans function 
kmeans.clustering(emb_path = normal_matrix_filtered_path, umap_path = umap_coord_path, n_clusters = config.n_clusters, save_path = config.out_dir)
kmeans.add_labels_to_metadata(labels_path = kmeans_labels_path, metadata_path = metadata_filtered_path, save_path=config.out_dir)

#analyze results 
color_by_sample.umap_by_sample(umap_path = umap_coord_path, sample_names_path = sample_names_path, plot_dir = figures_dir)
color_by_marker.umap_by_marker(umap_path = umap_coord_path, marker_path = normal_matrix_filtered_path, plot_dir = figures_dir, channel_names = config.filtered_channel_names) #i need the filtered channel names 
color_by_cluster.umap_by_cluster(umap_path = umap_coord_path, labels_path = kmeans_labels_path, plot_dir = figures_dir, n_clusters = config.n_clusters)
expression_per_cluster.gen_cluster_centroid_matrix(matrix_path = normal_matrix_path, labels_path = kmeans_labels_path, plot_dir = figures_dir, channel_names = config.channel_names)
expression_per_cluster.plot_cluster_matrix_as_heatmap(cluster_centroids_df_path = cluster_centroids_df_path, plot_dir = figures_dir, n_clusters = config.n_clusters, filtered_channel_names=config.filtered_channel_names)
sample_per_cluster.proportion_per_cluster(sample_names_path = sample_names_path, labels_path = kmeans_labels_path, plot_dir = figures_dir, n_clusters = config.n_clusters, slides = config.slides)