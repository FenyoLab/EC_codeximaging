import os
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import sys
import json 

from types import SimpleNamespace
sys.path.append('/gpfs/home/as18894/projects/as18894/FenyoLab/Endometrial/EC_codeximaging')
from utils import helper

def main():
    #import config
    config_yaml= '/gpfs/home/as18894/projects/as18894/FenyoLab/Endometrial/EC_codeximaging/config/config_cellphenotyping.yaml'
    run_config = helper.load_yaml_file(config_yaml)
    config = SimpleNamespace(**run_config)

    #function paths
    celltypes_dir = os.path.join(config.out_dir, config.celltypes_dir, f'{config.n_clusters_celltypes}_clusters')
    matrix_dir = os.path.join(config.out_dir, config.thresholded_dir)
    celltypes_dict = config.marker_celltype_dict
    channel_names = config.channel_names

    #run function
    plot_celltype_distributions(celltypes_dir, matrix_dir, celltypes_dict, channel_names)

def plot_celltype_distributions(celltypes_dir, matrix_dir, celltypes_dict, channel_names):

    #load data
    cell_types_df = pd.read_csv(os.path.join(celltypes_dir, 'cell_types_v2.csv'), index_col=0)
    print(cell_types_df.shape)
    matrix = np.load(os.path.join(matrix_dir, 'matrix.npy'))
    print(matrix.shape)

    #save path
    save_path = os.path.join(celltypes_dir, 'celltype_distributions')
    os.makedirs(save_path, exist_ok=True)

    percentile_dict = {}

    for i, sample in enumerate(cell_types_df['slide_id'].unique()):
        print(f'Processing sample {sample}')
        sample_dict = {}

        #sample save path
        sample_save_path = os.path.join(save_path, sample)
        os.makedirs(sample_save_path, exist_ok=True)
        
        #create a figure for 4 plots, 1 for each cell type
        fig, axs = plt.subplots(2, 2, figsize=(15, 15))
        fig.suptitle(f'Sample: {sample}')

        subplot_idx = 0

        for celltype, marker in celltypes_dict.items():
            celltype_df = cell_types_df[(cell_types_df['slide_id'] == sample) & (cell_types_df['cell_type'] == celltype)]

            if celltype_df.empty:
                print(f"No data for {celltype} in sample {sample}. Skipping.")
                continue
            
            print(f'Processing celltype {celltype}')
            print('Amount of cells:', celltype_df.shape[0])
            
            celltype_df_index = celltype_df.index - 1
            celltype_matrix = matrix[celltype_df_index, channel_names.index(marker)]

            percentiles = np.percentile(celltype_matrix, [5, 25, 50, 75, 95])
            sample_dict[marker] = {5: percentiles[0], 25: percentiles[1], 50: percentiles[2], 75: percentiles[3], 95: percentiles[4]}
            
            row = subplot_idx // 2
            col = subplot_idx % 2

            sns.kdeplot(celltype_matrix, color='blue', alpha = 0.8, ax=axs[row, col])
            axs[row, col].set_title(f'Celltype: {celltype} - {celltype_df.shape[0]} cells')
            axs[row, col].set_xlabel(f'{marker} Intensity')
            axs[row, col].set_ylabel('Density')

            #add vertical lines for the percentiles
            for perc, value in zip([5, 25, 50, 75, 95], percentiles):
                axs[row, col].axvline(value, color='red', linestyle='--', label=f'{perc}th: {value:.2f}')

            axs[row, col].legend(loc='upper right')
            subplot_idx += 1
        
        for i in range(subplot_idx, axs.size):  # axs.size gives the total number of axes
            row = i // 2
            col = i % 2
            axs[row, col].set_visible(False)

        #save the figure
        plt.savefig(os.path.join(sample_save_path, f'kde_celltypes.png'))
        plt.close()
        print(f'Saved cell type distribution plot for sample {sample}')

        percentile_dict[sample] = sample_dict
        print('')
    
    #save dict as json
    with open(os.path.join(save_path, 'percentile_dict.json'), 'w') as json_file:
        json.dump(percentile_dict, json_file, indent=4)

if __name__ == '__main__':
    main()