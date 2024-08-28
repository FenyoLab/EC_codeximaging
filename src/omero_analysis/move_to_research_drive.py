import subprocess
import shutil
import os
import getpass
from types import SimpleNamespace
import sys

sys.path.append('/gpfs/home/as18894/projects/as18894/FenyoLab/Endometrial/EC_codeximaging')
from utils import helper

'''this script must be run from datamover node with omero conda environment activated'''

def move_to_research_drive(label_images_dir, mount_path, base_dir, kerberosid = None, out_suffix = None):
    if kerberosid is None:
        raise ValueError("Kerberos ID must be provided")
    
    research_drive_dir = f'/mnt/{kerberosid}/{mount_path}'
    mount_command = f'mount {research_drive_dir}'
    mount_fenyolab(mount_command)

    os.chdir(os.path.join(research_drive_dir, base_dir))
    print(f"Current directory: {os.getcwd()}")

    os.makedirs(out_suffix, exist_ok =True)
    os.chdir(out_suffix)
    print(f"Current directory: {os.getcwd()}")

    sample_names = os.listdir(label_images_dir)    
    for sample in sample_names:
        print(f'Processing sample {sample}')

        os.makedirs(sample, exist_ok =True)
        os.chdir(sample)
        print(f"Current directory: {os.getcwd()}")

        backup_path = os.path.join(research_drive_dir, base_dir, out_suffix, sample, 'backup.zarr')
        if os.path.exists(backup_path):
            print('Label image already copied with backup, skipping')
            continue
        
        label_image_path = os.path.join(label_images_dir, sample, 'label_image.zarr')
        copied_label_image_path = os.path.join(research_drive_dir, base_dir, out_suffix, sample, 'label_image.zarr')

        copy_directory(label_image_path, copied_label_image_path)
        copy_directory(copied_label_image_path, backup_path)
        print(f"Label image successfully copied with backup for {sample}")

        os.chdir('..')

def mount_fenyolab(command):
    try:
        result = subprocess.run(
            command,
            shell=True,  # Using shell=True to process the piping
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("Mount successful.")
        else:
            print(f"Mount failed with error:\n{result.stderr}")
    
    except subprocess.CalledProcessError as e:
        print(f"Mount failed with error:\n{e.stderr}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def copy_directory(src, dst):
    try:
        shutil.copytree(src, dst)
        print(f"Copied directory from {src} to {dst}")
    except Exception as e:
        print(f"Error copying directory: {e}")
    
if __name__ == "__main__":
    
    #load in config 
    config_yaml= '/gpfs/home/as18894/projects/as18894/FenyoLab/Endometrial/EC_codeximaging/config/config_cellsegmentation.yaml'
    run_config = helper.load_yaml_file(config_yaml)
    config = SimpleNamespace(**run_config)

    label_images_dir = os.path.join(config.out_dir, config.label_images_dir)
    out_suffix = os.path.basename(config.out_dir)

    move_to_research_drive(label_images_dir = label_images_dir, mount_path = config.mount_lab, base_dir = config.research_drive_dir, 
                            kerberosid = config.kerberosid, out_suffix = out_suffix)
