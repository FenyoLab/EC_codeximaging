import os
import subprocess 

def convert_tiff_to_zarr(label_images_dir, tiff_file='label_image.tiff', zarr_file='label_image.zarr'): #samples_to_remove = None,
    """
    Converts TIFF files to Zarr format in the specified directory.
    Parameters:
    - label_images_dir: str : Directory containing the sample subdirectories with TIFF images.
    - tiff_file: str : Name of the input TIFF file. 
    - zarr_file: str : Name of the output Zarr file.
    """
    sample_names = os.listdir(label_images_dir)

    for sample in sample_names:
        print("Processing sample", sample)
        image_path = os.path.join(label_images_dir, sample)
        
        if not os.path.isdir(image_path):
            continue  # Skip this loop iteration if not a directory 

        os.chdir(image_path)
        if os.path.isfile(tiff_file):  # Check if the TIFF file exists
            if not os.path.exists(zarr_file):  # Check if the Zarr file exists; skip if it was already generated
                print("Converting TIFF to Zarr...")
                # Define the bash command
                bash_command = f'bioformats2raw {tiff_file} {zarr_file}'
                try:
                    # Run the bash command
                    subprocess.run(bash_command, shell=True, check=True)
                    print(f"Successfully converted {os.path.join(image_path, tiff_file)} to a Zarr file")
                except subprocess.CalledProcessError as e:
                    print(f"Error running command on {os.path.join(image_path, tiff_file)}: {e}")
            else:
                print(f"{os.path.join(image_path, zarr_file)} already exists")
        else:
            print(f"{os.path.join(image_path, tiff_file)} does not exist")