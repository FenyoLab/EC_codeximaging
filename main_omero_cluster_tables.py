import os
import numpy as np
from types import SimpleNamespace
from utils import helper

'''set password in env first: export YOUR_PASSWORD='your_password' '''
'''this script must be run with conda activate omero'''

#import config
config_yaml= '/gpfs/home/as18894/projects/as18894/FenyoLab/Endometrial/EC_codeximaging/config/config_cellsegmentation.yaml'
run_config = helper.load_yaml_file(config_yaml)
config = SimpleNamespace(**run_config)

from src.omero_tables import omero_cluster_tables

clustering_path = os.path.join(config.out_dir, config.clustering_dir, f'{config.n_clusters}_clusters')
phenotype_clusters_df_path = os.path.join(clustering_path, 'phenotype_clusters.csv')
omero_df_dir = os.path.join(clustering_path, 'omero_df_by_sample')
out_suffix = os.path.basename(config.out_dir)

omero_cluster_tables.celltype_clusters_omero_df(metadata_path = phenotype_clusters_df_path, save_path = omero_df_dir, data_dir = config.data_dir, omero_info_dict = config.omero_image_info_dict, samples_to_remove= config.samples_to_remove)
omero_cluster_tables.upload_omero_table(table_dir = omero_df_dir, omero_info_dict = config.omero_image_info_dict, 
                    n_clusters =config.n_clusters, kerberosid = config.kerberosid, out_suffix=out_suffix)