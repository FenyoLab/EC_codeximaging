import os 
import subprocess
import sys

import numpy as np
from src.label_images.csv_input.create_ome_csv import create_ome_csv

def omero_label_image(omero_dir, base_dir, seg_data_path, image_id_dict, channel_names, tile_size = 256):
    '''Function to upload label images from a csv input to OMERO, also creates a marker intensity omero table
    Inputs: omero_dir - str, path to omero save location
            base_dir - str, path to the research drive for back up
            seg_data_path - str, path to the segmentation data
            image_id_dict - dict, dictionary with image ids for each sample
            channel_names - list of str, names of the channels
            tile_size - int, size of the tiles'''

    # Get env variables 
    password = os.getenv('PASSWORD')
    kerberosid = os.getenv('USER')

    if password is None:
        raise ValueError('No password provided in environment variable PASSWORD')
    elif kerberosid is None:
        raise ValueError('No kerberos provided in environment variable USER')

    # Defines research drive path where the csv input will be saved
    research_drive_dir = f'/mnt/{kerberosid}/{base_dir}'
    print(f"Current directory: {os.getcwd()}")
    os.chdir(research_drive_dir)
    print(f"Current directory: {os.getcwd()}")

    print("Logging into omero")
    omero_login(kerberosid, password)

    # Loop through each sample
    # cell_sample_names = np.load(os.path.join(seg_data_path, 'cell_sample_names.npy'))
    # for sample in np.unique(cell_sample_names):
    for sample in image_id_dict:
        # Create dir in research drive for each sample and cd into it
        sample_research_drive_path = os.path.join(research_drive_dir, sample)
        os.makedirs(sample_research_drive_path, exist_ok =True)
        os.chdir(sample_research_drive_path)
        print(f"Current directory: {os.getcwd()}")

        # Create csv input to create label image
        table_filename = create_ome_csv(sample, seg_data_path, sample_research_drive_path, channel_names)

        # Define additional variables for roi_converter_ngff
        roi_name = 'cell_label_image_csv'
        table_name = 'marker_intensities'
        zarr_filename = 'csv_tile_mask'
        image_id = image_id_dict.get(sample, {}).get('image_id')
        server_directory = os.path.join('/omero', omero_dir, sample)

        label_image_zarr = os.path.join(sample_research_drive_path, f'{zarr_filename}.zarr')
        if os.path.exists(label_image_zarr):
            print(f"Label image zarr file already exists for {sample}. Skipping upload.")
            continue

        print(f"Uploading label image with roi_converter_ngff")
        try:
            print(image_id)
            run_roi_converter_ngff(table_filename, zarr_filename, tile_size, image_id, kerberosid, password, roi_name, server_directory, table_name)
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)

    del password

def omero_login(user, password, server="omero.nyumc.org", port_number=4064, group_id="fenyolab-cg-01"):

    # Log into OMERO
    login_command = f'omero login -u {user} -w {password} -s {server} -p {port_number} -g {group_id}'
    result = subprocess.call(login_command, shell=True, executable='/bin/bash')

    # Check if the login was successful
    if result != 0:
        print("OMERO login failed.")
        sys.exit("Terminating script due to unsuccessful login.")
    


def run_roi_converter_ngff(table_filename, zarr_filename, tile_size, image_id, kerberosid, password, roi_name, server_directory, table_name, server="omelpdcpvm01.nyumc.org", port=4064):
    command = f'ROI_Converter_NGFF --input_file {table_filename} --output_filename {zarr_filename} --tile_size {tile_size} --register_to {image_id} --server {server} --port {port} --user {kerberosid} --password {password} --table --name {roi_name} --server_directory {server_directory} --table_name {table_name}'
    print(command)
    subprocess.call(command, shell=True, executable='/bin/bash')
