import os
import tifffile
import zarr
import pdb
import numpy as np
import dask.array as da

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

    #THIS WORKED WITH 550G!!! WITH fn_short
    # with tifffile.TiffFile(input_file) as tif:
    #     dask_img = da.from_array(tif.asarray(), chunks=(12, 1000, 1000))  # Adjust chunk size based on your system's memory
    # pdb.set_trace()

    # Read the TIFF file... this works if the data is not too big!
    with tifffile.TiffFile(input_file) as tif:
        img_data = tif.asarray().astype(int)

    with open(output_channel_file, 'w') as file:
        file.write('channel,marker\n')
        for channel, marker in enumerate(channels):
            file.write(f'{channel},{marker}\n')

    #print("zarr path: ", output_zarr)
    # Convert to Zarr Array
    zarr.array(img_data, chunks=chunk_size, store=output_zarr)
    
    #pdb.set_trace()
    # tile_size = 100  # Define the size of each tile

    # with tifffile.TiffFile(input_file) as tif:
    #     image_shape = tif.pages[0].shape
    #     num_channels = len(tif.pages)  # Number of channels (pages)
       
    #     for y in range(0, image_shape[0], tile_size):
    #         for x in range(0, image_shape[1], tile_size):
    #             tile_list = []
    #             # Read the tile for each channel without loading the entire image
    #             for channel in range(len(channels)):
    #                 print(channel)
    #                 page = tif.pages[channel]
    #                 # Load the entire page (channel) and extract the tile region
    #                 full_page = page.asarray()
    #                 tile_channel = full_page[y:y+tile_size, x:x+tile_size]
    #                 tile_list.append(tile_channel)
                    
    #             pdb.set_trace()
    #             # Stack the channels to form a 3D array (tile_size x tile_size x num_channels)
    #             tile = np.stack(tile_list, axis=-1)
        
    #             print(f'Processing tile at x: {x}, y: {y}')
    # pdb.set_trace()

    # tile_size = 100  # Define the size of each tile
    # num_channels = len(channels)

    # # Get the shape of the first page (assuming all channels have the same dimensions)
    # with tifffile.TiffFile(input_file) as tif:
    #     image_shape = tif.pages[0].shape

    # # Create a Zarr array with the appropriate shape
    # zarr_shape = (num_channels, image_shape[0], image_shape[1])  # (channels, height, width)
    # zarr_array = zarr.zeros(zarr_shape, dtype=np.int32, chunks=(num_channels, tile_size, tile_size), store=output_zarr)

    # # Read all channels into memory
    # with tifffile.TiffFile(input_file) as tif:
    #     full_pages = [page.asarray() for page in tif.pages]  # Read all channels at once

    # # Loop over the image in tiles
    # for y in range(0, image_shape[0], tile_size):
    #     for x in range(0, image_shape[1], tile_size):
    #         # Define the tile boundaries
    #         tile_y_end = min(y + tile_size, image_shape[0])
    #         tile_x_end = min(x + tile_size, image_shape[1])

    #         # Process each channel
    #         for channel in range(num_channels):
    #             # Extract the tile for the current channel
    #             tile_channel = full_pages[channel][y:tile_y_end, x:tile_x_end]
                
    #             # Store the tile in the corresponding location in the Zarr array
    #             zarr_array[channel, y:tile_y_end, x:tile_x_end] = tile_channel

    #         print(f'Processed tile at x: {x}, y: {y}')

    # pdb.set_trace()

    # tile_size = 100  # Define the size of each tile
    # num_channels = len(channels)

    # # Get the shape of the first page (assuming all channels have the same dimensions)
    # with tifffile.TiffFile(input_file) as tif:
    #     image_shape = tif.pages[0].shape

    # # Create a Zarr array with the appropriate shape
    # zarr_shape = (num_channels, image_shape[0], image_shape[1])  # (channels, height, width)
    # zarr_array = zarr.zeros(zarr_shape, dtype=np.int32, chunks=(num_channels, tile_size, tile_size), store=output_zarr)

    # # Check if channels match the number of channels provided
    # #assert image_shape[0] == len(channels), f'Number of channels in the file does not match the number of channels provided. File has {image_shape[0]} channels and {len(channels)} channels were provided.'

    # # Write channel information to a CSV file
    # with open('output_channel_file.csv', 'w') as file:
    #     file.write('channel,marker\n')
    #     for channel, marker in enumerate(channels):
    #         file.write(f'{channel},{marker}\n')
    
    # # Loop over the image in tiles
    # with tifffile.TiffFile(input_file) as tif:
    #     for y in range(0, image_shape[0], tile_size):
    #         for x in range(0, image_shape[1], tile_size):
    #             # Read the tile for each channel and write it to the Zarr array
    #             for channel in range(num_channels):
    #                 print(channel)
    #                 page = tif.pages[channel]
    #                 full_page = page.asarray()
    #                 tile_channel = full_page[y:y+tile_size, x:x+tile_size]
                    
    #                 # Store the tile in the corresponding location in the Zarr array
    #                 zarr_array[channel, y:y+tile_size, x:x+tile_size] = tile_channel

    #             print(f'Processed tile at x: {x}, y: {y}')

    # pdb.set_trace()

    # # Check if channels matches the number of channels given
    # assert img_data.shape[0] == len(channels), f'Number of channels in the file does not match the number of channels provided. File has {len(img_data.shape)} channels and {len(channels)} channels were provided.'

    # with open(output_channel_file, 'w') as file:
    #     file.write('channel,marker\n')
    #     for channel, marker in enumerate(channels):
    #         file.write(f'{channel},{marker}\n')

    # # Convert to Zarr Array
    # zarr.array(img_data, chunks=chunk_size, store=output_zarr)
    #print(f'Successfully converted {file_name}.{input_ext} to zarr')
