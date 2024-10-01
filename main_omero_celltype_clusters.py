import os
import numpy as np
from types import SimpleNamespace
from utils import helper

'''conda activate omero'''

#import config
config_yaml= 'config/config_cellsegmentation.yaml'
run_config = helper.load_yaml_file(config_yaml)
config = SimpleNamespace(**run_config)

from src.omero_tables import omero_celltype_cluster_tables

clustering_path = os.path.join(config.out_dir, config.clustering_dir, f'{config.n_clusters_celltypes}_clusters')
omero_table_dir = os.path.join(clustering_path, 'omero_tables')
out_suffix = os.path.basename(config.out_dir)

omero_celltype_cluster_tables.create_celltype_clusters_df(clustering_path = clustering_path, 
                                                        save_path = omero_table_dir, 
                                                        omero_dict = config.omero_image_dict, 
                                                        n_clusters = config.n_clusters_celltypes, 
                                                        samples_to_remove=config.samples_to_remove, 
                                                        out_suffix=out_suffix):