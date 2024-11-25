import os
import pandas as pd
import numpy as np 
import json

def assign_celltypes(save_path, matrix_dir, n_clusters_celltypes, n_clusters_thresholding, cell_types_dict, thresholding_dict, phenotype_clusters_path, threshold_channel_names, channel_names, output_suffix = 'cell_types'):

    output_path = f'{save_path}/{output_suffix}/{n_clusters_celltypes}_clusters'
    os.makedirs(output_path, exist_ok=True)
    cell_types_df_path = os.path.join(output_path, 'cell_types.csv')
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

    thresholded_matrix = threshold_matrix(matrix_dir, thresholding_dict, threshold_channel_names, channel_names, n_clusters_thresholding)
    np.save(os.path.join(output_path, 'thresholded_matrix.npy'), thresholded_matrix)

    cell_types_df, heterogenous_cells_stats = assign_heterogeneous_celltype(phenotype_clusters, thresholded_matrix, thresholding_dict, channel_names)

    print('Cell types after assigning heterogeneous cell types:')
    print(cell_types_df['cell_type'].value_counts())

    cell_type_stats = {}
    
    for cell_type_name in ['B cells', 'Helper T cells', 'Cytotoxic T cells', 'T cells (other)', 'Macrophages']:
        print(f'Processing {cell_type_name}')
        cell_types_df, single_cell_type_stats = split_mixed_celltype(cell_type_name, cell_types_df, thresholded_matrix, channel_names)
        cell_type_stats[cell_type_name] = single_cell_type_stats
    
    with open(os.path.join(output_path, 'heterogeneous_cell_stats.json'), 'w') as json_file:
        json.dump(heterogenous_cells_stats, json_file, indent=4)

    with open(os.path.join(output_path, 'cell_type_stats.json'), 'w') as json_file:
        json.dump(cell_type_stats, json_file, indent=4)

    print('Cell types after splitting mixed cell types:')
    print(cell_types_df['cell_type'].value_counts())
    cell_types_df.to_csv(cell_types_df_path)

    print(f'Cell types assigned and saved at {cell_types_df_path}')

