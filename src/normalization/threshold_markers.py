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
        sample_indices = np.where(cell_sample_names == sample)[0]
        sample_matrix = matrix[sample_indices]

        # Load K-means labels for the sample
        sample_kmeans_labels_df = pd.read_csv(os.path.join(labels_dir, sample, f'lineage_markers_{n_clusters}clusters.csv')) 
        sample_kmeans_labels = sample_kmeans_labels_df[threshold_channel_names].to_numpy()

        # Iterate over channels in the thresholding dictionary
        for channel in threshold_channel_names:
            if channel in threshold_dict.get(sample, {}):  # Check if the sample is in the threshold_dict
                # Get the corresponding thresholding mapping for the current channel
                threshold_mapping = threshold_dict[sample][channel]

                # Iterate over each K-means label and its corresponding index
                for index, label in enumerate(sample_kmeans_labels[:, threshold_channel_names.index(channel)]):
                    # Check the value in the threshold mapping
                    if label in threshold_mapping:
                        # If the mapping value is 'negative', set the matrix value to 0
                        if threshold_mapping[label] == 'negative':
                            sample_matrix[index, threshold_channel_names.index(channel)] = 0
                        # If it’s positive, keep the original value (do nothing)

        # Update the matrix for this sample
        matrix[sample_indices] = sample_matrix

    # Save the thresholded matrix
    np.save(thresholded_matrix_path, matrix)
    print(f'Thresholded matrix saved at: {thresholded_matrix_path}')

if __name__ == '__main__':
    main()