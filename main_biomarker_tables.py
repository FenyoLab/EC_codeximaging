import os
import numpy as np
from types import SimpleNamespace
from utils import helper

#import config
config_yaml= 'config/config_cellsegmentation.yaml'
run_config = helper.load_yaml_file(config_yaml)
config = SimpleNamespace(**run_config)

from src.omero_tables import lineage_marker_cluster_tables, biomarker_mean_tables

#call thresholding lineage markers function 
omero_table_dir = os.path.join(config.segmentation_data_dir, config.omero_table_dir)

table_name_lineage_clusters = f'lineage_markers_{config.n_clusters_thresholding}clusters'
lineage_marker_cluster_tables.lineage_marker_cluster_tables(segmentation_data_dir = config.segmentation_data_dir, 
                                                        channel_names = config.channel_names, 
                                                        thresholding_channel_names = config.threshold_channel_names, 
                                                        omero_dict = config.omero_image_dict, 
                                                        save_dir = omero_table_dir, 
                                                        n_clusters = config.n_clusters_thresholding,
                                                        table_name = table_name_lineage_clusters)

table_name_biomarker_means = 'raw_biomarker_means'
biomarker_mean_tables.biomarker_mean_tables(segmentation_data_dir = config.segmentation_data_dir, 
                        channel_names = config.channel_names, 
                        omero_dict = config.omero_image_dict, 
                        save_dir = omero_table_dir,
                        table_name = table_name_biomarker_means)