def threshold_matrix(matrix_dir, threshold_dict, threshold_channel_names, channel_names, n_clusters_thresholding):
    matrix = np.load(os.path.join(matrix_dir, 'matrix.npy'))
    cell_sample_names = np.load(os.path.join(matrix_dir, 'cell_sample_names.npy'))

    for sample in np.unique(cell_sample_names):
        print(f'Processing sample {sample}')
        sample_indices = np.where(cell_sample_names == sample)[0]
        sample_matrix = matrix[sample_indices]
        print(f'Sample matrix shape: {sample_matrix.shape}')

        # Load K-means labels for the sample
        sample_kmeans_labels_df = pd.read_csv(os.path.join(matrix_dir, 'thresholding_clusters', sample, f'lineage_markers_{n_clusters_thresholding}clusters.csv')) 
        #print(f'Sample kmeans labels df head: {sample_kmeans_labels_df.head()}')
        sample_kmeans_labels = sample_kmeans_labels_df[threshold_channel_names].to_numpy()
        print(f'Sample kmeans labels: {sample_kmeans_labels.shape}')

        assert sample_matrix.shape[0] == sample_kmeans_labels.shape[0], \
    f"Mismatch: Sample matrix has {sample_matrix.shape[0]} rows, while kmeans labels have {sample_kmeans_labels.shape[0]}."

        threshold_indices = [channel_names.index(channel) for channel in threshold_channel_names if channel in channel_names]
        print(threshold_indices)
    
        # Iterate over channels in the thresholding dictionary
        for channel_index, channel in enumerate(threshold_channel_names):
            if channel in ['MPO', 'Ecadherin', 'DAPI']:
                continue
            print(channel, channel_index, threshold_indices[channel_index])
            
            if channel in threshold_dict.get(sample, {}):  # Check if the sample is in the threshold_dict
                # Get the corresponding thresholding mapping for the current channel
                threshold_mapping = threshold_dict[sample][channel]
                print(threshold_mapping)

                if 'upper_cutoff' in threshold_mapping and 'lower_cutoff' in threshold_mapping:
                    lower_cutoff = threshold_mapping['lower_cutoff']
                    upper_cutoff = threshold_mapping['upper_cutoff']
                    #print(f"Applying lower cutoff of {lower_cutoff} and upper cutoff of {upper_cutoff} for {channel}")
                    sample_matrix[sample_matrix[:, threshold_indices[channel_index]] < lower_cutoff, threshold_indices[channel_index]] = 0
                    sample_matrix[sample_matrix[:, threshold_indices[channel_index]] > upper_cutoff, threshold_indices[channel_index]] = 0

                # Check if the channel uses only lower cutoff thresholding
                elif 'lower_cutoff' in threshold_mapping:
                    lower_cutoff = threshold_mapping['lower_cutoff']
                    #print(f"Applying lower cutoff of {lower_cutoff} for {channel}")
                    sample_matrix[sample_matrix[:, threshold_indices[channel_index]] < lower_cutoff, threshold_indices[channel_index]] = 0

                # Check if the channel uses upper cutoff in addition to cluster-based thresholding
                elif 'upper_cutoff' in threshold_mapping:
                    upper_cutoff = threshold_mapping['upper_cutoff']
                    #print(f"Applying cluster-based + upper cutoff (of {upper_cutoff}) thresholding for {channel}")

                    # Apply cluster-based thresholding
                    for index, label in enumerate(sample_kmeans_labels[:, channel_index]):
                        if label in threshold_mapping and threshold_mapping[label] == 'negative':
                            sample_matrix[index, threshold_indices[channel_index]] = 0
                
                    # Apply upper cutoff thresholding
                    sample_matrix[sample_matrix[:, threshold_indices[channel_index]] > upper_cutoff, threshold_indices[channel_index]] = 0

                # Apply cluster-based thresholding (only clusters 0, 1, 2)
                else:
                    #print(f"Applying cluster-based thresholding for {channel}")
                    for index, label in enumerate(sample_kmeans_labels[:, channel_index]):
                        # If the mapping value is 'negative', set the matrix value to 0, If it’s positive, keep the original value (do nothing)
                        if label in threshold_mapping and threshold_mapping[label] == 'negative':
                            sample_matrix[index, threshold_indices[channel_index]] = 0

        # Update the matrix for this sample
        matrix[sample_indices] = sample_matrix
        print('Matrix shape after processing:', matrix.shape)

    #check how many 0s are in each column of thresholded channels
    for channel_index, channel in enumerate(threshold_channel_names):
        print(f'Channel: {channel}, Index {threshold_indices[channel_index]}, Number of 0s: {np.sum(matrix[:, threshold_indices[channel_index]] == 0)}')

    return matrix

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

