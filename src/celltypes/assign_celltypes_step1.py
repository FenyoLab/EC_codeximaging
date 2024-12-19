import os
import sys
import pandas as pd
import numpy as np 
import json

from types import SimpleNamespace
sys.path.append('/gpfs/home/as18894/projects/as18894/FenyoLab/Endometrial/EC_codeximaging')
from utils import helper

def main():
    #import config
    config_yaml= '/gpfs/home/as18894/projects/as18894/FenyoLab/Endometrial/EC_codeximaging/config/config_cellphenotyping.yaml'
    run_config = helper.load_yaml_file(config_yaml)
    config = SimpleNamespace(**run_config)

    save_path = config.out_dir
    thresholded_matrix_path = os.path.join(config.out_dir, config.thresholded_dir, 'matrix.npy')
    n_clusters_celltypes = config.n_clusters_celltypes
    cell_types_dict = config.cluster_celltype_labels
    thresholding_dict = config.lineage_markers_cluster_dict
    phenotype_clusters_path = os.path.join(config.out_dir, config.clustering_dir, f'{config.n_clusters_celltypes}_clusters/phenotype_clusters.csv')
    channel_names = config.channel_names
    
    assign_celltypes(save_path, thresholded_matrix_path, n_clusters_celltypes, cell_types_dict, thresholding_dict, phenotype_clusters_path, channel_names)

def assign_celltypes(save_path, thresholded_matrix_path, n_clusters_celltypes, cell_types_dict, thresholding_dict, phenotype_clusters_path, channel_names, output_suffix = 'celltypes'):

    output_path = f'{save_path}/{output_suffix}/{n_clusters_celltypes}_clusters'
    os.makedirs(output_path, exist_ok=True)
    cell_types_df_path = os.path.join(output_path, 'cell_types_v1.csv')
    print(cell_types_df_path)

    if os.path.exists(cell_types_df_path):  
        print('Cell type information saved, skipping')
        return

    phenotype_clusters = pd.read_csv(phenotype_clusters_path, index_col =0)
    print(phenotype_clusters.shape)
    print(phenotype_clusters.head())
    
    #map(): The map() function in pandas is used to map values from a dictionary to a DataFrame column.
    phenotype_clusters['cell_type'] = phenotype_clusters['cluster_label'].map(cell_types_dict)
    print(phenotype_clusters.head())

    #load in thresholded matrix
    thresholded_matrix = np.load(thresholded_matrix_path)

    cell_types_df, heterogenous_cells_stats = assign_heterogeneous_celltype(phenotype_clusters, thresholded_matrix, thresholding_dict, channel_names)

    print('Cell types after assigning heterogeneous cell types:')
    print(cell_types_df['cell_type'].value_counts())

    cell_type_stats = {}
    
    for cell_type_name in ['B cells', 'Helper T cells', 'Cytotoxic T cells', 'T cells (other)', 'Macrophages', 'Stromal cells (undefined)']:
        print(f'Processing {cell_type_name}')
        cell_types_df, single_cell_type_stats = split_mixed_celltype(cell_type_name, cell_types_df, thresholded_matrix, channel_names)
        cell_type_stats[cell_type_name] = single_cell_type_stats
    
    with open(os.path.join(output_path, 'heterogeneous_cells_stat.json'), 'w') as json_file:
        json.dump(heterogenous_cells_stats, json_file, indent=4)

    with open(os.path.join(output_path, 'cell_type_stats_v1.json'), 'w') as json_file:
        json.dump(cell_type_stats, json_file, indent=4)

    print('Cell types after splitting mixed cell types:')
    print(cell_types_df['cell_type'].value_counts())
    cell_types_df.to_csv(cell_types_df_path)

    print(f'Cell types assigned and saved at {cell_types_df_path}')

