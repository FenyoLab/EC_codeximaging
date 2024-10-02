import os
import sys
import numpy as np
import sklearn.cluster as cluster
import matplotlib.pyplot as plt
import seaborn as sns
import zarr
from skimage.transform import resize
from skimage.io import imsave

def cluster_tiles(mean_data_dir, n_clusters, clusters_dir):

    top5_means = np.load(os.path.join(mean_data_dir, 'top5percent_means.npy'))
    top5_means_reshaped = top5_means.reshape(-1, 1)

    sample_names = np.load(os.path.join(mean_data_dir, 'sample_names.npy'))
    unique_samples = np.unique(sample_names)

    for sample in unique_samples:
        sample_save_path = os.path.join(save_path, sample)
        os.makedirs(sample_save_path, exist_ok = True)
        kmeans_labels_path = os.path.join(sample_save_path, 'kmeans_labels.npy')
        if os.path.exists(kmeans_labels_path):
            print(f'Kmeans labels for sample {sample} tiles already exists')
            continue
        
        print(f'Processing sample {sample}')
        sample_indices = np.where(sample_names == sample)[0]
        sample_top5_means = top5_means_reshaped[sample_indices]

        kmeans = cluster.KMeans(n_clusters=n_clusters, random_state=0).fit(sample_top5_means)
        kmeans_labels = kmeans.labels_
        np.save(kmeans_labels_path, kmeans_labels)

        kmeans_cluster_centers = kmeans.cluster_centers_
        np.save(os.path.join(sample_save_path, 'kmeans_cluster_centers.npy'), kmeans_cluster_centers)

        plt.figure(figsize=(8, 4))
    
        colors = ['blue', 'orange', 'red', 'green', 'purple']  # Add more colors if needed
        for i in range(n_clusters):
            plt.scatter(sample_top5_means[kmeans_labels == i], 
                    np.zeros_like(sample_top5_means[kmeans_labels == i]), 
                    color=colors[i % len(colors)], label=f'Cluster {i} (mean={sample_top5_means[kmeans_labels == i].mean():.2f})')
            
            plt.scatter(kmeans_cluster_centers, [0]*n_clusters, color='black', marker='x', s=100, label='Cluster Centers')
        plt.title(f'Visualization of {n_clusters} Clusters')
        plt.xlabel('Mean Values')
        plt.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(sample_save_path, 'tile_kmeans_labels.png'))
        plt.close()

def create_cluster_masks(mean_data_dir, clusters_dir, data_dir, tile_size):
    sample_names = np.load(os.path.join(mean_data_dir, 'sample_names.npy'))
    tile_positions = np.load(os.path.join(mean_data_dir, 'tile_positions.npy'))

    unique_samples = np.unique(sample_names)

    # Define colors for each cluster (you can customize these colors)
    cluster_colors = {
        1: [255, 0, 0],     # Cluster 1: red
        2: [0, 255, 0],     # Cluster 2: green
        3: [0, 0, 255]      # Cluster 3: blue
    }

    # Loop through each sample
    for sample in unique_samples:
        save_path = os.path.join(clusters_dir, sample)
        combined_mask_path = os.path.join(save_path, f'combined_cluster_mask.png')
        if os.path.exists(combined_mask_path):
            print(f'Cluster masks for sample {sample} already exist')
            continue
        
        print(f'Processing sample {sample}')

        #load in zarr data 
        slide_path = f'{data_dir}/{sample}/data.zarr'
        print('Reading slide...')
        slide = zarr.load(slide_path) 
        print(f'Slide_shape: {slide.shape}')

        _, slide_height, slide_width = slide.shape
        grid_height, grid_width = slide_height // tile_size, slide_width // tile_size
        color_mask = np.zeros((slide_height, slide_width, 3), dtype=np.uint8)

        #load in sample cluster data
        kmeans_labels = np.load(os.path.join(clusters_dir, sample, 'kmeans_labels.npy'))
        unique_clusters = np.unique(kmeans_labels)

        #filter tile pos for sample
        sample_indices = np.where(sample_names == sample)[0]
        sample_tile_positions = tile_positions[sample_indices]

        # Loop through each cluster
        for cluster in unique_clusters:
            print(f'Processing cluster {cluster}')

            # Initialize an empty bw mask for this cluster
            bw_mask = np.zeros((slide_height, slide_width), dtype=np.uint8)

            #filter tile pos for cluster
            label_indices = np.where(kmeans_labels == cluster)[0]
            cluster_tile_positions = sample_tile_positions[label_indices]
            
            for pos in cluster_tile_positions:
                h = pos[0]  # 'h' is in the first column
                w = pos[1]
                # Assign the cluster color to the mask
                color_mask[h:h+tile_size, w:w+tile_size] = cluster_colors.get(cluster, [0, 0, 0])
                #assign white to bw mask
                bw_mask[h:h+tile_size, w:w+tile_size] = 1
            
            #resize bw mask and save
            bw_mask = resize(bw_mask, (grid_height, grid_width), order=0, anti_aliasing=False)
            img = (np.clip(bw_mask, 0, 1) * 255).astype(np.uint8)
            imsave(os.path.join(save_path, f'cluster_{cluster}_mask.png'), img)
            print(f'Cluster {cluster} mask saved as img for sample {sample}')
        
        #resize color mask and save
        color_mask = resize(color_mask, (slide_height // tile_size, slide_width // tile_size, 3), order=0, anti_aliasing=False, preserve_range=True) #optional
        color_mask = color_mask.astype(np.uint8)  #optional
        imsave(combined_mask_path, color_mask)
        print(f'Combined cluster mask saved for sample {sample}')


if __name__ == "__main__":
    main()