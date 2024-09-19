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

#set password in env first: export YOUR_PASSWORD='your_password'
'''this script must be run from datamover node with omero conda environment activated'''
'''first mount the research drive directly in terminal and then run the script (from sbatch)'''

def main():
    #load in config 
    config_yaml= '/gpfs/home/as18894/projects/as18894/FenyoLab/Endometrial/EC_codeximaging/config/config_cellsegmentation.yaml'
    run_config = helper.load_yaml_file(config_yaml)
    config = SimpleNamespace(**run_config)

    metadata_per_sample_path = os.path.join(config.out_dir, config.sample_metadata_dir)
    out_suffix = os.path.basename(config.out_dir)

    omero_table(metadata_dir = metadata_per_sample_path, base_dir = config.research_drive_dir, 
                    omero_info_dict = config.omero_image_info_dict, n_clusters = config.n_clusters, samples_to_remove = config.samples_to_skip, kerberosid = config.kerberosid, out_suffix = out_suffix) #, out_suffix = out_suffix)


def omero_table(metadata_dir, base_dir, omero_info_dict, n_clusters, samples_to_remove = None, kerberosid = None, out_suffix = None): #, out_suffix = None):
    
    #navigate to correct dir on research drive 
    research_drive_dir = f'/mnt/{kerberosid}/{base_dir}/label_images'
    os.chdir(research_drive_dir)
    print(f"Current directory: {os.getcwd()}")
    
    #to save tables with date of run 
    date = "_".join(out_suffix.split("_")[1:])

    password = os.getenv('YOUR_PASSWORD')
    if password is None:
        raise ValueError('No password provided in environment variable YOUR_PASSWORD')
    print(password)
    breakpoint()

    sample_names = os.listdir(research_drive_dir) 
    for sample in sample_names:
        
        #for testing purposes
        if sample in samples_to_remove:
            print(f"Skipping sample: {sample}")
            continue
        
        print(f'Processing sample {sample}')

        os.makedirs(sample, exist_ok =True)
        os.chdir(sample)
        print(f"Current directory: {os.getcwd()}")

        roi_value = omero_info_dict.get(sample, {}).get('roi_id')
        table_path = os.path.join(research_drive_dir, sample, f'metatable_{n_clusters}_{date}.csv')
        print(table_path)
        if os.path.exists(table_path):
            print('Metatable already generated')

        else:
            create_omero_table(metadata_dir, table_path, sample, roi_value, n_clusters)
            print("omero table created")
        
        image_id = omero_info_dict.get(sample, {}).get('image_id')
        table_name = f'cluster_celltype_{n_clusters}_{date}'
        ann_id = upload_omero_table(table_path, sample, table_name, image_id, roi_value, kerberosid, password)
        print(f"OMERO table uploaded for {sample}")
        breakpoint()
    
        os.chdir('..')
    

def create_omero_table(metadata_dir, table_path, sample, roi_value, n_clusters):

    metadata = pd.read_csv(f'{metadata_dir}/{n_clusters}_clusters/{sample}/sample_metadata.csv', index_col = 0)
    print("Metadata shape:", metadata.shape)
    print(sample, roi_value)

    omero_df = pd.DataFrame({
        'object': metadata['label_image_cell_index'],
        'roi': roi_value,
        'kmeans_label': metadata['cluster_label'],
        #'cell_types': metadata['cell_types']
    })
    print("Omero_df shape:", omero_df.shape)
    omero_df.to_csv(table_path, index = True)


def upload_omero_table(table_path, sample, table_name, image_id, roi_value, kerberosid, password, server="omero.nyumc.org", port=4064):

    ann_id = omero2pandas.upload_table(
    table_path, table_name, 
    links=[("Image", image_id), ("Roi", roi_value)], server="omero.nyumc.org", port=4064, username=kerberosid, password=password)


if __name__ == "__main__":
    main()