def assign_heterogeneous_celltype(cell_types_df, matrix, thresholding_dict, channel_names):
    
    print("Cell types df shape: ", cell_types_df.shape)
    print("Cell matrix shape: ", matrix.shape)
    print('Ecadherin channel index:', channel_names.index('Ecadherin'))

    assert cell_types_df.shape[0] == matrix.shape[0], "Number of cells in cell types df and matrix do not match"

    heterogenous_cells_stats = {}

    for sample in np.unique(cell_types_df['slide_id'].values):
        print(f'Processing sample {sample}')
        #get heterogeneous cells for each sample
        sample_heterogeneous_cells = cell_types_df[(cell_types_df['slide_id'] == sample) & (cell_types_df['cell_type'] == 'Heterogeneous')]
        print(f"Sample heterogeneous cells shape: {sample_heterogeneous_cells.shape}")
        print(f"Sample indices spread: {sample_heterogeneous_cells.index[0]} ... {sample_heterogeneous_cells.index[-1]}")

        sample_heterogeneous_arr = matrix[sample_heterogeneous_cells.index - 1, channel_names.index('Ecadherin')]
        print(f"Sample heterogeneous matrix shape: {sample_heterogeneous_arr.shape}")

        assert sample_heterogeneous_cells.shape[0] == sample_heterogeneous_arr.shape[0], "Number of cells in heterogenous cell types df and matrix do not match"

        ecadherin_threshold = thresholding_dict.get(sample, {}).get('Ecadherin')

        above_threshold = sample_heterogeneous_arr > ecadherin_threshold
        below_threshold = ~above_threshold

        if np.any(above_threshold):
            print(f"Cells above threshold: {np.where(above_threshold)[0][0]} ... {np.where(above_threshold)[0][-1]}, sum: {np.sum(above_threshold)}")
        else:
            print("No cells are above the threshold.")
        if np.any(below_threshold):
            print(f"Cells below threshold: {np.where(below_threshold)[0][0]} ... {np.where(below_threshold)[0][-1]}, sum: {np.sum(below_threshold)}")
        else:
            print("No cells are below the threshold.")
        
        # Assign cell types based on threshold condition
        sample_heterogeneous_cells.loc[above_threshold, 'cell_type'] = 'Tumor cells'
        sample_heterogeneous_cells.loc[below_threshold, 'cell_type'] = 'Stromal cells (undefined)'
        
        # Update these values in the original DataFrame
        cell_types_df.loc[sample_heterogeneous_cells.index, 'cell_type'] = sample_heterogeneous_cells['cell_type']
        print(cell_types_df.loc[sample_heterogeneous_cells.index, 'cell_type'].value_counts())
        print(cell_types_df.loc[sample_heterogeneous_cells.index].head())
        print('')

        heterogenous_cells_stats[sample] = {
            'ecadherin_threshold': int(ecadherin_threshold),
            'num_heterogeneous_cells': int(len(sample_heterogeneous_cells)),
            'num_tumor_cells': int(np.sum(above_threshold)),
            'num_stromal_cells': int(np.sum(below_threshold))
        }
        
    return cell_types_df, heterogenous_cells_stats 