def assign_mixed_celltype(cell_types_df, cluster_df, thresholding_dict, channel_names):

    print("Cell types df shape: ", cell_types_df.shape)
    print("Cell cluster array shape: ", cluster_df.shape)
    print('CD3e channel index:', channel_names.index('CD3e'))

    assert cell_types_df.shape[0] == cluster_df.shape[0], "Number of cells in cell types df and matrix do not match"

    mixed_cell_stats = {}

    for sample in np.unique(cell_types_df['slide_id'].values):
        print(f'Processing sample {sample}')
        #get heterogeneous cells for each sample
        sample_mixed_cells = cell_types_df[(cell_types_df['slide_id'] == sample) & (cell_types_df['cell_type'] == 'mixed Macrophages/Helper T cells')]
        print(f"Sample mixed cells shape: {sample_mixed_cells.shape}")
        print(f"Sample indices spread: {sample_mixed_cells.index[0]} ... {sample_mixed_cells.index[-1]}")

        sample_cluster_df = cluster_df[sample_mixed_cells.index - 1]
        print(f"Sample cluster array shape: {sample_cluster_df.shape}")

        assert sample_mixed_cells.shape[0] == sample_cluster_df.shape[0], "Number of cells in heterogenous cell types df and matrix do not match"

        cd3e_thresholds = thresholding_dict[sample]['CD3e']
        print(f"CD3e thresholds: {cd3e_thresholds}")

        helper_t_count = 0
        macrophage_count = 0
        
        # Assign cell types based on cluster values
        for i, cell_index in enumerate(sample_mixed_cells.index):
            cluster_value = sample_cluster_df[i]
            if cd3e_thresholds[cluster_value] == 'positive':
                #print(f'{cluster_value} is positive')
                cell_types_df.at[cell_index + 1, 'cell_type'] = 'Helper T cells'
                helper_t_count += 1
            elif cd3e_thresholds[cluster_value] == 'negative':
                #print(f'{cluster_value} is negative')
                cell_types_df.at[cell_index + 1, 'cell_type'] = 'Macrophages'
                macrophage_count += 1
        
        print(cell_types_df.loc[sample_mixed_cells.index, 'cell_type'].value_counts())
        print(cell_types_df.loc[sample_mixed_cells.index].head())
        print('')

        mixed_cell_stats[sample] = {
            'total_mixed_cells': int(sample_mixed_cells.shape[0]),
            'Helper T cells': int(helper_t_count),
            'Macrophages': int(macrophage_count)
        }

    return cell_types_df, mixed_cell_stats

