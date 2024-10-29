import sys
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def pca_by_cluster(pca_path, labels_path, plot_dir, n_clusters, cols = 5):
   
    if os.path.exists(f'{plot_dir}/color_by_cluster.png'):  #if clustering already exists, skip
        print('color_by_cluster plot already exists, skipping')
        return
    
    print("generating color_by_cluster plot")

    pca_embedding = np.load(pca_path)
    print(pca_embedding.shape)
    cluster_labels = np.load(labels_path)
    unique_labels = np.unique(cluster_labels)
    print(unique_labels)

    rows = n_clusters // cols 
    fig, axes = plt.subplots(rows, cols, figsize=(cols * 5, rows * 4))

    for label in unique_labels:
        label_indices = cluster_labels == label

        x = (label - 1) // cols
        y = (label - 1) % cols

        sample_color = 'blue'

        axes[x, y].scatter(pca_embedding[:, 0],
                           pca_embedding[:, 1], s = 0.1, c = 'lightgray', label = 'all')
        axes[x, y].scatter(pca_embedding[label_indices, 0],
                           pca_embedding[label_indices, 1], s = 0.1, c = sample_color, label = str(label))

        axes[x, y].set_title(f'Cluster {label} (n = {np.sum(label_indices)})')
        axes[x, y].set_xticks([])
        axes[x, y].set_yticks([])
        axes[x, y].legend()

    for i in range(len(unique_labels), rows * cols):
        axes[i // cols, i % cols].axis('off')

    for ax in axes.flat:
        ax.label_outer()
    plt.savefig(f'{plot_dir}/color_by_cluster.png', bbox_inches='tight')
    print(f"color by cluster fig saved for {n_clusters} clusters")
    plt.clf()

def umap_by_cluster(umap_path, labels_path, indices_one_percent_path, plot_dir, n_clusters, cols = 5):
   
    if os.path.exists(f'{plot_dir}/color_by_cluster.png'):  #if clustering already exists, skip
        print('color_by_cluster plot already exists, skipping')
        return
    
    print("generating color_by_cluster plot")

    umap_embedding = np.load(umap_path)
    print(umap_embedding.shape)
    cluster_labels = np.load(labels_path)
    indices_one_percent = np.load(indices_one_percent_path)

    cluster_labels_subset = cluster_labels[indices_one_percent_path]

    unique_labels = np.unique(cluster_labels_subset)
    print(unique_labels)

    rows = n_clusters // cols 
    fig, axes = plt.subplots(rows, cols, figsize=(cols * 5, rows * 4))

    for label in unique_labels:
        label_indices = cluster_labels_subset == label

        x = (label - 1) // cols
        y = (label - 1) % cols

        sample_color = 'blue'

        axes[x, y].scatter(umap_embedding[:, 0],
                           umap_embedding[:, 1], s = 0.1, c = 'lightgray', marker = 'o', label = 'all')
        axes[x, y].scatter(umap_embedding[label_indices, 0],
                           umap_embedding[label_indices, 1], s = 0.1, c = sample_color, marker = 'o', label = str(label))

        axes[x, y].set_title(f'Cluster {label} (n = {np.sum(label_indices)})')
        axes[x, y].set_xticks([])
        axes[x, y].set_yticks([])
        axes[x, y].legend()

    for i in range(len(unique_labels), rows * cols):
        axes[i // cols, i % cols].axis('off')

    for ax in axes.flat:
        ax.label_outer()
    plt.savefig(f'{plot_dir}/color_by_cluster.png', bbox_inches='tight')
    print(f"color by cluster fig saved for {n_clusters} clusters")
    plt.clf()

if __name__ == '__main__':
    main()