def split_mixed_celltype(cell_type_name, cell_types_df, thresholded_matrix, channel_names):

    print("Cell types df shape: ", cell_types_df.shape)
    print("Cell matrix shape: ", thresholded_matrix.shape)
    
    assert cell_types_df.shape[0] == thresholded_matrix.shape[0], "Number of cells in cell types df and cell matrix do not match"

    #dont have to do it by sample!!!
    single_cell_type_df = cell_types_df[cell_types_df['cell_type'] == cell_type_name]
    print(f"Single cell type df shape: {single_cell_type_df.shape}")
    print(f"Single cell type indices spread: {single_cell_type_df.index[0]} ... {single_cell_type_df.index[-1]}")

    single_cell_type_df_index = single_cell_type_df.index - 1
    #single_cell_type_matrix = thresholded_matrix[single_cell_type_df.index - 1]

    #assert single_cell_type_df.shape[0] == single_cell_type_matrix.shape[0], "Number of cells in single cell types df and corresponding cell type matrix do not match"
    
    split_cells_stats = {}

    if cell_type_name == 'B cells':
        print(cell_type_name)
        b_cell_count = 0
        helper_t_count = 0
        cytotoxic_t_count = 0
        t_cell_other_count = 0
        cd20_cd8_pos_count = 0
        cd20_cd4_pos_count = 0
        cd20_cd3e_pos_count = 0
        stromal_cell_count = 0

        for i, cell_index in enumerate(single_cell_type_df_index):
            cell_arr = thresholded_matrix[cell_index]

            if cell_arr[channel_names.index('CD3e')] > 0:
                if cell_arr[channel_names.index('CD8')] > 0:
                    if cell_arr[channel_names.index('CD20')] > 0:
                        #print('Cell is positive for CD20, CD3e and CD8 and becomes a cytotoxic T cell')
                        cell_types_df.at[cell_index + 1, 'cell_type'] = 'CD20+ and CD8+ cells'
                        cd20_cd8_pos_count += 1
                    else:
                        #print('Cell is positive for CD3e and CD8 and becomes a cytotoxic T cell')
                        cell_types_df.at[cell_index + 1, 'cell_type'] = 'Cytotoxic T cells'
                        cytotoxic_t_count += 1
                elif cell_arr[channel_names.index('CD4')] > 0:
                    if cell_arr[channel_names.index('CD20')] > 0:
                        #print('Cell is positive for CD20, CD3e and CD4 and becomes a helper T cell')
                        cell_types_df.at[cell_index + 1, 'cell_type'] = 'CD20+ and CD4+ cells'
                        cd20_cd4_pos_count += 1
                    else:
                        #print('Cell is positive for CD3e and CD4 and becomes a helper T cell')
                        cell_types_df.at[cell_index + 1, 'cell_type'] = 'Helper T cells'
                        helper_t_count += 1
                elif cell_arr[channel_names.index('CD20')] > 0:
                    #print('Cell is positive for CD3e and CD20 and becomes a T cells (other)')
                    cell_types_df.at[cell_index + 1, 'cell_type'] = 'CD20+ and CD3e+ cells'
                    cd20_cd3e_pos_count += 1
                else:  
                    cell_types_df.at[cell_index + 1, 'cell_type'] = 'T cells (other)'
                    t_cell_other_count += 1
            
            elif cell_arr[channel_names.index('CD20')] > 0:
                #print('Cell is positive for CD20 and becomes a B cell')
                cell_types_df.at[cell_index + 1, 'cell_type'] = 'B cells'
                b_cell_count += 1
        
            else:
                cell_types_df.at[cell_index + 1, 'cell_type'] = 'Stromal cells (undefined)'
                stromal_cell_count += 1

        split_cells_stats = {
            'Original cell number': int(single_cell_type_df.shape[0]),
            'B cell': int(b_cell_count),
            'Helper T cells': int(helper_t_count),
            'CD20+ and CD4+ cells': int(cd20_cd4_pos_count),
            'Cytotoxic T cells': int(cytotoxic_t_count),
            'CD20+ and CD8+ cells': int(cd20_cd8_pos_count),
            'T cells (other)': int(t_cell_other_count),
            'CD20+ and CD3e+ cells': int(cd20_cd3e_pos_count),
            'Stromal cells (undefined)': int(stromal_cell_count)
        }
        print('')
        
    if cell_type_name == 'Helper T cells':
        print(cell_type_name)
        helper_t_count = 0
        cytotoxic_t_count = 0
        t_cell_other_count = 0
        b_cell_count = 0
        macrophage_count = 0
        stromal_cell_count = 0
        cd4_cd8_t_cell_count = 0

        for i, cell_index in enumerate(single_cell_type_df_index):
            cell_arr = thresholded_matrix[cell_index]

            if cell_arr[channel_names.index('CD3e')] > 0:
                if cell_arr[channel_names.index('CD4')] > 0:
                    if cell_arr[channel_names.index('CD8')] > 0:
                        #print('Cell is positive for CD3e, CD4 and CD8 becomes a cell with both CD4 and CD8')
                        cell_types_df.at[cell_index + 1, 'cell_type'] = 'CD4+ and CD8+ T cells'
                        cd4_cd8_t_cell_count += 1
                    else:
                        #print('Cell is positive for CD3e and CD4 and remains a Helper T cell')
                        helper_t_count += 1
                elif cell_arr[channel_names.index('CD8')] > 0:
                    #print('Cell is positive for CD3e and CD8 and becomes a Cytotoxic T cell')
                    cell_types_df.at[cell_index + 1, 'cell_type'] = 'Cytotoxic T cells'
                    cytotoxic_t_count += 1
                else:
                    #print('Cell is positive for CD3e (not cd4 or cd8) and becomes a T cells (other)')
                    cell_types_df.at[cell_index + 1, 'cell_type'] = 'T cells (other)'
                    t_cell_other_count += 1

            elif cell_arr[channel_names.index('CD68')] > 0:
                #print('Cell is positive for CD68 and becomes a Macrophage')
                cell_types_df.at[cell_index + 1, 'cell_type'] = 'Macrophages'
                macrophage_count += 1
            
            elif cell_arr[channel_names.index('CD4')] > 0:
                if cell_arr[channel_names.index('CD8')] > 0:
                    #print('Cell is positive for CD4 and CD8 and becomes a cell with both CD4 and CD8')
                    cell_types_df.at[cell_index + 1, 'cell_type'] = 'CD4+ and CD8+ T cells'
                    cd4_cd8_t_cell_count += 1
                else:
                    #print('Cell is positive for CD4 and remains a Helper T cell')
                    helper_t_count += 1
            elif cell_arr[channel_names.index('CD8')] > 0:
                #print('Cell is positive for CD8 and becomes a Cytotoxic T cell')
                cell_types_df.at[cell_index + 1, 'cell_type'] = 'Cytotoxic T cells'
                cytotoxic_t_count += 1
            
            elif cell_arr[channel_names.index('CD20')] > 0:
                #print('Cell is positive for CD20 and becomes a B cell')
                cell_types_df.at[cell_index + 1, 'cell_type'] = 'B cells'
                b_cell_count += 1
            
            else:
                cell_types_df.at[cell_index + 1, 'cell_type'] = 'Stromal cells (undefined)'
                stromal_cell_count += 1
            
        split_cells_stats = {
            'Original cell number': int(single_cell_type_df.shape[0]),
            'Helper T cells': int(helper_t_count),
            'Cytotoxic T cells': int(cytotoxic_t_count),
            'T cells (other)': int(t_cell_other_count),
            'B cells': int(b_cell_count),
            'Macrophages': int(macrophage_count),
            'CD4+ and CD8+ T cells': int(cd4_cd8_t_cell_count),
            'Stromal cells (undefined)': int(stromal_cell_count)
        }
        print('')
    
    if cell_type_name == 'Cytotoxic T cells':
        print(cell_type_name)
        helper_t_count = 0
        cytotoxic_t_count = 0
        b_cell_count = 0
        t_cell_other_count = 0
        stromal_cell_count = 0 
        cd4_cd8_t_cell_count = 0

        for i, cell_index in enumerate(single_cell_type_df_index):
            cell_arr = thresholded_matrix[cell_index]

            if cell_arr[channel_names.index('CD3e')] > 0:
                if cell_arr[channel_names.index('CD8')] > 0:
                    if cell_arr[channel_names.index('CD4')] > 0:
                        #print('Cell is positive for CD3e, CD4 and CD8 becomes a cell with both CD4 and CD8')
                        cell_types_df.at[cell_index + 1, 'cell_type'] = 'CD4+ and CD8+ T cells'
                        cd4_cd8_t_cell_count += 1
                    else:
                        #print('Cell is positive for CD3e and CD8 and remains a Cytotoxic T cell')
                        cytotoxic_t_count += 1
                elif cell_arr[channel_names.index('CD4')] > 0:
                    #print('Cell is positive for CD3e and CD4 and becomes a Helper T cell')
                    cell_types_df.at[cell_index + 1, 'cell_type'] = 'Helper T cells'
                    helper_t_count += 1
                else:
                    #print('Cell is positive for CD3e (not cd4 or cd8) and becomes a T cells (other)')
                    cell_types_df.at[cell_index + 1, 'cell_type'] = 'T cells (other)'
                    t_cell_other_count += 1

            #v2 - added this
            elif cell_arr[channel_names.index('CD8')] > 0:
                if cell_arr[channel_names.index('CD4')] > 0:
                    #print('Cell is positive for CD8 and CD4 and becomes a cell with both CD4 and CD8')
                    cell_types_df.at[cell_index + 1, 'cell_type'] = 'CD4+ and CD8+ T cells'
                    cd4_cd8_t_cell_count += 1
                else:
                    #print('Cell is positive for CD8 and remains a Cytotoxic T cell')
                    cytotoxic_t_count += 1
            elif cell_arr[channel_names.index('CD4')] > 0:
                #print('Cell is positive for CD4 and becomes a Helper T cell')
                cell_types_df.at[cell_index + 1, 'cell_type'] = 'Helper T cells'
                helper_t_count += 1

            elif cell_arr[channel_names.index('CD20')] > 0:
                #print('Cell is positive for CD20 and becomes a B cell')
                cell_types_df.at[cell_index + 1, 'cell_type'] = 'B cells'
                b_cell_count += 1

            else:
                cell_types_df.at[cell_index + 1, 'cell_type'] = 'Stromal cells (undefined)'
                stromal_cell_count += 1
            
        split_cells_stats = {
            'Original cell number': int(single_cell_type_df.shape[0]),
            'Cytotoxic T cells': int(cytotoxic_t_count),
            'Helper T cells': int(helper_t_count),
            'T cells (other)': int(t_cell_other_count),
            'CD4+ and CD8+ T cells': int(cd4_cd8_t_cell_count),
            'B cells': int(b_cell_count),
            'Stromal cells (undefined)': int(stromal_cell_count),
        }
        print(split_cells_stats)
        print('')
    
    if cell_type_name == 'T cells (other)':
        print(cell_type_name)
        helper_t_count = 0
        cytotoxic_t_count = 0
        t_cell_other_count = 0
        b_cell_count = 0 
        stromal_cell_count = 0
        cd4_cd8_t_cell_count = 0

        for i, cell_index in enumerate(single_cell_type_df_index):
            cell_arr = thresholded_matrix[cell_index]

            if cell_arr[channel_names.index('CD3e')] > 0:
                if cell_arr[channel_names.index('CD8')] > 0:
                    if cell_arr[channel_names.index('CD4')] > 0:
                        #print('Cell is positive for CD3e, CD4 and CD8 becomes a cell witg both CD4 and CD8')
                        cell_types_df.at[cell_index + 1, 'cell_type'] = 'CD4+ and CD8+ T cells'
                        cd4_cd8_t_cell_count += 1
                    else:
                        #print('Cell is positive for CD3e and CD8 and becomes a cytotoxic T cell')
                        cell_types_df.at[cell_index + 1, 'cell_type'] = 'Cytotoxic T cells'
                        cytotoxic_t_count += 1

                elif cell_arr[channel_names.index('CD4')] > 0:
                    #print('Cell is positive for CD3e and CD4 and becomes a helper T cell')
                    cell_types_df.at[cell_index + 1, 'cell_type'] = 'Helper T cells'
                    helper_t_count += 1
                else:
                    #print('Cell is positive for CD3e (not cd4 or cd8) and remains a T cells (other)')
                    t_cell_other_count += 1


            elif cell_arr[channel_names.index('CD8')] > 0:
                if cell_arr[channel_names.index('CD4')] > 0:
                    #print('Cell is positive for CD8 and CD4 and becomes a cell with both CD4 and CD8')
                    cell_types_df.at[cell_index + 1, 'cell_type'] = 'CD4+ and CD8+ T cells'
                    cd4_cd8_t_cell_count += 1
                else:
                    #print('Cell is positive for CD8 and becomes a Cytotoxic T cell')
                    cell_types_df.at[cell_index + 1, 'cell_type'] = 'Cytotoxic T cells'
                    cytotoxic_t_count += 1
            elif cell_arr[channel_names.index('CD4')] > 0:
                #print('Cell is positive for CD4 and becomes a helper T cell')
                cell_types_df.at[cell_index + 1, 'cell_type'] = 'Helper T cells'
                helper_t_count += 1
            
            elif cell_arr[channel_names.index('CD20')] > 0:
                #print('Cell is positive for CD20 and becomes a B cell')
                cell_types_df.at[cell_index + 1, 'cell_type'] = 'B cells'
                b_cell_count += 1
            
            else:
                cell_types_df.at[cell_index + 1, 'cell_type'] = 'Stromal cells (undefined)'
                stromal_cell_count += 1
                
            
        split_cells_stats = {
            'Original cell number': int(single_cell_type_df.shape[0]),
            'T cells (other)': int(t_cell_other_count),
            'Cytotoxic T cells': int(cytotoxic_t_count),
            'Helper T cells': int(helper_t_count),
            'B cells': int(b_cell_count),
            'CD4+ and CD8+ T cells': int(cd4_cd8_t_cell_count),
            'Stromal cells (undefined)': int(stromal_cell_count)
        }
        print(split_cells_stats)
        print('')
        
    if cell_type_name == 'Macrophages':
        print(cell_type_name)
        macrophage_cd163_pos_count = 0
        macrophage_cd163_neg_count = 0
        helper_t_count = 0
        cytotoxic_t_count = 0
        t_cell_other_count = 0
        cd4_cd8_t_cell_count = 0
        stromal_cell_count = 0

        for i, cell_index in enumerate(single_cell_type_df_index):
            cell_arr = thresholded_matrix[cell_index]

            if cell_arr[channel_names.index('CD3e')] > 0:
                if cell_arr[channel_names.index('CD4')] > 0:
                    if cell_arr[channel_names.index('CD8')] > 0:
                        #print('Cell is positive for CD3e, CD4 and CD8 becomes a cell with both CD4 and CD8')
                        cell_types_df.at[cell_index + 1, 'cell_type'] = 'CD4+ and CD8+ T cells'
                        cd4_cd8_t_cell_count += 1
                    else:
                        cell_types_df.at[cell_index + 1, 'cell_type'] = 'Helper T cells'
                        helper_t_count += 1
                elif cell_arr[channel_names.index('CD8')] > 0:
                    cell_types_df.at[cell_index + 1, 'cell_type'] = 'Cytotoxic T cells'
                    helper_t_count += 1
                else:
                    #print('Cell is positive for CD3e (not cd4 or cd8) and becomes a T cells (other)')
                    cell_types_df.at[cell_index + 1, 'cell_type'] = 'T cells (other)'
                    t_cell_other_count += 1

            elif cell_arr[channel_names.index('CD68')] > 0:
                if cell_arr[channel_names.index('CD163')] > 0:
                    #print('Cell is positive for CD68 and CD163 and is a Macrophage (CD163+)')
                    cell_types_df.at[cell_index + 1, 'cell_type'] = 'Macrophages (CD163+)'
                    macrophage_cd163_pos_count += 1
                else:
                    #print('Cell is positive for CD68 and negative for CD163 and is a Macrophage (CD163-)')
                    cell_types_df.at[cell_index + 1, 'cell_type'] = 'Macrophages (CD163-)'
                    macrophage_cd163_neg_count += 1

            elif cell_arr[channel_names.index('CD8')] > 0:
                if cell_arr[channel_names.index('CD4')] > 0:
                        #print('Cell is positive for CD3e, CD4 and CD8 becomes a cell with both CD4 and CD8')
                        cell_types_df.at[cell_index + 1, 'cell_type'] = 'CD4+ and CD8+ T cells'
                        cd4_cd8_t_cell_count += 1
                else:
                    #print('Cell is positive for CD3e and CD8 and becomes a cytotoxic T cell')
                    cell_types_df.at[cell_index + 1, 'cell_type'] = 'Cytotoxic T cells'
                    cytotoxic_t_count += 1
            elif cell_arr[channel_names.index('CD4')] > 0:
                #print('Cell is positive for CD4 and becomes a Helper T cell')
                cell_types_df.at[cell_index + 1, 'cell_type'] = 'Helper T cells'
                helper_t_count += 1
    
            else:
                #print('Cell is not positive for any relevant lineage markers')
                cell_types_df.at[cell_index + 1, 'cell_type'] = 'Stromal cells (undefined)'
                stromal_cell_count += 1
        
        split_cells_stats = {
            'Original cell number': int(single_cell_type_df.shape[0]),
            'Macrophages (CD163+)': int(macrophage_cd163_pos_count),
            'Macrophages (CD163-)': int(macrophage_cd163_neg_count),
            'Helper T cells': int(helper_t_count),
            'Cytotoxic T cells': int(cytotoxic_t_count),
            'T cells (other)': int(t_cell_other_count),
            'CD4+ and CD8+ T cells': int(cd4_cd8_t_cell_count),
            'Stromal cells (undefined)': int(stromal_cell_count)
        }
        print(split_cells_stats)
        print('')

    if cell_type_name == 'Stromal cells (undefined)':
        print(cell_type_name)
        helper_t_count = 0
        cytotoxic_t_count = 0
        t_cell_other_count = 0
        b_cell_count = 0
        macrophage_cd163_pos_count = 0
        macrophage_cd163_neg_count = 0
        stromal_cell_count = 0
        cd4_cd8_t_cell_count = 0
        cd20_cd8_pos_count = 0
        cd20_cd4_pos_count = 0
        cd20_cd3e_pos_count = 0

        for i, cell_index in enumerate(single_cell_type_df_index):
            cell_arr = thresholded_matrix[cell_index]

            if cell_arr[channel_names.index('CD3e')] > 0:
                if cell_arr[channel_names.index('CD4')] > 0:
                    if cell_arr[channel_names.index('CD8')] > 0:
                        #print('Cell is positive for CD3e, CD4 and CD8 becomes a cell with both CD4 and CD8')
                        cell_types_df.at[cell_index + 1, 'cell_type'] = 'CD4+ and CD8+ T cells'
                        cd4_cd8_t_cell_count += 1
                    elif cell_arr[channel_names.index('CD20')] > 0:
                        cell_types_df.at[cell_index + 1, 'cell_type'] = 'CD20+ and CD4+ cells'
                        cd20_cd4_pos_count += 1
                    else:
                        cell_types_df.at[cell_index + 1, 'cell_type'] = 'Helper T cells'
                        helper_t_count += 1
                elif cell_arr[channel_names.index('CD8')] > 0:
                    if cell_arr[channel_names.index('CD20')] > 0:
                        cell_types_df.at[cell_index + 1, 'cell_type'] = 'CD20+ and CD8+ cells'
                        cd20_cd8_pos_count += 1
                    else:
                        cell_types_df.at[cell_index + 1, 'cell_type'] = 'Cytotoxic T cells'
                        cytotoxic_t_count += 1
                elif cell_arr[channel_names.index('CD20')] > 0:
                    cell_types_df.at[cell_index + 1, 'cell_type'] = 'CD20+ and CD3e+ cells'
                    cd20_cd3e_pos_count += 1
                else:
                    cell_types_df.at[cell_index + 1, 'cell_type'] = 'T cells (other)'
                    t_cell_other_count += 1

            elif cell_arr[channel_names.index('CD68')] > 0:
                if cell_arr[channel_names.index('CD163')] > 0:
                    #print('Cell is positive for CD68 and CD163 and is a Macrophage (CD163+)')
                    cell_types_df.at[cell_index + 1, 'cell_type'] = 'Macrophages (CD163+)'
                    macrophage_cd163_pos_count += 1
                else:
                    #print('Cell is positive for CD68 and negative for CD163 and is a Macrophage (CD163-)')
                    cell_types_df.at[cell_index + 1, 'cell_type'] = 'Macrophages (CD163-)'
                    macrophage_cd163_neg_count += 1

            elif cell_arr[channel_names.index('CD20')] > 0:
                #print('Cell is positive for CD20 and becomes a B cell')
                cell_types_df.at[cell_index + 1, 'cell_type'] = 'B cells'
                b_cell_count += 1

            elif cell_arr[channel_names.index('CD8')] > 0:
                if cell_arr[channel_names.index('CD4')] > 0:
                    #print('Cell is positive for CD8 and CD4 and becomes a cell with both CD4 and CD8')
                    cell_types_df.at[cell_index + 1, 'cell_type'] = 'CD4+ and CD8+ T cells'
                    cd4_cd8_t_cell_count += 1
                else:
                    #print('Cell is positive for CD8 and becomes a Cytotoxic T cell')
                    cell_types_df.at[cell_index + 1, 'cell_type'] = 'Cytotoxic T cells'
                    cytotoxic_t_count += 1
            
            elif cell_arr[channel_names.index('CD4')] > 0:
                #print('Cell is positive for CD4 and becomes a Helper T cell')
                cell_types_df.at[cell_index + 1, 'cell_type'] = 'Helper T cells'
                helper_t_count += 1

            else:
                cell_types_df.at[cell_index + 1, 'cell_type'] = 'Stromal cells (undefined)'
                stromal_cell_count += 1

        split_cells_stats = {
            'Original cell number': int(single_cell_type_df.shape[0]),
            'Macrophages (CD163+)': int(macrophage_cd163_pos_count),
            'Macrophages (CD163-)': int(macrophage_cd163_neg_count),
            'Helper T cells': int(helper_t_count),
            'Cytotoxic T cells': int(cytotoxic_t_count),
            'T cells (other)': int(t_cell_other_count),
            'CD4+ and CD8+ T cells': int(cd4_cd8_t_cell_count),
            'CD20+ and CD4+ cells': int(cd20_cd4_pos_count),
            'CD20+ and CD8+ cells': int(cd20_cd8_pos_count),
            'CD20+ and CD3e+ cells': int(cd20_cd3e_pos_count),
            'B cells': int(b_cell_count),
            'Stromal cells (undefined)': int(stromal_cell_count)
        }
        print('')

    
    return cell_types_df, split_cells_stats

if __name__ == '__main__':
    main()