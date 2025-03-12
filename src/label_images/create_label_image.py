import os
import numpy as np
import pandas as pd
import zarr 
import tifffile as tiff
import matplotlib.pyplot as plt

def create_label_image(data_dir, label_images_dir, label_image_name = 'label_image'):
    # Iterate through all samples in the label_images_dir
    for sample in os.listdir(label_images_dir):
        sample_dir = os.path.join(label_images_dir, sample)
        image_dir = os.path.join(data_dir, sample)
        
        label_image_path = os.path.join(sample_dir, f'{label_image_name}.tiff') # If label image already exists, skip
        if os.path.exists(label_image_path):
            print(f'Label image already exists for sample {sample}, skipping')
            continue
        
        print(f"Processing sample: {sample}")

        # These functions are run on 1 sample at a time
        create_label_tiles(sample_dir)
        create_label_slide(sample_dir, image_dir, label_image_name)
        print(f'Label image created for sample {sample}')

def create_label_tiles(label_images_dir):
    '''Function to update the cell masks with the label image cell index so each cell in the final label image has a unique id'''
    # Load cell masks, tile positions and metadata 
    masks = np.load(os.path.join(label_images_dir, 'segmentation_masks.npy'))
    print("Cell masks shape:", masks.shape)

    tile_positions = np.load(os.path.join(label_images_dir, 'tile_positions.npy'))
    print("Tile positions shape:", tile_positions.shape)

    metadata = pd.read_csv(os.path.join(label_images_dir, 'sample_metadata.csv'))

    # Initialize list to store updated masks
    updated_masks = []

    # Iterate through each tile and update the cell masks
    for i, mask in enumerate(masks):
        tile_position = tile_positions[i]
        # To get only the cells on that tile 
        filtered_metadata = metadata[
            (metadata['tile_h'] == tile_position[0]) & 
            (metadata['tile_w'] == tile_position[1])]

        # Create a dictionary to map cell id to label image cell index
        cell_to_label = dict(zip(filtered_metadata['cell_label'], filtered_metadata['label_image_cell_index']))
    
        # Function to replace cell id with label image cell index
        def replace_cell_id(cell_id):
            return cell_to_label.get(cell_id, 0)  # Return 0 if cell_id is not in the dictionary
    
        # Vectorize the function to apply it to the entire mask
        vectorized_replace = np.vectorize(replace_cell_id)
        # Apply the function to the mask
        updated_mask = vectorized_replace(mask)

        # Append the updated mask to the list
        updated_masks.append(updated_mask)

        if i % 500 == 0:
            print(i, tile_position, filtered_metadata.shape)

    # Save the updated masks as a numpy array - used to create label imagee  
    updated_masks_arr = np.array(updated_masks)
    print("# of unique values in updated mask:", len(np.unique(updated_masks_arr)))   
    print("Label masks shape:", updated_masks_arr.shape)
    np.save(os.path.join(label_images_dir, 'label_tiles.npy'), updated_masks_arr)

def create_label_slide(label_images_dir, data_dir, label_image_name):
    '''Function to create the final label image from the label tiles by placing them in the correct position'''
    # Load original image
    zarr_img = zarr.open(os.path.join(data_dir, 'data.zarr'), mode='r')
    print("Original image shape:", zarr_img.shape)

    # Load label tiles and tile positions
    label_tiles = np.load(os.path.join(label_images_dir, 'label_tiles.npy'))
    print("Label masks shape:", label_tiles.shape)
    tile_positions = np.load(os.path.join(label_images_dir, 'tile_positions.npy'))
    print("Tile positions shape:", tile_positions.shape)

    # Create blank label image
    label_image = np.zeros(zarr_img.shape[1:], dtype=np.uint16)
    print("Blank label image shape:", label_image.shape)

    # Place label tiles in correct position
    for i, tile_mask in enumerate(label_tiles):
        h, w = tile_positions[i]
        label_image[h:h+tile_mask.shape[0], w:w+tile_mask.shape[1]] = tile_mask

        if i % 500 == 0:
            print(f'Tile {i}: {h}, {w}')
    
    print("Label image shape:", label_image.shape)
    print("# of Unique values in label image:", len(np.unique(label_image)))
    print("datatype", type(label_image[0][0]))
    label_image = label_image.astype(np.uint16)
    print("datatype", type(label_image[0][0]))

    # Save the slide mask as tiff
    tiff.imwrite(os.path.join(label_images_dir, f'{label_image_name}.tiff'), label_image)
    print("Label image saved as tiff")
