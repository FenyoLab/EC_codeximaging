import os
import pandas as pd
import numpy as np 
import json
import sys

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
    mixed_celltypes = config.mixed_celltypes
    channel_names = config.channel_names
    threshold_dict = config.stricter_threshold_dict

    assign_mixed_celltypes_by_strict_thresholding(celltypes_dir, matrix_dir, mixed_celltypes, channel_names, threshold_dict)

def assign_mixed_celltypes_by_strict_thresholding(celltypes_dir, matrix_dir, mixed_celltypes, channel_names, threshold_dict):
    
    cell_types_df_path = os.path.join(celltypes_dir, 'cell_types_v2.csv')
    if os.path.exists(cell_types_df_path):  
        print('Cell type information saved, skipping')
        return

    #load in cell_typs_df and matrix
    cell_types_df = pd.read_csv(os.path.join(celltypes_dir, 'cell_types_v1.csv'), index_col=0)
    matrix = np.load(os.path.join(matrix_dir, 'matrix.npy'))

    assert matrix.shape[0] == cell_types_df.shape[0], 'Matrix and cell types df do not have the same number of cells'

    ct_assignment_dict = {}

    for i, sample in enumerate(cell_types_df['slide_id'].unique()):
        print(f'Processing sample {sample}')
        
        #initalize sample in dict 
        if sample not in ct_assignment_dict:
            ct_assignment_dict[sample] = {}

        for idx, cell_type in enumerate(mixed_celltypes):
            sample_df = cell_types_df[
                (cell_types_df['slide_id'] == sample) &
                (cell_types_df['cell_type'] == cell_type)
            ]
            if len(sample_df) == 0:
                print(f'No cells of type {cell_type} in this sample')
                continue
            
            print(f'Processing cell type {cell_type}')

            #initialize cell type in dict
            if cell_type not in ct_assignment_dict[sample]:
                ct_assignment_dict[sample][cell_type] = {}
            
            print('Number of cells:', len(sample_df))
            sample_df_index = sample_df.index - 1

            #get thresholds for this sample
            thresholds = threshold_dict[sample]

            if cell_type == 'CD4+ and CD8+ T cells':
                cytotoxic_t_count = 0
                helper_t_count = 0
                cd4_cd8_t_cell_count = 0

                for index, cell_index in enumerate(sample_df_index):
                    cell_arr = matrix[cell_index]

                    if cell_arr[channel_names.index('CD8')] > thresholds['CD8']:
                        #print('Cell is positive for CD8 and becomes a Cytotoxic T cell')
                        cell_types_df.at[cell_index + 1, 'cell_type'] = 'Cytotoxic T cells'
                        cytotoxic_t_count += 1
                    elif cell_arr[channel_names.index('CD4')] > thresholds['CD4']:
                        #print('Cell is positive for CD4 and becomes a Helper T cell')
                        cell_types_df.at[cell_index + 1, 'cell_type'] = 'Helper T cells'
                        helper_t_count += 1
                    else:
                        #print('Cell is positive for both CD4 and CD8')
                        cd4_cd8_t_cell_count += 1
            
                ct_assignment_dict[sample][cell_type] = {
                    'Original cell number': len(sample_df),
                    'Cytotoxic T cells': cytotoxic_t_count,
                    'Helper T cells': helper_t_count,
                    'CD4+ and CD8+ T cells': cd4_cd8_t_cell_count
                }
            
            if cell_type == 'CD20+ and CD3e+ cells':
                t_cell_other_count = 0
                b_cell_count = 0
                cd20_cd3e_pos_count = 0

                for index, cell_index in enumerate(sample_df_index):
                    cell_arr = matrix[cell_index]

                    if cell_arr[channel_names.index('CD20')] > thresholds['CD20']:
                        if cell_arr[channel_names.index('CD3e')] > thresholds['CD3e']:
                            #print('Cell is positive for CD20 and CD3e')
                            cd20_cd3e_pos_count += 1
                        else:
                            #print('Cell is positive for CD20 and becomes a B cell')
                            cell_types_df.at[cell_index + 1, 'cell_type'] = 'B cells'
                            b_cell_count += 1
                    
                    elif cell_arr[channel_names.index('CD3e')] > thresholds['CD3e']:
                        #print('Cell is positive for CD3e and becomes a T cell')
                        cell_types_df.at[cell_index + 1, 'cell_type'] = 'T cells (other)'
                        t_cell_other_count += 1
                    else:
                        #print('Cell is positive for both CD20 and CD3e')
                        cd20_cd3e_pos_count += 1
                
                ct_assignment_dict[sample][cell_type] = {
                    'Original cell number': len(sample_df),
                    'B cells': b_cell_count,
                    'T cells (other)': t_cell_other_count,
                    'CD20+ and CD3e+ cells': cd20_cd3e_pos_count
                }

            if cell_type == 'CD20+ and CD4+ cells':
                helper_t_count = 0
                b_cell_count = 0
                cd20_cd4_pos_count = 0

                for index, cell_index in enumerate(sample_df_index):
                    cell_arr = matrix[cell_index]

                    if cell_arr[channel_names.index('CD20')] > thresholds['CD20']:
                        if cell_arr[channel_names.index('CD4')] > thresholds['CD4']:
                            #print('Cell is positive for CD20 and CD4')
                            cd20_cd4_pos_count += 1
                        else:
                            #print('Cell is positive for CD20 and becomes a B cell')
                            cell_types_df.at[cell_index + 1, 'cell_type'] = 'B cells'
                            b_cell_count += 1
                    
                    elif cell_arr[channel_names.index('CD4')] > thresholds['CD4']:
                        #print('Cell is positive for CD4 and becomes a Helper T cell')
                        cell_types_df.at[cell_index + 1, 'cell_type'] = 'Helper T cells'
                        helper_t_count += 1
                    else:
                        #print('Cell is positive for both CD20 and CD4')
                        cd20_cd4_pos_count += 1
                
                ct_assignment_dict[sample][cell_type] = {
                    'Original cell number': len(sample_df),
                    'B cells': b_cell_count,
                    'Helper T cells': helper_t_count,
                    'CD20+ and CD4+ cells': cd20_cd4_pos_count
                }

            if cell_type == 'CD20+ and CD8+ cells':
                cytotoxic_t_count = 0
                b_cell_count = 0
                cd20_cd8_pos_count = 0

                for index, cell_index in enumerate(sample_df_index):
                    cell_arr = matrix[cell_index]

                    if cell_arr[channel_names.index('CD8')] > thresholds['CD8']:
                        #print('Cell is positive for CD8 and becomes a Cytotoxic T cell')
                        cell_types_df.at[cell_index + 1, 'cell_type'] = 'Cytotoxic T cells'
                        cytotoxic_t_count += 1
                    
                    elif cell_arr[channel_names.index('CD20')] > thresholds['CD20']:
                        #print('Cell is positive for CD20 and becomes a B cell')
                        cell_types_df.at[cell_index + 1, 'cell_type'] = 'B cells'
                        b_cell_count += 1
                    
                    else:
                        #print('Cell is positive for both CD20 and CD8')
                        cd20_cd8_pos_count += 1
                
                ct_assignment_dict[sample][cell_type] = {
                    'Original cell number': len(sample_df),
                    'B cells': b_cell_count,
                    'Cytotoxic T cells': cytotoxic_t_count,
                    'CD20+ and CD8+ cells': cd20_cd8_pos_count
                }
        print('')

    with open(os.path.join(celltypes_dir, 'cell_type_stats_v2.json'), 'w') as json_file:
        json.dump(ct_assignment_dict, json_file, indent=4)

    print('Cell types after second round of splitting mixed cell types:')
    print(cell_types_df['cell_type'].value_counts())

    cell_types_df.to_csv(cell_types_df_path)
    print(f"Cell types assigned and saved at {cell_types_df_path}")

if __name__ == '__main__':
    main()