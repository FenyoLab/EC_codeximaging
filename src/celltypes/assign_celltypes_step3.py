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
    mixed_celltypes = config.mixed_celltypes
    percentile_thresholds_dict = config.percentile_thresholds_dict

    assign_final_celltypes(celltypes_dir, mixed_celltypes, percentile_thresholds_dict)
    

def assign_final_celltypes(celltypes_dir, mixed_celltypes, percentile_thresholds_dict):
    #load in cell_typs_df and matrix
    cell_types_df = pd.read_csv(os.path.join(celltypes_dir, 'cell_types_v2.csv'), index_col=0)
    #matrix = np.load(os.path.join(matrix_dir, 'matrix.npy'))
    #assert matrix.shape[0] == cell_types_df.shape[0], 'Matrix and cell types df do not have the same number of cells'

    ct_assignment_dict = {}

    for i, sample in enumerate(cell_types_df['slide_id'].unique()):
        mixed_celltype_df_path = os.path.join(celltypes_dir, 'celltype_distributions', sample, 'mixed_celltypes.csv')
        if not os.path.exists(mixed_celltype_df_path):
            print(f'No mixed celltype data for sample {sample}. Skipping.')
            continue

        print(f'Processing sample {sample}')

        #load in mixed celltype df and thresholds
        mixed_celltype_df = pd.read_csv(mixed_celltype_df_path, index_col=0)
        sample_thresholds = percentile_thresholds_dict.get(sample, {})

        for idx, cell_type in enumerate(mixed_celltypes):
            sample_df = cell_types_df[
                (cell_types_df['slide_id'] == sample) &
                (cell_types_df['cell_type'] == cell_type)
            ]
            if sample_df.empty:
                print(f'No cells of type {cell_type} in this sample')
                continue
            
            print(f'Processing cell type {cell_type}')
            print(f'Number of cells: {len(sample_df)}')

            #initialize sample in dict (if doesn't already exist)
            if sample not in ct_assignment_dict:
                ct_assignment_dict[sample] = {}
            #initialize cell type in dict
            if cell_type not in ct_assignment_dict[sample]:
                ct_assignment_dict[sample][cell_type] = {}
            
            if cell_type == 'CD4+ and CD8+ T cells':
                cytotoxic_t_count = 0
                helper_t_count = 0
                cd4_cd8_t_cell_count = 0
                stromal_count = 0

                cd4_threshold = sample_thresholds.get('CD4', 0)
                cd8_threshold = sample_thresholds.get('CD8', 0)

                for cell_id in sample_df.index:
                    cd4_percentile = mixed_celltype_df.loc[cell_id, 'CD4_percentile']
                    cd8_percentile = mixed_celltype_df.loc[cell_id, 'CD8_percentile']

                    if cd4_percentile < cd4_threshold and cd8_percentile < cd8_threshold:
                        #print('Cell is below threshold for both CD4 and CD8')
                        cell_types_df.at[cell_id, 'cell_type'] = 'Stromal cells (undefined)'
                        stromal_count += 1

                    elif cd4_percentile >= cd4_threshold and cd8_percentile < cd8_threshold:
                        #print('Cell is above threshold for CD4 but below for CD8')
                        cell_types_df.at[cell_id, 'cell_type'] = 'Helper T cells'
                        helper_t_count += 1

                    elif cd8_percentile >= cd8_threshold and cd4_percentile < cd4_threshold:
                        #print('Cell is above threshold for CD8 but below for CD4')
                        cell_types_df.at[cell_id, 'cell_type'] = 'Cytotoxic T cells'
                        cytotoxic_t_count += 1
                    
                    elif cd4_percentile >= cd4_threshold and cd8_percentile >= cd8_threshold:
                        #print('Cell is above threshold for both CD4 and CD8')
                        cd4_cd8_t_cell_count += 1
                
                ct_assignment_dict[sample][cell_type] = {
                    'Original cell number': len(sample_df),
                    'Cytotoxic T cells': cytotoxic_t_count,
                    'Helper T cells': helper_t_count,
                    'CD4+ and CD8+ T cells': cd4_cd8_t_cell_count,
                    'Stromal cells': stromal_count
                }

            if cell_type == 'CD20+ and CD3e+ cells':
                t_cell_other_count = 0
                b_cell_count = 0
                cd20_cd3e_pos_count = 0
                stromal_count = 0

                cd20_threshold = sample_thresholds.get('CD20', 0)
                cd3e_threshold = sample_thresholds.get('CD3e', 0)

                for cell_id in sample_df.index:
                    cd20_percentile = mixed_celltype_df.loc[cell_id, 'CD20_percentile']
                    cd3e_percentile = mixed_celltype_df.loc[cell_id, 'CD3e_percentile']

                    if cd20_percentile < cd20_threshold and cd3e_percentile < cd3e_threshold:
                        cell_types_df.at[cell_id, 'cell_type'] = 'Stromal cells (undefined)'
                        stromal_count += 1

                    elif cd20_percentile >= cd20_threshold and cd3e_percentile < cd3e_threshold:
                        cell_types_df.at[cell_id, 'cell_type'] = 'B cells'
                        b_cell_count += 1

                    elif cd3e_percentile >= cd3e_threshold and cd20_percentile < cd20_threshold:
                        cell_types_df.at[cell_id, 'cell_type'] = 'T cells (other)'
                        t_cell_other_count += 1
                    
                    elif cd20_percentile >= cd20_threshold and cd3e_percentile >= cd3e_threshold:
                        cd20_cd3e_pos_count += 1
                
                ct_assignment_dict[sample][cell_type] = {
                    'Original cell number': len(sample_df),
                    'B cells': b_cell_count,
                    'T cells (other)': t_cell_other_count,
                    'CD20+ and CD3e+ cells': cd20_cd3e_pos_count,
                    'Stromal cells': stromal_count
                }
            
            if cell_type == 'CD20+ and CD4+ cells':
                helper_t_count = 0
                b_cell_count = 0
                cd20_cd4_pos_count = 0
                stromal_count = 0

                cd20_threshold = sample_thresholds.get('CD20', 0)
                cd4_threshold = sample_thresholds.get('CD4', 0)

                for cell_id in sample_df.index:
                    cd20_percentile = mixed_celltype_df.loc[cell_id, 'CD20_percentile']
                    cd4_percentile = mixed_celltype_df.loc[cell_id, 'CD4_percentile']

                    if cd20_percentile < cd20_threshold and cd4_percentile < cd4_threshold:
                        cell_types_df.at[cell_id, 'cell_type'] = 'Stromal cells (undefined)'
                        stromal_count += 1

                    elif cd20_percentile >= cd20_threshold and cd4_percentile < cd4_threshold:
                        cell_types_df.at[cell_id, 'cell_type'] = 'B cells'
                        b_cell_count += 1

                    elif cd4_percentile >= cd4_threshold and cd20_percentile < cd20_threshold:
                        cell_types_df.at[cell_id, 'cell_type'] = 'Helper T cells'
                        helper_t_count += 1
                    
                    elif cd20_percentile >= cd20_threshold and cd4_percentile >= cd4_threshold:
                        cd20_cd4_pos_count += 1
                
                ct_assignment_dict[sample][cell_type] = {
                    'Original cell number': len(sample_df),
                    'B cells': b_cell_count,
                    'Helper T cells': helper_t_count,
                    'CD20+ and CD4+ cells': cd20_cd4_pos_count,
                    'Stromal cells': stromal_count
                }
            
            if cell_type == 'CD20+ and CD8+ cells':
                cytotoxic_t_count = 0
                b_cell_count = 0
                cd20_cd8_pos_count = 0
                stromal_count = 0

                cd20_threshold = sample_thresholds.get('CD20', 0)
                cd8_threshold = sample_thresholds.get('CD8', 0)

                for cell_id in sample_df.index:
                    cd20_percentile = mixed_celltype_df.loc[cell_id, 'CD20_percentile']
                    cd8_percentile = mixed_celltype_df.loc[cell_id, 'CD8_percentile']

                    if cd20_percentile < cd20_threshold and cd8_percentile < cd8_threshold:
                        cell_types_df.at[cell_id, 'cell_type'] = 'Stromal cells (undefined)'
                        stromal_count += 1

                    elif cd20_percentile >= cd20_threshold and cd8_percentile < cd8_threshold:
                        cell_types_df.at[cell_id, 'cell_type'] = 'B cells'
                        b_cell_count += 1

                    elif cd8_percentile >= cd8_threshold and cd20_percentile < cd20_threshold:
                        cell_types_df.at[cell_id, 'cell_type'] = 'Cytotoxic T cells'
                        cytotoxic_t_count += 1
                    
                    elif cd20_percentile >= cd20_threshold and cd8_percentile >= cd8_threshold:
                        cd20_cd8_pos_count += 1
                
                ct_assignment_dict[sample][cell_type] = {
                    'Original cell number': len(sample_df),
                    'B cells': b_cell_count,
                    'Cytotoxic T cells': cytotoxic_t_count,
                    'CD20+ and CD8+ cells': cd20_cd8_pos_count,
                    'Stromal cells': stromal_count
                }
        
        print(ct_assignment_dict[sample])
        print('')

    with open(os.path.join(celltypes_dir, 'cell_type_stats_v3.json'), 'w') as json_file:
        json.dump(ct_assignment_dict, json_file, indent=4)

    print('Cell types after final round of splitting mixed cell types:')
    print(cell_types_df['cell_type'].value_counts())

    cell_types_df.to_csv(os.path.join(celltypes_dir, 'cell_types.csv'))
    print(f"Cell types assigned and saved at {os.path.join(celltypes_dir, 'cell_types_final.csv')}")

if __name__ == '__main__':
    main()