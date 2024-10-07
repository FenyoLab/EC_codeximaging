import os
import numpy as np
from types import SimpleNamespace
from utils import helper

#import config
config_yaml= 'config/config_cellsegmentation.yaml'
run_config = helper.load_yaml_file(config_yaml)
config = SimpleNamespace(**run_config)

#import python files
from src.split_tiles import ecadherin_means, kmeans_tiles, assign_tissue_identity
from src.cell_segmentation import get_cell_segmentations
from src.omero_tables import create_biomarker_cluster_tables
#from src.cell_segmentation import get_cell_segmentations

segmentation_tile_positions_dir = os.path.join(config.segmentation_data_dir, config.tiles_split_dir)

mean_data_dir = os.path.join(segmentation_tile_positions_dir, 'tile_means')
clusters_dir = os.path.join(segmentation_tile_positions_dir, 'tissue_type_clusters')
positions_dir = os.path.join(segmentation_tile_positions_dir, 'tile_positions')

ecadherin_means.get_top5_means_ecadherin(data_path = config.data_dir, tile_size = config.tile_size, 
                                    batch_size = config.batch_size, channel_names = config.channel_names, 
                                    mean_data_dir = mean_data_dir)
kmeans_tiles.cluster_tiles(mean_data_dir = mean_data_dir, n_clusters=config.n_clusters_preprocessing, 
                                    clusters_dir = clusters_dir)
kmeans_tiles.create_cluster_masks(mean_data_dir = mean_data_dir, clusters_dir = clusters_dir, 
                                    data_dir = config.data_dir, tile_size = config.tile_size)
assign_tissue_identity.new_positions(mean_data_dir = mean_data_dir, clusters_dir = clusters_dir, 
                                    positions_dir = positions_dir, tile_size = config.tile_size) #FOR NOW, POSITIONS DIR - IT WILL BE THE REAL DATA DIR POST PREPROCESSING!

#call segmentation function 
get_cell_segmentations(data_path = config.data_dir, tile_size = config.tile_size, batch_size = config.batch_size, 
                       save_path = config.segmentation_data_dir, num_biomarkers = config.num_channels)

#call thresholding lineage markers function 
thresholding_save_dir = os.path.join(config.segmentation_data_dir, 'thresholding_clusters')

create_biomarker_cluster_tables.threshold_biomarker_clusters(segmentation_data_dir = config.segmentation_data_dir, 
                                                        channel_names = config.channel_names, 
                                                        thresholding_channel_names = config.threshold_channel_names, 
                                                        omero_dict = config.omero_image_dict, 
                                                        save_dir = thresholding_save_dir, 
                                                        n_clusters = config.n_clusters_thresholding,
                                                        table_name = f'lineage_markers_{config.n_clusters_thresholding}clusters')