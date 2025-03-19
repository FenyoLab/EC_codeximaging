import os
import numpy as np
from src.omero_tables import gen_omero_tables, upload_omero_table

from types import SimpleNamespace
from utils import helper

#import config
config_yaml= 'config/config_cellsegmentation.yaml'
run_config = helper.load_yaml_file(config_yaml)
config = SimpleNamespace(**run_config)

#define relevant paths
sample_names_path = os.path.join(config.segmentation_data_dir, 'cell_sample_names.npy')
omero_table_dir = os.path.join(config.segmentation_data_dir, config.omero_table_dir) 

###### Lineage marker cluster tables ######                                   
table_name_lineage_clusters = f'lineage_markers_{config.n_clusters_thresholding}clusters'
gen_omero_tables.lineage_marker_cluster_tables(sample_names_path = sample_names_path, 
                                            segmentation_data_dir = config.segmentation_data_dir, 
                                            omero_table_path = omero_table_dir, omero_dict = config.omero_image_dict, 
                                            table_name = table_name_lineage_clusters, channel_names = config.channel_names, 
                                            thresholding_channel_names = config.threshold_channel_names, 
                                            n_clusters = config.n_clusters_thresholding)

upload_omero_table.upload_omero_table(table_dir = omero_table_dir, table_name = table_name_lineage_clusters, 
                                    omero_dict = config.omero_image_dict, server="omero.nyumc.org", port=4064)

###### Biomarker means tables ###### 
table_name_biomarker_means = 'raw_biomarker_means'
gen_omero_tables.biomarker_mean_tables(sample_names_path = sample_names_path, 
                                    segmentation_data_dir = config.segmentation_data_dir, 
                                    omero_table_path = omero_table_dir, omero_dict = config.omero_image_dict, 
                                    table_name = table_name_biomarker_means, channel_names = config.channel_names)

upload_omero_table.upload_omero_table(table_dir = omero_table_dir, table_name = table_name_biomarker_means, 
                                    omero_dict = config.omero_image_dict, server="omero.nyumc.org", port=4064)
