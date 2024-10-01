import os
import numpy as np
import pandas as pd 

def threshold_markers(data_dir, channel_names, threshold_dict, save_path, output_suffix = 'thresholded_matrix'):
    matrix = np.load(os.path.join(data_dir, 'matrix.npy'))
    cell_sample_names = np.load(os.path.join(data_dir, 'cell_sample_names.npy'))

    output_path = f'{save_path}/{output_suffix}'
    os.makedirs(output_path, exist_ok = True)
    
    thresholded_matrix_path = os.path.join(output_path, 'matrix.npy')
    if os.path.exists(thresholded_matrix_path):
        print('Thresholded matrix already exists, skipping')
        return

    unique_samples = np.unique(cell_sample_names)

    for sample in unique_samples:

        sample_indices = np.where(cell_sample_names == sample)[0]
        sample_matrix = matrix[sample_indices]

        if sample in threshold_dict:
            thresholds = threshold_dict[sample]
            print(f'Processing sample {sample} {thresholds}')
            
            # Loop over all channels that have a threshold for this sample
            for channel, threshold_value in thresholds.items():
                # Find the index of the channel in channel_names
                if channel in channel_names:
                    channel_idx = channel_names.index(channel)
                    
                    # Apply threshold: set values in this channel that are below the threshold to 0
                    sample_matrix[:, channel_idx] = np.where(sample_matrix[:, channel_idx] < threshold_value, np.float64(0), sample_matrix[:, channel_idx])

        # Store the updated sample matrix back into the original matrix
        matrix[sample_indices] = sample_matrix

    # Save the updated matrix back to file
    np.save(thresholded_matrix_path, matrix)

if __name__ == '__main__':
    main()