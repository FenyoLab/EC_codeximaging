import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import zarr
from skimage.transform import resize
from skimage.io import imsave

def create_thumbnail_from_tile_positions(data_dir, tile_dir, tile_size=256):
    
    for sample in os.listdir(data_dir):
        if sample == 'common_channels.txt' or sample == 'common_channels_cell_segmentation.txt':
            continue
        print(f'Creating thumbnail for sample {sample}')
        
        # Load in tile positions
        tile_positions = pd.read_csv(os.path.join(data_dir, sample, tile_dir, f'positions_{tile_size}.csv'))

        # Open slide - zarr data  
        slide_path = f'{data_dir}/{sample}/data.zarr'
        print('Reading slide metadata...')
        slide = zarr.open(slide_path, mode='r')  # Opens the Zarr array in read-only mode
        print(f'Slide_shape: {slide.shape}')

        _, slide_height, slide_width = slide.shape
        grid_height, grid_width = slide_height // tile_size, slide_width // tile_size
        bw_mask = np.zeros((slide_height, slide_width), dtype=np.uint8)

        for _, pos in tile_positions.iterrows(): 
            h = pos['h'] 
            w = pos['w'] 
            bw_mask[h:h+tile_size, w:w+tile_size] = 1  # Set the tile area in bw_mask to 1
        
        bw_mask = resize(bw_mask, (grid_height, grid_width), order=0, anti_aliasing=False)
        img = (np.clip(bw_mask, 0, 1) * 255).astype(np.uint8)
        save_path = os.path.join(data_dir, sample, f'{tile_dir}_roi_img')
        os.makedirs(save_path, exist_ok=True)
        imsave(os.path.join(save_path, f'tile_img_{tile_size}.png'), img)
        print(f'Thumbnail saved as img for sample {sample}')
