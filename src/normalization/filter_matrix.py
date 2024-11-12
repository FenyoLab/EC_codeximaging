import numpy as np
import os
import pandas as pd

def filter_by_dapi_threshold(matrix_path, raw_sample_names_path, threshold_dict, channel_names, save_path): #switched filterede_matrix to matrix_path bc didnt do biomarker filtering first 
    matrix = np.load(matrix_path) #added this line to load matrix
    cell_sample_names = np.load(raw_sample_names_path)
    print("Raw matrix shape:", matrix.shape)
    print("Raw cell sample names shape:", cell_sample_names.shape)

    assert matrix.shape[0] == cell_sample_names.shape[0], "Mismatch: Matrix has {matrix.shape[0]} rows, while cell sample names have {cell_sample_names.shape[0]}."
    dapi_filter_arr = np.zeros(matrix.shape[0], dtype=bool)
    count = 0 

    unique_samples, sample_order = np.unique(cell_sample_names, return_index=True)
    unique_samples = unique_samples[np.argsort(sample_order)]  

    for sample in unique_samples:
        print(f'Processing sample {sample}')
        sample_indices = np.where(cell_sample_names == sample)[0]
        sample_matrix = matrix[sample_indices]
        print(f'Sample matrix shape: {sample_matrix.shape}')

        dapi_index = channel_names.index('DAPI')
        dapi_threshold = threshold_dict[sample]['DAPI']
        print(f'DAPI threshold for {sample}: {dapi_threshold}')

        dapi_channel = sample_matrix[:, dapi_index] #isolate dapi channel from matrix 
        from src.normalization.dapi_distribution import plot_dapi_distribution
        dapi_dist_save_path = os.path.join(save_path, 'dapi_distributions')
        os.makedirs(dapi_dist_save_path, exist_ok=True)
        plot_dapi_distribution(dapi_channel, dapi_threshold, sample, dapi_dist_save_path)

        dapi_filter = sample_matrix[:, dapi_index] >= dapi_threshold
        dapi_filter_arr[sample_indices] = dapi_filter

        sample_matrix[:, dapi_index] = np.where(sample_matrix[:, dapi_index] < dapi_threshold, 0, sample_matrix[:, dapi_index])
        #print how many cells have dapi = 0
        cells_removed = np.sum(sample_matrix[:, dapi_index] == 0)
        print(f"Number of cells with DAPI = 0: {cells_removed}")
        print('')
        count += cells_removed

        # Replace original matrix rows for this sample with the modified sample matrix
        matrix[sample_indices] = sample_matrix
    
    #remove rows from matrix where dapi channel == 0 
    matrix_filtered = matrix[dapi_filter_arr]
    print("Matrix filtered by dapi threshold shape:", matrix_filtered.shape)
    print(f"Total number of cells removed: {count}")

    return matrix_filtered, dapi_filter_arr

def filter_by_doublets(matrix_filtered):
    pass

def filter_by_biomarker(normal_matrix_path, channel_names, lineage_markers): #will this now go last? 
    normal_matrix = np.load(normal_matrix_path)
    print("Normalized_matrix shape:", normal_matrix.shape)

    print("All channel names:", channel_names, len(channel_names))
    print("Filtered channel names:", lineage_markers, (len(lineage_markers)))
    filtered_indices = [i for i, channel in enumerate(channel_names) if channel in lineage_markers]

    filtered_matrix = normal_matrix[:, filtered_indices]
    print("Normal matrix filtered by biomarkers shape:", filtered_matrix.shape)

    return filtered_matrix

def filter_by_sample(raw_data_dir, output_dir, thresholded_dir, samples_to_remove):
    # Load the data
    cell_sample_names = np.load(os.path.join(raw_data_dir, 'cell_sample_names.npy'))
    metadata_df = pd.read_csv(os.path.join(raw_data_dir, 'metadata.csv'), index_col=0)
    matrix = np.load(os.path.join(thresholded_dir, 'matrix.npy'))

    matrix_filtered_by_sample_path = os.path.join(output_dir, 'matrix.npy')
    if os.path.exists(matrix_filtered_by_sample_path):
        print('Matrix filtered by sample already exists, skipping')
        return

    # Find indices to remove
    indices_to_remove = []
    for sample in samples_to_remove:
        indices = np.where(cell_sample_names == sample)[0]
        indices_to_remove.extend(indices.tolist())

    print(f'Removing {len(indices_to_remove)} rows for {len(samples_to_remove)} samples')

    # Remove indices from data
    print("Cell sample names shape before:", cell_sample_names.shape)
    cell_sample_names = np.delete(cell_sample_names, indices_to_remove)
    print("Cell sample names shape after:", cell_sample_names.shape)

    print("Matrix shape before:", matrix.shape)
    matrix = np.delete(matrix, indices_to_remove, axis=0)
    print("Matrix shape after:", matrix.shape)

    print("Metadata shape before:", metadata_df.shape)
    metadata_df = metadata_df.drop(indices_to_remove)
    print("Metadata shape after:", metadata_df.shape)

    # Save the filtered data
    np.save(matrix_filtered_by_sample_path, matrix)
    np.save(os.path.join(output_dir, 'cell_sample_names.npy'), cell_sample_names)
    metadata_df.to_csv(os.path.join(output_dir, 'metadata.csv'), index=True)