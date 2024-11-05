import os
import numpy as np
from types import SimpleNamespace
from utils import helper

#import config
config_yaml= 'config/config_cellsegmentation.yaml'
run_config = helper.load_yaml_file(config_yaml)
config = SimpleNamespace(**run_config)

from src.omero_tables import celltype_tables, upload_omero_table

#create celltype cluster tables for omero
cell_types_path = os.path.join(config.out_dir, config.celltypes_dir, f'{config.n_clusters_celltypes}_clusters')
omero_table_dir = os.path.join(cell_types_path, 'omero_tables')

out_suffix = os.path.basename(config.out_dir)
date = "_".join(out_suffix.split("_")[1:])
table_name_celltypes = f'celltypes_{date}'

celltype_tables.celltype_tables(cell_types_path = cell_types_path, save_path = omero_table_dir, 
                                omero_dict = config.omero_image_dict, n_clusters = config.n_clusters_celltypes,
                                table_name = table_name_celltypes, samples_to_remove=config.samples_to_remove)

#upload celltype cluster tables to omero
upload_omero_table.upload_omero_table(table_dir = omero_table_dir, table_name = table_name_celltypes, 
                            omero_dict = config.omero_image_dict, 
                            server="omero.nyumc.org", port=4064)