def split_mixed_celltype(cell_type_name, cell_types_df, thresholded_matrix, channel_names):

    print("Cell types df shape: ", cell_types_df.shape)
    print("Cell matrix shape: ", thresholded_matrix.shape)
    
    assert cell_types_df.shape[0] == thresholded_matrix.shape[0], "Number of cells in cell types df and cell matrix do not match"
    
    mixed_cell_stats = {}

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
        stromal_cell_count = 0

        for i, cell_index in enumerate(single_cell_type_df_index):
            cell_arr = thresholded_matrix[cell_index]

            if cell_arr[channel_names.index('CD20')] > 0:
                #print('Cell is positive for CD20 and remains a B cell')
                b_cell_count += 1

            elif cell_arr[channel_names.index('CD3e')] > 0:
                if cell_arr[channel_names.index('CD8')] > 0:
                    #print('Cell is positive for CD20 and CD8 and becomes a cytotoxic T cell')
                    cell_types_df.at[cell_index + 1, 'cell_type'] = 'Cytotoxic T cells'
                    cytotoxic_t_count += 1
                elif cell_arr[channel_names.index('CD4')] > 0:
                    #print('Cell is positive for CD20 and CD4 and becomes a helper T cell')
                    cell_types_df.at[cell_index + 1, 'cell_type'] = 'Helper T cells'
                    helper_t_count += 1
                else:
                    #print('Cell is positive for CD20 and remains a B cell')
                    b_cell_count += 1

            else:
                cell_types_df.at[cell_index + 1, 'cell_type'] = 'Stromal cells (undefined)'
                stromal_cell_count += 1

        split_cells_stats = {
            'Original cell number': int(single_cell_type_df.shape[0]),
            'B cell': int(b_cell_count),
            'Helper T cells': int(helper_t_count),
            'Cytotoxic T cells': int(cytotoxic_t_count),
            'Stromal cells (undefined)': int(stromal_cell_count)
        }
        print(split_cells_stats)
        print('')
        
    if cell_type_name == 'T cells (other)':
        print(cell_type_name)
        helper_t_count = 0
        cytotoxic_t_count = 0
        t_cell_other_count = 0
        b_cell_count = 0 
        #stromal_cell_count = 0

        for i, cell_index in enumerate(single_cell_type_df_index):
            cell_arr = thresholded_matrix[cell_index]

            if cell_arr[channel_names.index('CD3e')] > 0:
                if cell_arr[channel_names.index('CD8')] > 0:
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
                #print('Cell is positive for CD8 and becomes a cytotoxic T cell')
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
                #print('Cell remains a T cells (other)')\
                t_cell_other_count += 1
                #print('Cell is not positive for cd3e according to thresholding')
                #cell_types_df.at[cell_index + 1, 'cell_type'] = 'Stromal cells (undefined)'
                #stromal_cell_count += 1
                
            
        split_cells_stats = {
            'Original cell number': int(single_cell_type_df.shape[0]),
            'T cells (other)': int(t_cell_other_count),
            'Cytotoxic T cells': int(cytotoxic_t_count),
            'Helper T cells': int(helper_t_count),
            'B cells': int(b_cell_count)#,
            #'Stromal cells (undefined)': int(stromal_cell_count)
        }
        print(split_cells_stats)
        print('')
        
    if cell_type_name == 'Helper T cells':
        print(cell_type_name)
        helper_t_count = 0
        cytotoxic_t_count = 0
        macrophage_count = 0
        t_cell_other_count = 0
        b_cell_count = 0
        stromal_cell_count = 0

        for i, cell_index in enumerate(single_cell_type_df_index):
            cell_arr = thresholded_matrix[cell_index]

            if cell_arr[channel_names.index('CD3e')] > 0:
                if cell_arr[channel_names.index('CD4')] > 0:
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
            'Macrophages': int(macrophage_count),
            'T cells (other)': int(t_cell_other_count),
            'B cells': int(b_cell_count),
            'Stromal cells (undefined)': int(stromal_cell_count)
        }
        print(split_cells_stats)
        print('')
    
    if cell_type_name == 'Cytotoxic T cells':
        print(cell_type_name)
        helper_t_count = 0
        cytotoxic_t_count = 0
        b_cell_count = 0
        t_cell_other_count = 0
        stromal_cell = 0 

        for i, cell_index in enumerate(single_cell_type_df_index):
            cell_arr = thresholded_matrix[cell_index]

            if cell_arr[channel_names.index('CD3e')] > 0:
                if cell_arr[channel_names.index('CD8')] > 0:
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
                #print('Cell remains a cytotoxic T cell')
                cytotoxic_t_count += 1
                #cell_types_df.at[cell_index + 1, 'cell_type'] = 'Stromal cells (undefined)'
                #stromal_cell += 1
            
        split_cells_stats = {
            'Original cell number': int(single_cell_type_df.shape[0]),
            'Cytotoxic T cells': int(cytotoxic_t_count),
            'Helper T cells': int(helper_t_count),
            'T cells (other)': int(t_cell_other_count),
            'B cells': int(b_cell_count)#,
            #'Stromal cells (undefined)': int(stromal_cell),
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
        stromal_cell_count = 0

        for i, cell_index in enumerate(single_cell_type_df_index):
            cell_arr = thresholded_matrix[cell_index]

            if cell_arr[channel_names.index('CD3e')] > 0:
                if cell_arr[channel_names.index('CD8')] > 0:
                    #print('Cell is positive for CD3e and CD8 and becomes a cytotoxic T cell')
                    cell_types_df.at[cell_index + 1, 'cell_type'] = 'Cytotoxic T cells'
                    cytotoxic_t_count += 1
                elif cell_arr[channel_names.index('CD4')] > 0:
                    #print('Cell is positive for CD3e and CD4 and becomes a helper T cell')
                    cell_types_df.at[cell_index + 1, 'cell_type'] = 'Helper T cells'
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
            
            #v2 - added this
            elif cell_arr[channel_names.index('CD8')] > 0:
                #print('Cell is positive for CD8 and becomes a Cytotoxic T cell')
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
            'Stromal cells (undefined)': int(stromal_cell_count)
        }
        print(split_cells_stats)
        print('')

    return cell_types_df, split_cells_stats
            
    




