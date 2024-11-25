import sys
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import zscore
import pdb

def gen_cluster_centroid_matrix(matrix_path, labels_path, plot_dir, n_clusters, channel_names=None):
    
    if os.path.exists(f'{plot_dir}/cluster_centroids_df.csv'):  #if clustering already exists, skip
        print('cluster_centroids_df already exists, skipping')
        return
    
    print("generating cluster_centroids_df")

    # Load data
    matrix = np.load(matrix_path)
    print(matrix.shape)

    # Load labels
    labels = np.load(labels_path)
    unique_labels = np.unique(labels)

    # Create DataFrame to store cluster centroids
    cluster_centroids = pd.DataFrame(index=channel_names, columns=unique_labels)
    
    # Compute mean values for each cluster
    for label in unique_labels:
        cluster_centroids[label] = matrix[labels == label, :].mean(axis=0)

    # Save the cluster centroids to a CSV file
    cluster_centroids.to_csv(f'{plot_dir}/cluster_centroids_df.csv', index=True)
    return cluster_centroids

def plot_cluster_matrix_as_heatmap(cluster_centroids_df_path, plot_dir, n_clusters, filtered_channel_names=None):
    
    if os.path.exists(f'{plot_dir}/all_biomarkers_heatmap.png'):  #if clustering already exists, skip
        print('all_biomarkers_heatmap already exists, skipping')
        return
    
    cluster_centroids_df = pd.read_csv(cluster_centroids_df_path, index_col=0)
    if n_clusters >= 35:
        plt.figure(figsize=(30, 10))
    else:
        plt.figure(figsize=(20, 10))
    #plt.figure(figsize=(35, 15))
    sns.heatmap(cluster_centroids_df, annot=True, fmt=".2f", cmap='coolwarm', cbar=True)
    plt.title(f'All Biomakers - Mean Expression Across {n_clusters} Clusters')
    plt.xlabel('Clusters')
    plt.ylabel('Channel Names')
    plt.tight_layout()
    plt.savefig(f'{plot_dir}/all_biomarkers_heatmap.png')
    print(f"expression per cluster fig saved ")
    plt.clf()

    # Filtered heatmap
    if filtered_channel_names is not None:
        filtered_df = cluster_centroids_df.loc[filtered_channel_names]
        if n_clusters >= 35:
            plt.figure(figsize=(30, 6))
        else:
            plt.figure(figsize=(20, 10))
        sns.heatmap(filtered_df, annot=True, fmt=".2f", cmap='coolwarm', cbar=True)
        plt.title(f'Cell Lineage Biomarkers - Mean Expression Across {n_clusters} Clusters')
        plt.xlabel('Clusters')
        plt.ylabel('Channel Names')
        plt.tight_layout()
        plt.savefig(f'{plot_dir}/lineage_biomarkers_heatmap.png')
        print(f"expression per cluster fig saved for filtered biomarkers")
        plt.clf()

def plot_heatmap_for_poster(mean_df_path, save_path):
    mean_df = pd.read_csv(mean_df_path)
    mean_df = mean_df.set_index(mean_df.columns[0])
    mean_df = mean_df.rename_axis('Channels')
    
    channels = ['E-cadherin', 'Pan-Cytokeratin', 'Ki67', 'ER', 'PR', 'CD3e', 'CD8', 'CD4', 'CD20', 'HLA-ABC', 'CD163', 'CD68', 'PD-L1', 'MPO', 'CD31']
    filtered_df = mean_df.loc[channels]

    plt.figure(figsize=(20, 10))
    sns.heatmap(filtered_df, annot=True, fmt=".2f", cmap='coolwarm', cbar=True)
    plt.title(f'Channel Expression Means of KMeans Clusters')
    plt.xlabel('Clusters')
    plt.ylabel('Channel Names')
    plt.tight_layout()
    plt.savefig(f'{save_path}/filtered_cluster_heatmap.png')
    print(f"expression per cluster fig saved for clusters")
    plt.clf()

if __name__ == '__main__':
    main()