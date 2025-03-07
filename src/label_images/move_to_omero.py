import os
import getpass
import shutil
import subprocess
import sys
import getpass

def move_label_images_to_omero(label_images_dir, base_dir, image_id_dict, label_image_dir_name = "label_images", image_name = 'label_image', date = None):
    password = os.getenv('PASSWORD')
    kerberosid = os.getenv('KERBEROSID')

    if password is None:
        raise ValueError('No password provided in environment variable PASSWORD')
    elif kerberosid is None:
        raise ValueError('No kerberos provided in environment variable KERBEROSID')
    
    research_drive_dir = f'/mnt/{kerberosid}/{base_dir}'
    print(research_drive_dir)
    os.chdir(research_drive_dir)

    os.makedirs(label_image_dir_name, exist_ok =True)
    os.chdir(label_image_dir_name)
    print(f"Current directory: {os.getcwd()}")

    print("Logging into omero")
    omero_login(kerberosid, password)

    sample_names = os.listdir(label_images_dir)  
    for sample in sample_names:
        print(f'Processing sample {sample}')

        sample_dir = f'{sample}_{date}' # Add date to dir name for sample to preserve dir structure 
        os.makedirs(sample_dir, exist_ok =True)
        os.chdir(sample_dir)
        print(f"Current directory: {os.getcwd()}")

        original_label_image_path = os.path.join(label_images_dir, sample, f'{image_name}.zarr')
        copied_label_image_path = os.path.join(research_drive_dir, label_image_dir_name, sample_dir, f'{image_name}.zarr')
        backup_path = os.path.join(research_drive_dir, label_image_dir_name, sample_dir, 'backup.zarr')
        
        if os.path.exists(backup_path):
            print('Label image already exists, skipping')
        else:
            copy_directory(original_label_image_path, copied_label_image_path)
            copy_directory(copied_label_image_path, backup_path)
            print(f"Label image successfully copied with backup for {sample}")

        labels_path = os.path.join(f'{image_name}.zarr', '0', 'labels')
        zero_path = os.path.join(f'{image_name}.zarr', '0', '0')

        # Check which directory exists and perform actions accordingly
        if os.path.isdir(labels_path):
            print(f"Label image already uploaded to omero with roi_converter_ngff")
        
        elif os.path.isdir(zero_path):
            print(f"Uploading label image with roi_converter_ngff")
            image_id = image_id_dict.get(sample, {}).get('image_id')
            print(sample, image_id)
            server_directory = os.path.join('/omero', base_dir, label_image_dir_name, sample_dir)
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

def run_roi_converter_ngff(image_id, image_name, kerberosid, password, server_directory, server="omelpdcpvm01.nyumc.org", port=4064):
    command = f'ROI_Converter_NGFF -i {image_name}.zarr/0 -r {image_id} -n {image_name} --server {server} --port {port} --user {kerberosid} --server_directory {server_directory} --password {password}'
    subprocess.call(command, shell=True, executable='/bin/bash')
    del password 

if __name__ == '__main__':
    main()
