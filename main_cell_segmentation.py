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

cell_marker_matrix_dir = os.path.join(config.out_dir, config.cell_marker_matrix_dir)
normal_matrix_filtered_path = os.path.join(config.out_dir, config.matrix_normal_filtered_path)
umap_coord_path = os.path.join(config.out_dir, config.umap_coord_path)
kmeans_labels_path = os.path.join(config.out_dir, config.kmeans_labels_path)
metadata_filtered_path = os.path.join(config.out_dir, config.metadata_filtered_path)

#call segmentation function 
get_cell_segmentations(data_path = config.data_dir, tile_size = config.tile_size, batch_size = config.batch_size, 
                       save_path = config.out_dir, num_biomarkers = config.num_channels)
#call normalization function 
get_normalized_matrix(save_path = config.out_dir, cell_marker_matrix_dir = cell_marker_matrix_dir, channel_names = config.channel_names, filtered_channel_names = config.filtered_channel_names) 
#call umap function 
gen_umap_embedding.plot_umap(emb_path = normal_matrix_filtered_path, umap_emb_path = umap_coord_path, save_path = config.out_dir)
#call kmeans function 
kmeans.clustering(emb_path = normal_matrix_filtered_path, umap_path = umap_coord_path, n_clusters = config.n_clusters, save_path = config.out_dir)
kmeans.add_labels_to_metadata(labels_path = kmeans_labels_path, metadata_path = metadata_filtered_path, save_path=config.out_dir)