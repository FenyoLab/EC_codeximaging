import os
import sys
import pandas as pd

import omero
import omero2pandas
from omero.gateway import BlitzGateway
from omero.model import RoiAnnotationLinkI, RoiI, FileAnnotationI
from omero.sys import ParametersI
from getpass import getpass

from types import SimpleNamespace

sys.path.append('../..')
from utils import helper

def celltype_clusters_omero_df(metadata_path, save_path, data_dir, omero_info_dict, samples_to_remove=None):

    metadata = pd.read_csv(metadata_path)

    os.makedirs(save_path, exist_ok=True)
    unique_sample_names = os.listdir(data_dir)

    for sample in unique_sample_names:
        if samples_to_remove is not None and sample in samples_to_remove:
            print(f"Skipping sample: {sample}")
            continue
        if sample == 'common_channels.txt':
            continue
        
        sample_dir = os.path.join(save_path, sample)
        os.makedirs(sample_dir, exist_ok=True)
        
        sample_omero_df_path = os.path.join(sample_dir, 'omero_df_celltype_clusters.csv')
        if os.path.exists(sample_omero_df_path):
            print('Cluster information already exists for this sample, skipping')
            continue

        print(f"Processing sample: {sample}")
        
        sample_metadata = metadata[metadata['slide_id'] == sample]
        sample_metadata = sample_metadata.reset_index(drop=True)
        sample_metadata.index += 1
        sample_metadata['label_image_cell_index'] = sample_metadata.index

        # create omero df
        roi_value = omero_info_dict.get(sample, {}).get('roi_id')
        omero_df = pd.DataFrame({
            'object': sample_metadata['label_image_cell_index'],
            'roi': roi_value,
            'kmeans_label': sample_metadata['cluster_label'],
        #'cell_types': metadata['cell_types']
        })

        # Save the selected columns to CSV
        omero_df.to_csv(sample_omero_df_path, index=False)

def upload_omero_table(table_dir, omero_info_dict, n_clusters, kerberosid = None, out_suffix=None):

    #get password 
    password = os.getenv('YOUR_PASSWORD')
    if password is None:
        raise ValueError('No password provided in environment variable YOUR_PASSWORD')

    #get date of run
    date = "_".join(out_suffix.split("_")[1:])

    sample_names = os.listdir(table_dir) 
    for sample in sample_names:
        if samples_to_remove is not None and sample in samples_to_remove:
            print(f"Skipping sample: {sample}")
            continue

        print(f'Processing sample {sample}')

        roi_value = omero_info_dict.get(sample, {}).get('roi_id')
        image_id = omero_info_dict.get(sample, {}).get('image_id')
        table_path = os.path.join(table_dir, sample, 'omero_df_celltype_clusters.csv')
        table_name = f'celltype_{n_clusters}_clusters_{date}'
        
        ann_id = omero2pandas.upload_table(table_path, table_name, 
                links=[("Image", image_id), ("Roi", roi_value)], server="omero.nyumc.org", 
                port=4064, username=kerberosid, password=password)
        print(f"OMERO table uploaded for {sample}")

if __name__ == "__main__":
    main()