import os
import sys
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import zarr

from types import SimpleNamespace
sys.path.append('/gpfs/home/as18894/projects/as18894/FenyoLab/Endometrial/EC_codeximaging')
from utils import helper

def main():
    #import config
    config_yaml= '/gpfs/home/as18894/projects/as18894/FenyoLab/Endometrial/EC_codeximaging/config/config_cellphenotyping.yaml'
    run_config = helper.load_yaml_file(config_yaml)
    config = SimpleNamespace(**run_config)

    cell_types_dir = os.path.join(config.out_dir, config.celltypes_dir, f'{config.n_clusters_celltypes}_clusters')
    distributions_dir = os.path.join(cell_types_dir, 'celltype_distributions')
    metadata_path = os.path.join(config.segmentation_data_dir, 'metadata.csv')
    cell_types_df_path = os.path.join(cell_types_dir, 'cell_types_v2.csv')
    image_dir = config.data_dir

    markers = config.mixed_celltype_markers
    channel_names = config.all_channel_names
    
    visualize_cells(distributions_dir, metadata_path, cell_types_df_path, image_dir, markers, channel_names)

def visualize_cells(distributions_dir, metadata_path,  cell_types_df_path, image_dir, markers, channel_names): #channel names should be all 36

    metadata = pd.read_csv(metadata_path, index_col=0)
    metadata.index = metadata.index + 1
    cell_types_df = pd.read_csv(cell_types_df_path, index_col=0)
    
    for sample in os.listdir(distributions_dir):

        #load mixed celltypes dir
        mixed_celltypes_df_path = os.path.join(distributions_dir, sample, 'mixed_celltypes.csv')
        if not os.path.exists(mixed_celltypes_df_path):
            print(f'No mixed celltypes data for {sample}')
            continue
        
        print(f'Processing sample {sample}')

        zarr_img = zarr.open(os.path.join(image_dir, sample, 'data.zarr'), mode = 'r')
        print('Zarr img shape:', zarr_img.shape)

        mixed_celltypes_df = pd.read_csv(mixed_celltypes_df_path, index_col=0)
        print('Mixed celltypes df shape:', mixed_celltypes_df.shape)

        for marker in markers:
            if marker not in mixed_celltypes_df.columns:
                print(f'No data for {marker} in {sample}')
                continue
            
            print(f'Processing marker {marker}')
            #marker save path
            marker_save_path = os.path.join(distributions_dir, sample, marker)
            os.makedirs(marker_save_path, exist_ok=True)

            marker_data = mixed_celltypes_df[marker].dropna()
            marker_percentiles = mixed_celltypes_df[f'{marker}_percentile'].dropna()

            print(marker_data.shape)
            print(marker_percentiles.shape)

            data_by_percentile = {
                percentile: marker_data[marker_percentiles == percentile]
                for percentile in marker_percentiles.unique()
            }

            for percentile, data_in_percentile in data_by_percentile.items():
                percentile_new = set_percentile(percentile)

                print(f'{marker}: Percentile {percentile_new}, Num cells: {len(data_in_percentile)}')

                fig, axs = plt.subplots(4, 5, figsize=(20, 15))
                fig.suptitle(f'Sample: {sample}, Marker: {marker}, Percentile: {percentile_new}, Num cells: {len(data_in_percentile)}')

                n_values = min(len(data_in_percentile), 20)

                for i in range(n_values):
                    marker_value = data_in_percentile.iloc[i] 
                    cell_info = metadata.loc[data_in_percentile.index[i]]
                    cell_type_info = cell_types_df.loc[data_in_percentile.index[i]]

                    centroid_x = cell_info['centroid_x']
                    centroid_y = cell_info['centroid_y']

                    tile_h = cell_info['tile_h']
                    tile_w = cell_info['tile_w']

                    #get the tile from zarr image and plot it in the corresponding subplot
                    tile_dapi = zarr_img[channel_names.index('DAPI'), tile_h:tile_h + 256, tile_w:tile_w + 256]
                    tile_marker = zarr_img[channel_names.index(marker), tile_h:tile_h + 256, tile_w:tile_w + 256]
                    
                    tile_dapi = tile_dapi / tile_dapi.max()
                    tile_marker = tile_marker / tile_marker.max()

                    rgb_tile = np.zeros((tile_dapi.shape[0], tile_dapi.shape[1], 3), dtype=np.float32)
                    rgb_tile[..., 1] = tile_marker  # Green channel for the marker
                    rgb_tile[..., 2] = tile_dapi    # Blue channel for the DAPI
                
                    axs[i//5, i%5].imshow(rgb_tile)
                    axs[i//5, i%5].scatter(centroid_y, centroid_x, c='red', s=7) #plot white dot on centroid
                    axs[i//5, i%5].axis('off')
                    axs[i//5, i%5].set_title(f'H: {tile_h}, W: {tile_w}, Value: {marker_value:.2f}')

                for j in range(n_values, 20):
                    fig.delaxes(axs[j//5, j%5])

                plt.tight_layout()
                plt.savefig(os.path.join(marker_save_path, f'{percentile_new}.png'))
                plt.close()

def set_percentile(percentile):
    if percentile == 0:
        return '<5'
    elif percentile == 5:
        return '5-25'
    elif percentile == 25:
        return '25-50'
    elif percentile == 50:
        return '50-75'
    elif percentile == 75:
        return '75-95'
    elif percentile == 95:
        return '>95'

if __name__ == '__main__':
    main()