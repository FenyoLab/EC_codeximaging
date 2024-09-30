#import the label table into omero!!

import os
import sys
import pandas as pd
import pdb

import omero
import omero2pandas
from omero.gateway import BlitzGateway
from omero.model import RoiAnnotationLinkI, RoiI, FileAnnotationI
from omero.sys import ParametersI
from getpass import getpass

from types import SimpleNamespace

sys.path.append('../..')
from utils import helper

import numpy as np

#set password in env first: export YOUR_PASSWORD='your_password'
'''this script must be run from datamover node with omero conda environment activated'''
'''first mount the research drive directly in terminal and then run the script (from sbatch)'''

def main():

    #load in config 
    config_yaml= '/gpfs/home/mh6486/projects/mh6486/FenyoLab/Endometrial/EC_codeximaging/config/config_cellsegmentation_test.yaml'
    run_config = helper.load_yaml_file(config_yaml)
    config = SimpleNamespace(**run_config)

    out_suffix = os.path.basename(config.out_dir)

    omero_table(labels_dir = config.clustering_results_dir, base_dir = config.research_drive_dir, 
                omero_info_dict = config.omero_image_info_dict, n_clusters = config.n_clusters, omero_table_name = config.omero_table_name, omero_table_info = config.omero_table_info,
                samples_to_remove = None, kerberosid = config.kerberosid, out_suffix = out_suffix)

def omero_table(labels_dir, base_dir, omero_info_dict, n_clusters, omero_table_name, omero_table_info, samples_to_remove = None, kerberosid = None, out_suffix = None): 
    #pdb.set_trace()
    #navigate to correct dir on research drive 
    research_drive_dir = f'/mnt/{kerberosid}/{base_dir}/label_images'
    os.chdir(research_drive_dir)
    print(f"Current directory: {os.getcwd()}")
    
    #to save tables with date of run 
    date = "_".join(out_suffix.split("_")[1:])

    password = os.getenv('YOUR_PASSWORD')
    if password is None:
        raise ValueError('No password provided in environment variable YOUR_PASSWORD')
    #print(password)

    sample_names = os.listdir(research_drive_dir) #I'm confused because in research_drive_dir, we have a labels folder but I thought we were generating a new folder with the data... but this folder doesn't have any samples in it!!!
    for sample in sample_names:
        #if sample == '20230922-5689-1P_Scan1':
        if samples_to_remove is not None:
            if sample in samples_to_remove:
                print(f"Skipping sample: {sample}")
                continue
            
        print(f'Processing sample {sample}')

        os.makedirs(sample, exist_ok =True)
        os.chdir(sample)
        print(f"Current directory: {os.getcwd()}")
        #pdb.set_trace()
        roi_value = omero_info_dict.get(sample, {}).get('roi_id')
        #table_path = os.path.join(research_drive_dir, sample, f'metatable_{n_clusters}_{date}.csv')
        table_path = os.path.join(research_drive_dir, sample, f'omerotable_{omero_table_name}.csv')
        print(table_path)

        #identify the clustering results file 
        label_file_persample = [file for file in os.listdir(labels_dir) if sample in file][0]
        label_file_persample_path = os.path.join(labels_dir,label_file_persample)
        print('label path: ', label_file_persample_path)

        if os.path.exists(table_path):
            print('Metatable already generated')
        else:
            create_omero_table(label_file_persample_path, table_path, sample, roi_value, omero_table_info, n_clusters)
            print("omero table created")
        #pdb.set_trace()
        image_id = omero_info_dict.get(sample, {}).get('image_id')
        #table_name = f'cluster_celltype_{n_clusters}_{date}'
        table_name = omero_table_name
            
        ann_id = upload_omero_table(table_path, sample, table_name, image_id, roi_value, kerberosid, password)
        print(f"OMERO table uploaded for {sample}")
        
        os.chdir('..')

def create_omero_table(label, table_path, sample, roi_value, omero_table_info, n_clusters):
   
    label = pd.read_csv(label)
    print(sample, roi_value)

    label_columns = label.columns.drop('Unnamed: 0')  # Drop the 'Unnamed: 0' column

    omero_df = pd.DataFrame({
        'object': range(1,(len(label) + 1)),
        'roi': roi_value,
         **label[label_columns].to_dict(orient='list')  # Convert selected columns to a dict so it can be used here!! keys are column names, and values are lists of column data
        })
    
    print("Omero_df shape:", omero_df.shape)
    #omero_df.to_csv(table_path, index = True)
    omero_df.to_csv(table_path, index = False)

def upload_omero_table(table_path, sample, table_name, image_id, roi_value, kerberosid, password, server="omero.nyumc.org", port=4064):

    ann_id = omero2pandas.upload_table(
        table_path, table_name, 
        links=[("Image", image_id), ("Roi", roi_value)], server="omero.nyumc.org", port=4064, username=kerberosid, password=password)


if __name__ == "__main__":
    main()