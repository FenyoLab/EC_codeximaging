import os
import numpy as np
from types import SimpleNamespace
from utils import helper

#import config
config_yaml= 'config/config_cellsegmentation.yaml'
run_config = helper.load_yaml_file(config_yaml)
config = SimpleNamespace(**run_config)

from src.omero_tables import omero_biomarker_cluster_tables

thresholding_save_dir = os.path.join(config.segmentation_data_dir, 'thresholding_clusters')

omero_biomarker_cluster_tables.threshold_biomarker_clusters(segmentation_data_dir = config.segmentation_data_dir, 
                                                        channel_names = config.channel_names, 
                                                        thresholding_channel_names = config.threshold_channel_names, 
                                                        omero_dict = config.omero_image_dict, 
                                                        save_dir = thresholding_save_dir, 
                                                        n_clusters = config.n_clusters_thresholding)

omero_mean_marker_tables(segmentation_data_dir = config.segementation_data_dir, 
                        channel_names = config.channel_names, 
                        omero_dict = config.omero_image_dict, 
                        save_dir = config.label_images_dir)