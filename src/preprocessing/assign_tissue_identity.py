import os
import sys
import numpy as np
import pandas as pd

def new_positions(mean_data_dir, clusters_dir, positions_dir, tile_size):
    sample_names = np.load(os.path.join(mean_data_dir, 'sample_names.npy'))
    tile_positions = np.load(os.path.join(mean_data_dir, 'tile_positions.npy'))
    
    unique_samples = np.unique(sample_names)

    for sample in unique_samples:
        sample_positions_path = os.path.join(positions_dir, sample)
        os.makedirs(sample_positions_path, exist_ok=True)
        positions_df_path = os.path.join(sample_positions_path, f'ecad+_positions_{tile_size}.csv')
        if os.path.exists(positions_df_path):
            print(f'Tissue identities already assigned for sample {sample}')
            continue
        
        print(f'Processing samples {sample}')

        ecad_pos_positions = []
        ecad_neg_positions = []

        sample_indices = (sample_names == sample)
        sample_tile_positions = tile_positions[sample_indices]
        kmeans_labels = np.load(os.path.join(clusters_dir, sample, 'kmeans_labels.npy'))
        cluster_centers = np.load(os.path.join(clusters_dir, sample, 'kmeans_cluster_centers.npy'))
        print(cluster_centers)

        # Determine which cluster has the higher center
        higher_center_label = np.argmax(cluster_centers) 
        lower_center_label = np.argmin(cluster_centers) 
        print(f"higher_center_label: {higher_center_label}")
        print(f"lower_center_label: {lower_center_label}")

        # Assign positions based on the cluster label
        ecad_pos_positions = sample_tile_positions[kmeans_labels == higher_center_label]
        ecad_neg_positions = sample_tile_positions[kmeans_labels == lower_center_label]

        ecad_pos_positions_arr = np.array(ecad_pos_positions)
        ecad_neg_positions_arr = np.array(ecad_neg_positions)

        ecad_pos_positions_df = pd.DataFrame({'h': ecad_pos_positions_arr[:, 0], 'w': ecad_pos_positions_arr[:, 1]})
        ecad_pos_positions_df.to_csv(os.path.join(sample_positions_path, f'ecad+_positions_{tile_size}.csv'), index=True)

        ecad_neg_positions_df = pd.DataFrame({'h': ecad_neg_positions_arr[:, 0], 'w': ecad_neg_positions_arr[:, 1]})
        ecad_neg_positions_df.to_csv(os.path.join(sample_positions_path, f'ecad-_positions_{tile_size}.csv'), index=True)
        print(f'Ecad+ and ecad- positions saved for {sample}')

if __name__ == "__main__":
    main()