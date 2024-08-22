import os
import numpy as np
from types import SimpleNamespace
from utils import helper

#import config
config_yaml= '/media/ssd02/mh6486/Endometrial/as18894/cell_segmentation/config/config_cellsegmentation.yaml'
run_config = helper.load_yaml_file(config_yaml)
config = SimpleNamespace(**run_config)

#import python files
from src.analysis import color_by_sample, color_by_marker, color_by_cluster, sample_per_cluster, expression_per_cluster

kmeans_labels_path = os.path.join(config.out_dir, config.kmeans_labels_path)
figures_path = os.path.join(config.out_dir, config.figures_dir)
normal_matrix_path = os.path.join(config.out_dir, config.matrix_normal_path)
umap_coord_path = os.path.join(config.out_dir, config.umap_coord_path)
cluster_centroids_df_path = os.path.join(config.out_dir, config.figures_dir, 'cluster_centroids_df.csv')
sample_names_path = os.path.join(config.out_dir, 'normalized_matrix', 'cell_sample_names_filtered.npy')

color_by_sample.umap_by_sample(umap_path = umap_coord_path, sample_names_path = sample_names_path, plot_dir = figures_path)
color_by_marker.umap_by_marker(umap_path = umap_coord_path, marker_path = normal_matrix_path, plot_dir = figures_path, channel_names = config.filtered_channel_names) #i need the filtered channel names 
color_by_cluster.umap_by_cluster(umap_path = umap_coord_path, labels_path = kmeans_labels_path, plot_dir = figures_path, n_clusters = config.n_clusters)
expression_per_cluster.gen_cluster_centroid_matrix(matrix_path = normal_matrix_path, labels_path = kmeans_labels_path, plot_dir = figures_path, channel_names = config.filtered_channel_names)
expression_per_cluster.plot_cluster_matrix_as_heatmap(cluster_centroids_df_path = cluster_centroids_df_path, plot_dir = figures_path, n_clusters = config.n_clusters)
sample_per_cluster.proportion_per_cluster(sample_names_path = sample_names_path, labels_path = kmeans_labels_path, plot_dir = figures_path, n_clusters = config.n_clusters, slides = config.slides)