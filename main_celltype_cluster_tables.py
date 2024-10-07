import os
import numpy as np
from types import SimpleNamespace
from utils import helper

#import config
config_yaml= 'config/config_cellsegmentation.yaml'
run_config = helper.load_yaml_file(config_yaml)
config = SimpleNamespace(**run_config)

from src.omero_tables import celltype_cluster_tables

#create celltype cluster tables for omero
clustering_path = os.path.join(config.out_dir, config.clustering_dir, f'{config.n_clusters_celltypes}_clusters')
omero_table_dir = os.path.join(clustering_path, 'omero_tables')

out_suffix = os.path.basename(config.out_dir)
date = "_".join(out_suffix.split("_")[1:])
table_name_celltype_clusters = f'celltype_{config.n_clusters_celltypes}clusters_{date}'

celltype_cluster_tables.celltype_cluster_tables(clustering_path = clustering_path, save_path = omero_table_dir, 
                                                omero_dict = config.omero_image_dict, n_clusters = config.n_clusters_celltypes,
                                                table_name = table_name_celltype_clusters, samples_to_remove=config.samples_to_remove, 
                                                out_suffix=out_suffix)

#upload celltype cluster tables to omero
upload_omero_table.upload_omero_table(table_dir = omero_table_dir, table_name = table_name_celltype_clusters, 
                            omero_dict = config.omero_image_dict, 
                            server="omero.nyumc.org", port=4064)