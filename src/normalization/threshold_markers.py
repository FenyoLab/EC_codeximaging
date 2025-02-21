import os
import numpy as np
import pandas as pd 

def threshold_markers(data_dir, channel_names, threshold_dict, threshold_channel_names, save_path, n_clusters, output_suffix='thresholded_matrix'):
    matrix = np.load(os.path.join(data_dir, 'matrix.npy'))
    cell_sample_names = np.load(os.path.join(data_dir, 'cell_sample_names.npy'))

    output_path = os.path.join(save_path, output_suffix)
    os.makedirs(output_path, exist_ok=True)
    
    thresholded_matrix_path = os.path.join(output_path, 'matrix.npy')
    if os.path.exists(thresholded_matrix_path):
        print('Thresholded matrix already exists, skipping')
        return

    # Iterate over unique samples
    for sample in np.unique(cell_sample_names):
        print(f'Processing sample {sample}')
        sample_indices = np.where(cell_sample_names == sample)[0]
        sample_matrix = matrix[sample_indices]
        print(f'Sample matrix shape: {sample_matrix.shape}')

        # Load K-means labels for the sample
        sample_kmeans_labels_df = pd.read_csv(os.path.join(data_dir, 'omero_tables', sample, f'lineage_markers_{n_clusters}clusters.csv')) 
        sample_kmeans_labels = sample_kmeans_labels_df[threshold_channel_names].to_numpy()
        print(f'Sample kmeans labels: {sample_kmeans_labels.shape}')

        assert sample_matrix.shape[0] == sample_kmeans_labels.shape[0], \
    f"Mismatch: Sample matrix has {sample_matrix.shape[0]} rows, while kmeans labels have {sample_kmeans_labels.shape[0]}."

        threshold_indices = [channel_names.index(channel) for channel in threshold_channel_names if channel in channel_names]
        print(threshold_indices)
    
        # Iterate over channels in the thresholding dictionary
        for channel_index, channel in enumerate(threshold_channel_names):
            #if channel in ['MPO', 'CD8', 'CD3e', 'Ecadherin', 'DAPI']:
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
                    print(f"Applying lower cutoff of {lower_cutoff} and upper cutoff of {upper_cutoff} for {channel}")
                    sample_matrix[sample_matrix[:, threshold_indices[channel_index]] < lower_cutoff, threshold_indices[channel_index]] = 0
                    sample_matrix[sample_matrix[:, threshold_indices[channel_index]] > upper_cutoff, threshold_indices[channel_index]] = 0

                # Check if the channel uses only lower cutoff thresholding
                elif 'lower_cutoff' in threshold_mapping:
                    lower_cutoff = threshold_mapping['lower_cutoff']
                    print(f"Applying lower cutoff of {lower_cutoff} for {channel}")
                    sample_matrix[sample_matrix[:, threshold_indices[channel_index]] < lower_cutoff, threshold_indices[channel_index]] = 0

                # Check if the channel uses upper cutoff in addition to cluster-based thresholding
                elif 'upper_cutoff' in threshold_mapping:
                    upper_cutoff = threshold_mapping['upper_cutoff']
                    print(f"Applying cluster-based + upper cutoff (of {upper_cutoff}) thresholding for {channel}")

                    # Apply cluster-based thresholding
                    for index, label in enumerate(sample_kmeans_labels[:, channel_index]):
                        if label in threshold_mapping and threshold_mapping[label] == 'negative':
                            sample_matrix[index, threshold_indices[channel_index]] = 0
                
                    # Apply upper cutoff thresholding
                    sample_matrix[sample_matrix[:, threshold_indices[channel_index]] > upper_cutoff, threshold_indices[channel_index]] = 0

                # Apply cluster-based thresholding (only clusters 0, 1, 2)
                else:
                    print(f"Applying cluster-based thresholding for {channel}")
                    for index, label in enumerate(sample_kmeans_labels[:, channel_index]):
                        # If the mapping value is 'negative', set the matrix value to 0, If it’s positive, keep the original value (do nothing)
                        if label in threshold_mapping and threshold_mapping[label] == 'negative':
                            sample_matrix[index, threshold_indices[channel_index]] = 0

        # Update the matrix for this sample
        matrix[sample_indices] = sample_matrix

    # Save the thresholded matrix
    np.save(thresholded_matrix_path, matrix)
    np.save(os.path.join(output_path, 'cell_sample_names.npy'), cell_sample_names)
    print(f'Thresholded matrix saved at: {thresholded_matrix_path}')

if __name__ == '__main__':
    main()