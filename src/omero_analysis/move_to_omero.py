import os
import getpass
import shutil
import subprocess
import sys
import getpass

from types import SimpleNamespace

sys.path.append('../..')
from utils import helper
#sys.path.append('src/omero_analysis')

'''this script must be run from datamover node with omero conda environment activated'''
'''first mount the research drive directly in terminal and then run the script (from sbatch)'''

def main():
    #load in config 
    config_yaml= '/gpfs/home/as18894/projects/as18894/FenyoLab/Endometrial/EC_codeximaging/config/config_cellsegmentation.yaml'
    run_config = helper.load_yaml_file(config_yaml)
    config = SimpleNamespace(**run_config)

    label_images_dir = os.path.join(config.out_dir, config.label_images_dir)
    out_suffix = os.path.basename(config.out_dir)

    move_label_images_to_omero(label_images_dir = label_images_dir, mount_path = config.mount_lab, base_dir = config.research_drive_dir, 
                            image_id_dict = config.omero_image_id_dict, kerberosid = config.kerberosid, out_suffix = out_suffix)

def move_label_images_to_omero(label_images_dir, mount_path, base_dir, image_id_dict, kerberosid = None, out_suffix = None):
    
    research_drive_dir = f'/mnt/{kerberosid}/{mount_path}'

    os.chdir(os.path.join(research_drive_dir, base_dir))
    os.makedirs(out_suffix, exist_ok =True)
    os.chdir(out_suffix)
    print(f"Current directory: {os.getcwd()}")
    date = "_".join(out_suffix.split("_")[1:])

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

        copied_label_image_path = os.path.join(research_drive_dir, base_dir, out_suffix, sample, 'label_image.zarr')
        if os.path.exists(copied_label_image_path):
            print('Label image already exists, skipping')
            continue
        
        original_label_image_path = os.path.join(label_images_dir, sample, 'label_image.zarr')
        backup_path = os.path.join(research_drive_dir, base_dir, out_suffix, sample, 'backup.zarr')

        copy_directory(original_label_image_path, copied_label_image_path)
        copy_directory(copied_label_image_path, backup_path)
        print(f"Label image successfully copied with backup for {sample}")

        image_name = f'raw_cell_label_image'
        print(image_name)
        server_directory = os.path.join('/omero', mount_path, base_dir, out_suffix, sample)
        print(server_directory)
        run_roi_converter_ngff(image_id_dict.get(sample), image_name, kerberosid, password, server_directory)
        print(f"Label image for sample {sample} has been succesfully imported into omero")

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
    

