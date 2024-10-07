import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.cluster import KMeans
from src.omero_tables.create_omero_table import create_omero_table


def lineage_marker_cluster_tables(segmentation_data_dir, channel_names, thresholding_channel_names, omero_dict, save_dir, n_clusters, table_name):   

    #load data
    matrix = np.load(os.path.join(segmentation_data_dir, 'matrix.npy'))
    cell_sample_names = np.load(os.path.join(segmentation_data_dir, 'cell_sample_names.npy'))

    for sample in np.unique(cell_sample_names):
        os.makedirs(os.path.join(save_dir, sample), exist_ok = True)
        table_path = os.path.join(save_dir, sample, f'{table_name}.csv')
        if os.path.exists(table_path):
            print(f'Omero table of lineage marker clusters already saved for sample {sample}')
            continue
        
        print(f'Processing sample {sample}')
        sample_indices = np.where(cell_sample_names == sample)[0] 
        sample_matrix = matrix[sample_indices, :]

        marker_df = cluster_marker_means(sample_matrix, channel_names, thresholding_channel_names, n_clusters)
        roi_value = omero_dict.get(sample, {}).get('roi_id')
        
        omero_df = create_omero_table(marker_df, roi_value)
        print(omero_df.head())

        omero_df.to_csv(table_path, index = False)
        print(f'Omero table of lineage marker clusters saved for {sample}')

def cluster_marker_means(sample_matrix, channel_names, thresholding_channel_names, n_clusters):
    kmeans_channel = []
    for channel in thresholding_channel_names:
        print(f'Channel: {channel}')
        channel_index = channel_names.index(channel)
        sample_channel_array = sample_matrix[:, channel_index]
        sample_channel_array = sample_channel_array.reshape(-1, 1)
        kmeans = KMeans(n_clusters=n_clusters, random_state=0).fit(sample_channel_array)
        cluster_labels = kmeans.labels_
        cluster_centers = kmeans.cluster_centers_
        kmeans_channel.append(cluster_labels)
        
    kmeans_channel_stacked = np.column_stack(kmeans_channel)
    kmeans_df = pd.DataFrame(kmeans_channel_stacked, columns = thresholding_channel_names)
    return kmeans_df