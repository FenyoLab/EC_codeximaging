import os
import numpy as np
import pandas as pd
import sklearn.cluster as cluster
import zarr
from skimage.transform import resize
from skimage.io import imsave
import json

def main():
    metadata_path = '/gpfs/data/proteomics/projects/Endometrial_mIF/EC_codeximaging_results/out_12-2-24/celltypes/27_clusters/metadata_with_celltypes.csv'
    save_path = '/gpfs/data/proteomics/projects/Endometrial_mIF/EC_codeximaging_results/out_12-2-24/remove_necrosis'
    image_dir = '/gpfs/data/proteomics/projects/Endometrial_mIF/EC_codeximaging_results/out_256/data'
    calculate_percentage_neutrophils(metadata_path, image_dir, save_path)
    cluster_tiles(save_path, image_dir)

def calculate_percentage_neutrophils(metadata_path, image_dir, save_path, tiles_dir = 'tiles_11_13'):
    #load the metadata 
    metadata = pd.read_csv(metadata_path, index_col=0)
    print(metadata.head())

    os.makedirs(save_path, exist_ok=True)

    for sample in metadata['slide_id'].unique():
        print(f'Processing sample: {sample}')
        sample_metadata = metadata[metadata['slide_id'] == sample]

        tile_positions_df = pd.read_csv(os.path.join(image_dir, sample, tiles_dir, 'positions_256.csv'), index_col=0)

        neutrophil_percentage = []

        for tile_index, (tile_h, tile_w) in tile_positions_df.iterrows():
            tile_data = sample_metadata[(sample_metadata['tile_h'] == tile_h) & (sample_metadata['tile_w'] == tile_w)]

            #calculate percentage of neutrophils of the total cells in the tile
            neutrophils_count = tile_data[tile_data['cell_type'] == 'Neutrophils'].shape[0]
            total_cells = tile_data.shape[0]
            if total_cells == 0:
                percentage = 0
            else:
                percentage = (neutrophils_count / total_cells) * 100 

            neutrophil_percentage.append({'tile_h': tile_h, 'tile_w': tile_w, 'neutrophil_percentage': percentage})
        
        #create new df with tile_h, tile_w, neutrophil_percentage
        neutrophil_percentage_df = pd.DataFrame(neutrophil_percentage)
        neutrophil_percentage_df.index += 1
        print(neutrophil_percentage_df.head())
        
        sample_save_path = os.path.join(save_path, sample)
        os.makedirs(sample_save_path, exist_ok=True)

        neutrophil_percentage_df.to_csv(os.path.join(sample_save_path, 'neutrophil_percentage.csv'))

def cluster_tiles(remove_necrosis_path, image_dir):
    for sample in os.listdir(remove_necrosis_path):
        print(f'Processing sample: {sample}')
        sample_path = os.path.join(remove_necrosis_path, sample)
        neutrophil_percentage_df = pd.read_csv(os.path.join(sample_path, 'neutrophil_percentage.csv'), index_col=0)

        neutrophil_percentages = neutrophil_percentage_df['neutrophil_percentage'].values.reshape(-1, 1)

        #2 clusters
        kmeans = cluster.KMeans(n_clusters=2, random_state=0).fit(neutrophil_percentages)
        kmeans_labels = kmeans.labels_
        kmeans_cluster_centers = kmeans.cluster_centers_
        neutrophil_percentage_df['clusters_2'] = kmeans_labels
        np.save(os.path.join(sample_path, 'kmeans_2_cluster_centers.npy'), kmeans_cluster_centers)

        #3 clusters
        kmeans = cluster.KMeans(n_clusters=3, random_state=0).fit(neutrophil_percentages)
        kmeans_labels = kmeans.labels_
        kmeans_cluster_centers = kmeans.cluster_centers_
        neutrophil_percentage_df['clusters_3'] = kmeans_labels
        np.save(os.path.join(sample_path, 'kmeans_3_cluster_centers.npy'), kmeans_cluster_centers)

        neutrophil_percentage_df.to_csv(os.path.join(sample_path, 'neutrophil_percentage.csv'))
        
        create_cluster_masks(neutrophil_percentage_df, sample_path, image_dir)

