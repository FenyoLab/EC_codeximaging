import os
import numpy as np
import pandas as pd
import zarr 
import tifffile as tiff
import matplotlib.pyplot as plt

def main():
    data_dir = '/gpfs/data/proteomics/projects/Endometrial_mIF/EC_codeximaging_results/out_256/data'
    label_images_dir = '/gpfs/data/proteomics/projects/Endometrial_mIF/EC_codeximaging_results/label_images'

    create_tile_label_image(data_dir, label_images_dir)

def create_tile_label_image(data_dir, label_images_dir, tiles_dir='tiles_11_13', tile_size=256):

    for sample in os.listdir(label_images_dir):
        sample_dir = os.path.join(label_images_dir, sample)
        image_dir = os.path.join(data_dir, sample)
        
        label_image_path = os.path.join(sample_dir, 'tile_label_image.tiff') #if matrix already exists, skip
        #if os.path.exists(label_image_path):
        #    print(f'Tile label image already exists for sample {sample}, skipping')
        #    continue
        
        print(f"Processing sample: {sample}")

        zarr_img = zarr.open(os.path.join(data_dir, sample, 'data.zarr'), mode='r')
        print("Original image shape:", zarr_img.shape)

        label_image = np.zeros(zarr_img.shape[1:], dtype=np.uint32)
        print("Label image shape:", label_image.shape)

        tile_positions_df = pd.read_csv(os.path.join(data_dir, sample, tiles_dir, 'positions_256.csv'), index_col=0)
        tile_positions_df.index += 1 #add 1 to index

        for tile_index, (h, w) in tile_positions_df.iterrows():
            label_image[h:h + tile_size, w:w + tile_size] = tile_index

        tiff.imwrite(label_image_path, label_image)
        print(f'Tile label image created for sample {sample}')
        print('')

if __name__ == '__main__':
    main()