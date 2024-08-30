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
from src.analysis import clustering_analysis

normal_matrix_filtered_path = os.path.join(config.out_dir, config.matrix_normal_filtered_path)
umap_coord_path = os.path.join(config.out_dir, config.umap_coord_path)
kmeans_labels_path = os.path.join(config.out_dir, config.kmeans_labels_path)
metadata_filtered_path = os.path.join(config.out_dir, config.metadata_filtered_path)

#call segmentation function 
get_cell_segmentations(data_path = config.data_dir, tile_size = config.tile_size, batch_size = config.batch_size, 
                       save_path = config.segementation_data_dir, num_biomarkers = config.num_channels)
#call normalization function 
get_normalized_matrix(save_path = config.out_dir, raw_data_dir = config.segementation_data_dir, channel_names = config.channel_names, filtered_channel_names = config.filtered_channel_names, samples_to_remove = config.samples_to_skip) 
#call umap function 
gen_umap_embedding.plot_umap(emb_path = normal_matrix_filtered_path, umap_emb_path = umap_coord_path, save_path = config.out_dir)
#call kmeans function 
kmeans.clustering(emb_path = normal_matrix_filtered_path, umap_path = umap_coord_path, n_clusters = config.n_clusters, save_path = config.out_dir)
kmeans.add_labels_to_metadata(labels_path = kmeans_labels_path, metadata_path = metadata_filtered_path, save_path=config.out_dir, n_clusters = config.n_clusters)
#analyze results 
clustering_analysis(save_path = config.out_dir, n_clusters = config.n_clusters, channel_names = config.channel_names, filtered_channel_names = config.filtered_channel_names, slide_names = config.slides)