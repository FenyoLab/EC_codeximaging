import os
import numpy as np
from types import SimpleNamespace
from utils import helper

#import config
config_yaml= 'config/config_cellsegmentation.yaml'
run_config = helper.load_yaml_file(config_yaml)
config = SimpleNamespace(**run_config)

from src.omero_tables import upload_omero_table

#upload biomarker cluster tables
omero_table_dir = os.path.join(config.segmentation_data_dir, config.omero_table_dir)

table_name_lineage_clusters = f'lineage_markers_{config.n_clusters_thresholding}clusters'
upload_omero_table.upload_omero_table(table_dir = omero_table_dir, table_name = table_name_lineage_clusters, 
                            omero_dict = config.omero_image_dict, 
                            server="omero.nyumc.org", port=4064)

table_name_biomarker_means = 'raw_biomarker_means'
upload_omero_table.upload_omero_table(table_dir = omero_table_dir, table_name = table_name_biomarker_means, 
                            omero_dict = config.omero_image_dict, 
                            server="omero.nyumc.org", port=4064)