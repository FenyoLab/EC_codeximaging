import numpy as np
import os
import pandas as pd

def filter_by_dapi_threshold(matrix_path, save_path): #switched filterede_matrix to matrix_path bc didnt do biomarker filtering first 
    matrix = np.load(matrix_path) #added this line to load matrix
    print("Raw matrix shape:", matrix.shape)
    dapi_channel = matrix[:, 0] #isolate dapi channel from matrix 
    
    from src.normalization.dapi_distribution import plot_dapi_distribution
    dapi_threshold = plot_dapi_distribution(dapi_channel, save_path) #get dapi threshold from channel distribution 
    
    dapi_filter = dapi_channel >= dapi_threshold #extract rows with dapi channel >= threshold
    matrix_filtered = matrix[dapi_filter] #filter matrix by dapi threshold
    print("Matrix filtered by dapi threshold shape:", matrix_filtered.shape)

    return matrix_filtered, dapi_filter

def filter_by_doublets(matrix_filtered):
    pass

def filter_by_biomarker(normal_matrix_path, channel_names, filtered_channel_names): #will this now go last? 
    normal_matrix = np.load(normal_matrix_path)
    print("Normalized_matrix shape:", normal_matrix.shape)

    print("All channel names:", channel_names, len(channel_names))
    print("Filtered channel names:", filtered_channel_names, (len(filtered_channel_names)))
    filtered_indices = [i for i, channel in enumerate(channel_names) if channel in filtered_channel_names]

    filtered_matrix = normal_matrix[:, filtered_indices]
    print("Normal matrix filtered by biomarkers shape:", filtered_matrix.shape)

    return filtered_matrix

def filter_by_sample(raw_data_dir, output_dir, samples_to_remove):
    # Load the data
    cell_sample_names = np.load(os.path.join(raw_data_dir, 'cell_sample_names.npy'))
    metadata_df = pd.read_csv(os.path.join(raw_data_dir, 'metadata.csv'), index_col=0)
    matrix = np.load(os.path.join(raw_data_dir, 'matrix.npy'))

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
    np.save(os.path.join(output_dir, 'cell_sample_names.npy'), cell_sample_names)
    np.save(os.path.join(output_dir, 'matrix.npy'), matrix)
    metadata_df.to_csv(os.path.join(output_dir, 'metadata.csv'), index=True)