def create_cluster_masks(data_df, sample_save_path, image_dir, tile_size=256):
    sample = os.path.basename(sample_save_path)

    # Load Zarr data
    slide_path = f'{image_dir}/{sample}/data.zarr'
    slide = zarr.open(slide_path, mode='r')  # Opens the Zarr array in read-only mode
    print(f'Slide_shape: {slide.shape}')

    _, slide_height, slide_width = slide.shape
    grid_height, grid_width = slide_height // tile_size, slide_width // tile_size

    mask_2_clusters = np.zeros((slide_height, slide_width), dtype=np.uint8)
    mask_3_clusters = np.zeros((slide_height, slide_width), dtype=np.uint8)

    # Load cluster centers
    cluster_centers_2 = np.load(os.path.join(sample_save_path, 'kmeans_2_cluster_centers.npy'))
    cluster_centers_3 = np.load(os.path.join(sample_save_path, 'kmeans_3_cluster_centers.npy'))
    save_cluster_centers(sample_save_path, cluster_centers_2, cluster_centers_3)

    # Determine cluster rankings
    cluster_ranks_2 = np.argsort(cluster_centers_2.flatten())  # Get sorted indices for 2 clusters
    cluster_ranks_3 = np.argsort(cluster_centers_3.flatten())  # Get sorted indices for 3 clusters

    # Map clusters to colors
    cluster_color_map_2 = {cluster_ranks_2[0]: 0,  # Black for lower center
                           cluster_ranks_2[1]: 255}  # White for higher center
    cluster_color_map_3 = {cluster_ranks_3[0]: 0,    # Black for lowest center
                           cluster_ranks_3[1]: 75,  # Gray for middle center
                           cluster_ranks_3[2]: 255}  # White for highest center

    # Process tiles and create masks
    for _, row in data_df.iterrows():
        tile_h, tile_w = int(row['tile_h']), int(row['tile_w'])

        # Update 2-cluster mask
        cluster_label_2 = row['clusters_2']
        mask_2_clusters[tile_h:tile_h + tile_size, tile_w:tile_w + tile_size] = cluster_color_map_2[cluster_label_2]

        # Update 3-cluster mask
        cluster_label_3 = row['clusters_3']
        mask_3_clusters[tile_h:tile_h + tile_size, tile_w:tile_w + tile_size] = cluster_color_map_3[cluster_label_3]
    
    #resize masks to grid size
    mask_2_clusters_resized = resize(mask_2_clusters, (grid_height, grid_width), order=0, anti_aliasing=False)
    mask_3_clusters_resized = resize(mask_3_clusters, (grid_height, grid_width), order=0, anti_aliasing=False)

    #save masks
    imsave(os.path.join(sample_save_path, '2_clusters_mask.png'), mask_2_clusters_resized)
    imsave(os.path.join(sample_save_path, '3_clusters_mask.png'), mask_3_clusters_resized)

def save_cluster_centers(sample_save_path, cluster_centers_2, cluster_centers_3):
    # Flatten the cluster centers to 1D arrays
    cluster_centers_2_flat = cluster_centers_2.flatten().tolist()  # Flatten the array and convert to list
    cluster_centers_3_flat = cluster_centers_3.flatten().tolist()  # Flatten the array and convert to list

    # Convert the cluster centers to a simple dictionary
    cluster_data = {
        "clusters_2": cluster_centers_2_flat,
        "clusters_3": cluster_centers_3_flat
    }

    # Save to JSON
    json_path = os.path.join(sample_save_path, 'cluster_centers.json')
    with open(json_path, 'w') as json_file:
        json.dump(cluster_data, json_file, indent=4)
    print(f"Cluster centers saved to {json_path}")







if __name__ == '__main__':
    main()