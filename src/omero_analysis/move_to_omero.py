import os
import getpass
import shutil
import subprocess
import sys
import getpass
import pdb

from types import SimpleNamespace

sys.path.append('../..')
from utils import helper
#sys.path.append('src/omero_analysis')

'''this script must be run from datamover node with omero conda environment activated'''
'''first mount the research drive directly in terminal and then run the script (from sbatch)'''

def main():
    #load in config 
    config_yaml= '/gpfs/home/mh6486/projects/mh6486/FenyoLab/Endometrial/EC_codeximaging/config/config_cellsegmentation_test.yaml'
    run_config = helper.load_yaml_file(config_yaml)
    config = SimpleNamespace(**run_config)

    label_images_dir = os.path.join(config.out_dir, config.label_images_dir)
    out_suffix = os.path.basename(config.out_dir)

    move_label_images_to_omero(label_images_dir = label_images_dir, base_dir = config.research_drive_dir, 
                            image_id_dict = config.omero_image_info_dict, kerberosid = config.kerberosid)

def move_label_images_to_omero(label_images_dir, base_dir, image_id_dict, kerberosid = None, out_suffix = "label_images"):
    research_drive_dir = f'/mnt/{kerberosid}/{base_dir}'
    print(research_drive_dir)
    
    os.chdir(research_drive_dir)

    os.makedirs(out_suffix, exist_ok =True)
    os.chdir(out_suffix)
    print(f"Current directory: {os.getcwd()}")

    password = os.getenv('YOUR_PASSWORD')
    if password is None:
        raise ValueError('No password provided in environment variable YOUR_PASSWORD')

    print("Logging into omero")
    omero_login(kerberosid, password)

    sample_names = os.listdir(label_images_dir)  
    for sample in sample_names:
        print(f'Processing sample {sample}')

        os.makedirs(sample, exist_ok =True)
        os.chdir(sample)
        print(f"Current directory: {os.getcwd()}")

        original_label_image_path = os.path.join(label_images_dir, sample, 'label_image.zarr')
        copied_label_image_path = os.path.join(research_drive_dir, out_suffix, sample, 'label_image.zarr')
        backup_path = os.path.join(research_drive_dir, out_suffix, sample, 'backup.zarr')
        
        if os.path.exists(backup_path):
            print('Label image already exists, skipping')
        else:
            copy_directory(original_label_image_path, copied_label_image_path)
            copy_directory(copied_label_image_path, backup_path)
            print(f"Label image successfully copied with backup for {sample}")

        labels_path = os.path.join('label_image.zarr', '0', 'labels')
        zero_path = os.path.join('label_image.zarr', '0', '0')

        # Check which directory exists and perform actions accordingly
        if os.path.isdir(labels_path):
            print(f"Label image already uploaded to omero with roi_converter_ngff")
        
        elif os.path.isdir(zero_path):
            print(f"Uploading label image with roi_converter_ngff")
            image_name = f'raw_cell_label_image'
            image_id = image_id_dict.get(sample, {}).get('image_id')
            print(sample, image_id)
            server_directory = os.path.join('/omero', base_dir, out_suffix, sample)
            print(server_directory)

            try:
                run_roi_converter_ngff(image_id, image_name, kerberosid, password, server_directory)
                print(f"Label image for sample {sample} has been successfully imported into OMERO")
            except Exception as e:
                print(f"Error: {e}")
                sys.exit(1)

        os.chdir('..')

def copy_directory(source, destination):
    try:
        shutil.copytree(source, destination)
        print(f"Copied directory from {source} to {destination}")
    except Exception as e:
        print(f"Error copying directory: {e}")
        sys.exit("Terminating script due to error in copying directory.")
    
def omero_login(user, password, server="omero.nyumc.org", port_number=4064):

    # Log into OMERO
    login_command = f'omero login -u {user} -w {password} -s {server} -p {port_number}'
    result = subprocess.call(login_command, shell=True, executable='/bin/bash')
    del password

    # Check if the login was successful
    if result != 0:
        print("OMERO login failed.")
        sys.exit("Terminating script due to unsuccessful login.")

def run_roi_converter_ngff(image_id, name, kerberosid, password, server_directory, server="omelpdcpvm01.nyumc.org", port=4064):

    command = f'ROI_Converter_NGFF -i label_image.zarr/0 -r {image_id} -n {name} --server {server} --port {port} --user {kerberosid} --server_directory {server_directory} --password {password}'
    subprocess.call(command, shell=True, executable='/bin/bash')
    del password 

    
if __name__ == '__main__':
    main()
    

