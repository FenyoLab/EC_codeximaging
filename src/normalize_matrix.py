import os
import time

import numpy as np
import pandas as pd

def get_normalized_matrix(save_path, raw_data_dir, thresholded_dir, channel_names, filtered_channel_names, output_suffix = 'normalized_matrix', samples_to_remove = None):
    start_time = time.time()

    output_path = f'{save_path}/{output_suffix}'
    os.makedirs(output_path, exist_ok = True)

    #skip function if normalized and filtered matrix already exists
    matrix_normal_filtered_path = os.path.join(output_path, 'matrix_normal_filtered_markers.npy') #if matrix already exists, skip
    if os.path.exists(matrix_normal_filtered_path):
        print('Filtered and normalized matrix already exists, skipping')
        return

    if samples_to_remove is not None:
        matrix_dir = os.path.join(save_path, 'matrix_filtered_samples')
        os.makedirs(matrix_dir, exist_ok = True)
        from src.normalization.filter_matrix import filter_by_sample
        filter_by_sample(raw_data_dir, matrix_dir, thresholded_dir, samples_to_remove)
        matrix_filtered, dapi_filter = filter_matrix_rows(output_path, matrix_dir)
        filter_metadata(dapi_filter, matrix_dir, output_path)
    
    else:
        matrix_filtered, dapi_filter = filter_matrix_rows(output_path, thresholded_dir)
        filter_metadata(dapi_filter, raw_data_dir, output_path)

    normalize_matrix(output_path, matrix_filtered, channel_names)
    filter_matrix_columns(output_path, channel_names, filtered_channel_names)

    end_time = time.time()  # Record the end time
    elapsed_time = end_time - start_time
    
    print("Matrix filtered and normalized")
    print(f"Time elapsed: {elapsed_time:.2f} seconds")

def filter_matrix_rows(output_path, matrix_dir): #, channel_names):
 
    raw_matrix_path = os.path.join(matrix_dir, 'matrix.npy')
    from src.normalization.filter_matrix import filter_by_dapi_threshold
    matrix_filtered, dapi_filter = filter_by_dapi_threshold(raw_matrix_path, output_path)

    '''old way where biomarkers were filtered first'''
    #from src.normalization.filter_matrix import filter_by_biomarker
    #matrix_filtered = filter_by_biomarker(os.path.join(cell_marker_matrix_dir, 'matrix.npy'), channel_names, filtered_channel_names)

    #from src.normalization.filter_matrix import filter_by_dapi_threshold
    #matrix_filtered, dapi_filter = filter_by_dapi_threshold(matrix_filtered, output_path)

    #from src.normalization.filter_matrix import filter_by_doublets
    #filtered_matrix = filter_by_doublets(filtered_matrix_b)

    #np.save(matrix_filtered_path, matrix_filtered)
    return matrix_filtered, dapi_filter #, channels_filtered

def filter_metadata(dapi_filter, matrix_dir, output_path): 

    #load data 
    cell_sample_names = np.load(os.path.join(matrix_dir, 'cell_sample_names.npy'))
    metadata = pd.read_csv(os.path.join(matrix_dir, 'metadata.csv'), index_col = 0)

    #filter data by dapi threshold
    cell_sample_names_filtered = cell_sample_names[dapi_filter]
    filtered_metadata = metadata[dapi_filter]

    print("Metadata filtered shape:", filtered_metadata.shape)
    print("Cell sample names filtered shape:", cell_sample_names_filtered.shape)
    
    #save filtered data 
    np.save(os.path.join(output_path, 'cell_sample_names_filtered.npy'), cell_sample_names_filtered)
    filtered_metadata.to_csv(os.path.join(output_path, 'metadata_filtered.csv'), index=True)
    print("Filtered metadata saved")

def normalize_matrix(output_path, matrix_filtered, channel_names):

    print("Matrix filtered by rows shape:", matrix_filtered.shape)

    #cap matrix to 99th percentile values per biomarker
    matrix_capped = np.clip(matrix_filtered, 0, np.percentile(matrix_filtered, 99, axis=0))

    #appy zscore and arcsinh transformation
    cell_sample_names_filtered = np.load(os.path.join(output_path, 'cell_sample_names_filtered.npy'))
    unique_sample_names, indices = np.unique(cell_sample_names_filtered, return_index=True)
    unique_sample_names = unique_sample_names[np.argsort(indices)]#sort them in order of when they show up

    num_channels = len(channel_names)
    normalized_matrix = np.empty((0, num_channels))

    for sample_name in unique_sample_names:
        #get indices were sample_ids == sample_id
        #get the same matrix rows
        sample_filter = cell_sample_names_filtered == sample_name
        sample_matrix = matrix_capped[sample_filter]
        print(sample_name, sample_matrix.shape)

        for col in range(num_channels):
            array = sample_matrix[:, col]
            mean = np.mean(array)
            std = np.std(array)
            print(col, std)
            array_zscore = (array - mean) / std
            array_arcsinh = np.arcsinh(array_zscore)

            sample_matrix[:, col] = array_arcsinh
        
        normalized_matrix = np.concatenate((normalized_matrix, sample_matrix), axis=0)

    print("Matrix normalized per patient shape:", normalized_matrix.shape)
    np.save(os.path.join(output_path, 'matrix_normal.npy'), normalized_matrix)
    print("Normalized matrix saved")

def filter_matrix_columns(output_path, channel_names, filtered_channel_names):
    matrix_normal_path = os.path.join(output_path, 'matrix_normal.npy') 

    from src.normalization.filter_matrix import filter_by_biomarker
    filtered_matrix = filter_by_biomarker(matrix_normal_path, channel_names, filtered_channel_names)

    np.save(os.path.join(output_path, 'matrix_normal_filtered_markers.npy'), filtered_matrix)
    print("Normal matrix filtered by biomarkers saved")


#matrix_dir = '/gpfs/data/proteomics/projects/Endometrial_mIF/EC_codeximaging/out_8-26-24/matrix_filtered_samples'
#output_path = '/gpfs/data/proteomics/projects/Endometrial_mIF/EC_codeximaging/out_8-26-24/matrix_filtered_samples/normalized_matrix_new'
#matrix_filtered, dapi_filter = filter_matrix_rows(output_path, matrix_dir)
#ilter_metadata(dapi_filter, matrix_dir, output_path)