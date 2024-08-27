import os
import numpy as np
import pandas as pd

def split_by_sample(tile_dir, metadata_path, label_images_dir, data_dir, samples_to_remove= None):

    os.makedirs(label_images_dir, exist_ok=True)

    #load in tile info and metadata
    segmentation_masks = np.load(os.path.join(tile_dir, 'segmentation_masks.npy'))
    tile_positions = np.load(os.path.join(tile_dir, 'tile_positions.npy'))
    tile_sample_names = np.load(os.path.join(tile_dir, 'tile_sample_names.npy'))
    #metadata = pd.read_csv(os.path.join(tile_dir, 'metadata.csv'))
    metadata = pd.read_csv(metadata_path)
    print("Masks and metadata loaded")

    print("Mask shape before swapping axes:", segmentation_masks.shape)
    segmentation_masks = segmentation_masks.swapaxes(1, 2)
    print("Mask shape after swapping axes:", segmentation_masks.shape) #should be the same 

    unique_sample_names = os.listdir(data_dir)

    for sample in unique_sample_names:
        if sample in samples_to_remove:
            print(f"Skipping sample: {sample}")
            continue
        if sample == 'common_channels.txt':
            continue

        print(f"Processing sample: {sample}")
        
        sample_dir = os.path.join(label_images_dir, sample)
        os.makedirs(sample_dir, exist_ok=True)
        
        sample_metadata_path = os.path.join(sample_dir, 'sample_metadata.csv') #if sample_metadata already exists, skip this sample
        if os.path.exists(sample_metadata_path):
            print('Metadata already exists for this sample, skipping')
            continue

        slide_indices = np.where(tile_sample_names == sample)[0]
        print(len(slide_indices))

        sample_masks = segmentation_masks[slide_indices]
        sample_tile_positions = tile_positions[slide_indices]
        sample_metadata = metadata[metadata['slide_id'] == sample]
        sample_metadata = sample_metadata.reset_index(drop=True)
        sample_metadata.index += 1
        sample_metadata['label_image_cell_index'] = sample_metadata.index
        print(sample_metadata.head()) #will display 5 rows (default)

        sample_metadata.to_csv(sample_metadata_path, index=False)
        np.save(os.path.join(sample_dir, 'segmentation_masks.npy'), sample_masks)
        np.save(os.path.join(sample_dir, 'tile_positions.npy'), sample_tile_positions)
    
    print('All Data Split by Sample')




