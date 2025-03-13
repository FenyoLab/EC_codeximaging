import os
import sys
import numpy as np
import pandas as pd

def new_positions(mean_data_dir, clusters_dir, positions_dir, tiles_dir, tile_size):
    '''Function to assign tissue identity to each tile based on the kmeans clustering'''
    sample_names = np.load(os.path.join(mean_data_dir, 'sample_names.npy'))
    tile_positions = np.load(os.path.join(mean_data_dir, 'tile_positions.npy'))
    
    for sample in np.unique(sample_names):
        sample_positions_path = os.path.join(positions_dir, sample, tiles_dir)
        os.makedirs(sample_positions_path, exist_ok=True)
        
        print(f'Processing samples {sample}')

        membane_marker_pos_positions = []
        membane_marker_neg_positions = []

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
        membane_marker_pos_positions = sample_tile_positions[np.isin(kmeans_labels, higher_center_labels)]
        membane_marker_neg_positions = sample_tile_positions[kmeans_labels == lowest_center_label]

        membane_marker_pos_positions_arr = np.array(membane_marker_pos_positions)
        membane_marker_neg_positions_arr = np.array(membane_marker_neg_positions)
        print("membrane_marker+ positions length: ", len(membane_marker_pos_positions_arr))
        print("membrane_marker- positions length: ", len(membane_marker_neg_positions_arr))

        membane_marker_pos_positions_df = pd.DataFrame({'h': membane_marker_pos_positions_arr[:, 0], 'w': membane_marker_pos_positions_arr[:, 1]})
        membane_marker_pos_positions_df.to_csv(os.path.join(sample_positions_path, f'membrane_marker+_positions_{tile_size}.csv'), index=True)

        membane_marker_neg_positions_df = pd.DataFrame({'h': membane_marker_neg_positions_arr[:, 0], 'w': membane_marker_neg_positions_arr[:, 1]})
        membane_marker_neg_positions_df.to_csv(os.path.join(sample_positions_path, f'membrane_marker-_positions_{tile_size}.csv'), index=True)
        print(f'membrane_marker+ and membrane_marker- positions saved for {sample}')

if __name__ == "__main__":
    main()