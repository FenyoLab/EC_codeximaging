import numpy as np

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
