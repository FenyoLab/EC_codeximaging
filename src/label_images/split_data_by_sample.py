import os
import numpy as np
import pandas as pd

def split_by_sample(segmentation_data_dir, label_images_dir):

    os.makedirs(label_images_dir, exist_ok=True)

    #load in tile info 
    segmentation_masks = np.load(os.path.join(segmentation_data_dir, 'segmentation_masks.npy'))
    tile_positions = np.load(os.path.join(segmentation_data_dir, 'tile_positions.npy'))
    tile_sample_names = np.load(os.path.join(segmentation_data_dir, 'tile_sample_names.npy'))
    metadata = pd.read_csv(os.path.join(segmentation_data_dir, 'metadata.csv'))
    print("Tile data loaded")

    print("Mask shape before swapping axes:", segmentation_masks.shape)
    segmentation_masks = segmentation_masks.swapaxes(1, 2)
    print("Mask shape after swapping axes:", segmentation_masks.shape) #should be the same 

    for sample in np.unique(tile_sample_names):
        sample_dir = os.path.join(label_images_dir, sample)
        os.makedirs(sample_dir, exist_ok=True)
    
        sample_masks_path = os.path.join(sample_dir, 'segmentation_masks.npy')
        if os.path.exists(sample_masks_path):
            print(f'Data already split for sample {sample}, skipping')
            continue
        
        print(f"Processing sample: {sample}")

        slide_indices = np.where(tile_sample_names == sample)[0]
        print(len(slide_indices))

        sample_masks = segmentation_masks[slide_indices]
        sample_tile_positions = tile_positions[slide_indices]

        sample_metadata = metadata[metadata['slide_id'] == sample]
        sample_metadata = sample_metadata.reset_index(drop=True)
        sample_metadata.index += 1
        sample_metadata['label_image_cell_index'] = sample_metadata.index
        sample_metadata_subset = sample_metadata[['cell_label', 'tile_x', 'tile_y', 'slide_id', 'label_image_cell_index']]

        np.save(sample_masks_path, sample_masks)
        np.save(os.path.join(sample_dir, 'tile_positions.npy'), sample_tile_positions)
        sample_metadata_subset.to_csv(os.path.join(sample_dir, 'sample_metadata.csv'), index=False)
        print(f'Data split for sample {sample}')




