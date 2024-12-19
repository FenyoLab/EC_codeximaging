import os
import numpy as np
import pandas as pd
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

    celltypes_dir = os.path.join(config.out_dir, config.celltypes_dir, f'{config.n_clusters_celltypes}_clusters')
    matrix_dir = os.path.join(config.out_dir, config.thresholded_dir)
    save_path = os.path.join(celltypes_dir, 'celltype_distributions')
    mixed_celltypes = config.mixed_celltypes
    channel_names = config.channel_names
    
    compare_celltype_distributions(celltypes_dir, matrix_dir, save_path, mixed_celltypes, channel_names)

def compare_celltype_distributions(celltypes_dir, matrix_dir, save_path, mixed_celltypes, channel_names):
    
    #load data
    cell_types_df = pd.read_csv(os.path.join(celltypes_dir, 'cell_types_v2.csv'), index_col=0)
    print(cell_types_df.shape)
    matrix = np.load(os.path.join(matrix_dir, 'matrix.npy'))
    print(matrix.shape)  

    #load percentiles dict
    with open(os.path.join(save_path, 'percentile_dict.json'), 'r') as f:
        percentiles_dict = json.load(f)

    for i, sample in enumerate(cell_types_df['slide_id'].unique()):
        print(f'Processing sample {sample}')

        #sample save path
        sample_save_path = os.path.join(save_path, sample)
        os.makedirs(sample_save_path, exist_ok=True)

        mixed_celltype_data = []

        for i, celltype, in enumerate(mixed_celltypes):
            celltype_df = cell_types_df[(cell_types_df['slide_id'] == sample) & (cell_types_df['cell_type'] == celltype)]

            if celltype_df.empty:
                print(f"No data for {celltype} in sample {sample}. Skipping.")
                continue
            
            print(f'Processing celltype {celltype}')
            print('Amount of cells:', celltype_df.shape[0])
            
            celltype_df_index = celltype_df.index - 1

            if celltype == 'CD4+ and CD8+ T cells':
                cd4_means = matrix[celltype_df_index, channel_names.index('CD4')]
                cd8_means = matrix[celltype_df_index, channel_names.index('CD8')]

                # Get the percentile thresholds for CD4 and CD8 from the dictionary
                cd4_percentile_value = percentiles_dict[sample]['CD4']
                cd8_percentile_value = percentiles_dict[sample]['CD8']

                for i, (cd4_value, cd8_value) in enumerate(zip(cd4_means, cd8_means)):
                    cd4_percentile = get_percentile_range(cd4_value, cd4_percentile_value)
                    cd8_percentile = get_percentile_range(cd8_value, cd8_percentile_value)

                    mixed_celltype_data.append({
                        "cell_label": celltype_df_index[i] + 1,  # Assuming index corresponds to the cell label
                        "celltype": celltype,
                        "CD8": cd8_value,
                        "CD8_percentile": cd8_percentile,
                        "CD4": cd4_value,
                        "CD4_percentile": cd4_percentile
                    })
            
            if celltype == 'CD20+ and CD3e+ cells':
                cd3e_means = matrix[celltype_df_index, channel_names.index('CD3e')]
                cd20_means = matrix[celltype_df_index, channel_names.index('CD20')]

                # Get the percentile thresholds for CD3e and CD20 from the dictionary
                cd3e_percentile_value = percentiles_dict[sample]['CD3e']
                cd20_percentile_value = percentiles_dict[sample]['CD20']

                for i, (cd3e_value, cd20_value) in enumerate(zip(cd3e_means, cd20_means)):
                    cd3e_percentile = get_percentile_range(cd3e_value, cd3e_percentile_value)
                    cd20_percentile = get_percentile_range(cd20_value, cd20_percentile_value)

                    mixed_celltype_data.append({
                        "cell_label": celltype_df_index[i] + 1,  # Assuming index corresponds to the cell label
                        "celltype": celltype,
                        "CD3e": cd3e_value,
                        "CD3e_percentile": cd3e_percentile,
                        "CD20": cd20_value,
                        "CD20_percentile": cd20_percentile
                    })
            
            if celltype == 'CD20+ and CD4+ cells':
                cd4_means = matrix[celltype_df_index, channel_names.index('CD4')]
                cd20_means = matrix[celltype_df_index, channel_names.index('CD20')]

                cd4_percentile_value = percentiles_dict[sample]['CD4']
                cd20_percentile_value = percentiles_dict[sample]['CD20']

                for i, (cd4_value, cd20_value) in enumerate(zip(cd4_means, cd20_means)):
                    cd4_percentile = get_percentile_range(cd4_value, cd4_percentile_value)
                    cd20_percentile = get_percentile_range(cd20_value, cd20_percentile_value)

                    mixed_celltype_data.append({
                        "cell_label": celltype_df_index[i] + 1,  # Assuming index corresponds to the cell label
                        "celltype": celltype,
                        "CD4": cd4_value,
                        "CD4_percentile": cd4_percentile,
                        "CD20": cd20_value,
                        "CD20_percentile": cd20_percentile
                    })
            
            if celltype == 'CD20+ and CD8+ cells':
                cd8_means = matrix[celltype_df_index, channel_names.index('CD8')]
                cd20_means = matrix[celltype_df_index, channel_names.index('CD20')]

                cd8_percentile_value = percentiles_dict[sample]['CD8']
                cd20_percentile_value = percentiles_dict[sample]['CD20']

                for i, (cd8_value, cd20_value) in enumerate(zip(cd8_means, cd20_means)):
                    cd8_percentile = get_percentile_range(cd8_value, cd8_percentile_value)
                    cd20_percentile = get_percentile_range(cd20_value, cd20_percentile_value)

                    mixed_celltype_data.append({
                        "cell_label": celltype_df_index[i] + 1,  # Assuming index corresponds to the cell label
                        "celltype": celltype,
                        "CD8": cd8_value,
                        "CD8_percentile": cd8_percentile,
                        "CD20": cd20_value,
                        "CD20_percentile": cd20_percentile
                    }) 

        print('')   
        mixed_celltype_df = pd.DataFrame(mixed_celltype_data)
        if len(mixed_celltype_df) == 0:
            print(f"No data for mixed celltypes in sample {sample}. No data saved.")
            continue
        mixed_celltype_df.to_csv(os.path.join(sample_save_path, f'mixed_celltypes.csv'), index = False)

def get_percentile_range(value, percentiles):
    if value < percentiles['5']:
        return 0
    elif percentiles['5'] <= value < percentiles['25']:
        return 5
    elif percentiles['25'] <= value < percentiles['50']:
        return 25
    elif percentiles['50'] <= value < percentiles['75']:
        return 50
    elif percentiles['75'] <= value < percentiles['95']:
        return 75
    elif value >= percentiles['95']:
        return 95

if __name__ == '__main__':
    main()