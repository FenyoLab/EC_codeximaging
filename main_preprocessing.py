import os
import numpy as np
from types import SimpleNamespace
from utils import helper

#import config
config_yaml= 'config/config_cellsegmentation.yaml'
run_config = helper.load_yaml_file(config_yaml)
config = SimpleNamespace(**run_config)

from src.preprocessing import ecadherin_means, kmeans_tiles, assign_tissue_identity

mean_data_dir = os.path.join(config.preprocessing_dir, 'tile_means')
clusters_dir = os.path.join(config.preprocessing_dir, 'tissue_type_clusters')
positions_dir = os.path.join(config.preprocessing_dir, 'tile_positions')

ecadherin_means.get_top5_means_ecadherin(data_path = config.data_dir, tile_size = config.tile_size, 
                                    batch_size = config.batch_size, channel_names = config.channel_names, 
                                    mean_data_dir = mean_data_dir)
kmeans_tiles.cluster_tiles(mean_data_dir = mean_data_dir, n_clusters=config.n_clusters_preprocessing, 
                                    clusters_dir = clusters_dir)
kmeans_tiles.create_cluster_masks(mean_data_dir = mean_data_dir, clusters_dir = clusters_dir, 
                                    data_dir = config.data_dir, tile_size = config.tile_size)
assign_tissue_identity.new_positions(mean_data_dir = mean_data_dir, clusters_dir = clusters_dir, 
                                    positions_dir = positions_dir, tile_size = config.tile_size) #FOR NOW, POSITIONS DIR - IT WILL BE THE REAL DATA DIR POST PREPROCESSING!
