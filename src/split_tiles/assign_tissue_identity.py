import os
import sys
import numpy as np
import pandas as pd

def new_positions(mean_data_dir, clusters_dir, positions_dir, tiles_dir, tile_size):
    sample_names = np.load(os.path.join(mean_data_dir, 'sample_names.npy'))
    tile_positions = np.load(os.path.join(mean_data_dir, 'tile_positions.npy'))
    
    for sample in np.unique(sample_names):
        sample_positions_path = os.path.join(positions_dir, sample, tiles_dir)
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
        sorted_indices = np.argsort(cluster_centers.flatten())  # Sort by cluster center values
        lowest_center_label = sorted_indices[0]  # Cluster with the lowest center
        higher_center_labels = sorted_indices[1:]
        
        print(f"Lowest center label: {lowest_center_label}")
        print(f"Higher center labels: {higher_center_labels}")

        # Assign positions based on the cluster label
        ecad_pos_positions = sample_tile_positions[np.isin(kmeans_labels, higher_center_labels)]
        ecad_neg_positions = sample_tile_positions[kmeans_labels == lowest_center_label]

        ecad_pos_positions_arr = np.array(ecad_pos_positions)
        ecad_neg_positions_arr = np.array(ecad_neg_positions)
        print("Ecad+ positions length: ", len(ecad_pos_positions_arr))
        print("Ecad- positions length: ", len(ecad_neg_positions_arr))

        ecad_pos_positions_df = pd.DataFrame({'h': ecad_pos_positions_arr[:, 0], 'w': ecad_pos_positions_arr[:, 1]})
        ecad_pos_positions_df.to_csv(os.path.join(sample_positions_path, f'ecad+_positions_{tile_size}.csv'), index=True)

        ecad_neg_positions_df = pd.DataFrame({'h': ecad_neg_positions_arr[:, 0], 'w': ecad_neg_positions_arr[:, 1]})
        ecad_neg_positions_df.to_csv(os.path.join(sample_positions_path, f'ecad-_positions_{tile_size}.csv'), index=True)
        print(f'Ecad+ and ecad- positions saved for {sample}')

if __name__ == "__main__":
    main()