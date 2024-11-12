import os
import numpy as np
from types import SimpleNamespace
from utils import helper

#import config
config_yaml= 'config/config_cellsegmentation.yaml'
run_config = helper.load_yaml_file(config_yaml)
config = SimpleNamespace(**run_config)

#import python files
from src.normalization import normalize_matrix, threshold_markers
from src.dimensionality_reduction import gen_umap_embedding, gen_pca_embedding
from src.clustering import kmeans
from src.analysis import clustering_analysis

#threshold raw_matrix
threshold_markers.threshold_markers(data_dir = config.segmentation_data_dir, channel_names = config.channel_names, 
                threshold_dict = config.lineage_markers_cluster_dict, 
                threshold_channel_names = config.threshold_channel_names,
                save_path = config.out_dir, n_clusters = config.n_clusters_thresholding)

#call normalization function 
thresholded_dir = os.path.join(config.out_dir, config.thresholded_dir)

normalize_matrix.get_normalized_matrix(save_path = config.out_dir, raw_data_dir = config.segmentation_data_dir, 
                    thresholded_dir = thresholded_dir, channel_names = config.channel_names, 
                    lineage_markers = config.lineage_markers, threshold_dict = config.lineage_markers_cluster_dict,
                    samples_to_remove = config.samples_to_remove) 

#call pca function 
normal_matrix_filtered_path = os.path.join(config.out_dir, config.matrix_normal_filtered_path)
pca_coord_path = os.path.join(config.out_dir, config.pca_coord_path)

gen_pca_embedding.plot_pca(emb_path = normal_matrix_filtered_path, pca_emb_path = pca_coord_path, 
                            save_path = config.out_dir, random_state = config.random_state)
                            
#call kmeans function 
kmeans_labels_path = os.path.join(config.out_dir, config.clustering_dir, f'{config.n_clusters_celltypes}_clusters', 'kmeans_labels.npy')
raw_metadata_path = os.path.join(config.segmentation_data_dir, 'metadata.csv')
metadata_filtered_path = os.path.join(config.out_dir, config.metadata_filtered_path)

kmeans.clustering(emb_path = normal_matrix_filtered_path, pca_path = pca_coord_path, 
                n_clusters = config.n_clusters_celltypes, save_path = config.out_dir, random_state = config.random_state)
kmeans.add_labels_to_metadata(labels_path = kmeans_labels_path, raw_metadata_path = raw_metadata_path, 
                filtered_metadata_path = metadata_filtered_path, save_path=config.out_dir, 
                n_clusters = config.n_clusters_celltypes)
                
#analyze results 
clustering_analysis.clustering_analysis(save_path = config.out_dir, n_clusters = config.n_clusters_celltypes, 
                                    channel_names = config.channel_names, 
                                    lineage_markers = config.lineage_markers)

