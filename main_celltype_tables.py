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
cell_types_path = os.path.join(config.out_dir, config.celltypes_dir, f'{config.n_clusters_celltypes}_clusters')
sample_names_path = os.path.join(config.segmentation_data_dir, 'cell_sample_names.npy')
omero_table_dir = os.path.join(config.out_dir, config.omero_table_dir)
out_suffix = os.path.basename(config.out_dir)
date = "_".join(out_suffix.split("_")[1:])

#create celltype cluster tables for omero
table_name_celltypes = f'celltypes_{date}'
gen_omero_tables.celltype_tables(sample_names_path = sample_names_path, cell_types_path = cell_types_path, 
                            omero_table_path = omero_table_dir, omero_dict = config.omero_image_dict, 
                            table_name = table_name_celltypes, n_clusters = config.n_clusters_celltypes)

#upload celltype cluster tables to omero
upload_omero_table.upload_omero_table(table_dir = omero_table_dir, table_name = table_name_celltypes, 
                            omero_dict = config.omero_image_dict, 
                            server="omero.nyumc.org", port=4064)
