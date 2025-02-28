import os
import tifffile
import zarr
import pdb
import numpy as np

def tiff_to_zarr(input_path, output_path, file_name, input_ext, common_channels, chunk_size=(None, 256, 256)):
    # Create zarr file and channel.csv for each sample
    input_file = f'{input_path}/{file_name}.{input_ext}'
    output_file_path = f'{output_path}/{file_name}'
    os.makedirs(output_file_path, exist_ok=True)
    output_zarr = f'{output_file_path}/data.zarr'
    print(output_zarr)
    if os.path.exists(output_zarr): # Skip if already exists
        print(f'Zarr file already exists at {output_zarr}')
        return 

    # Process channel
    input_channel_file = f'{input_path}/{file_name}.txt'
    output_channel_file = f'{output_file_path}/channels.csv'
    if os.path.exists(input_channel_file): # Check if channel file exists
        with open(input_channel_file, 'r') as f:
            if common_channels is not None:
                print(f'WARNING: Channels provided in the function will be ignored as channel file exists at {input_channel_file}')
            channels = f.read().splitlines()
            print(f'Custom channels: {channels}')
    else:
        channels = common_channels

    # Read the TIFF file... this works if the data is not too big!
    with tifffile.TiffFile(input_file) as tif:
        img_data = tif.asarray().astype(int)

    with open(output_channel_file, 'w') as file:
        file.write('channel,marker\n')
        for channel, marker in enumerate(channels):
            file.write(f'{channel},{marker}\n')

    # Convert to Zarr Array
    zarr.array(img_data, chunks=chunk_size, store=output_zarr)
