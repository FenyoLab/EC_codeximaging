import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import pdb

import sklearn.cluster as cluster

def clustering(emb_path, umap_path, n_clusters, save_path, output_suffix = 'clustering'):

    output_path = f'{save_path}/{output_suffix}/{n_clusters}_clusters' #create output directory 
    os.makedirs(output_path, exist_ok = True)
    
    labels_path = os.path.join(output_path, 'kmeans_labels.npy')
    if os.path.exists(labels_path):  #if clustering already exists, skip
        print('Kmeans labels already exist, skipping')
        return

    embedding = np.load(emb_path)
    print('Embedding loaded')
    kmeans = cluster.KMeans(n_clusters=n_clusters, random_state=0).fit(embedding)
    kmeans_labels = kmeans.labels_ + 1
    kmeans_inertia = kmeans.inertia_
    np.save(labels_path, kmeans_labels)
    print('Kmeans saved')
    with open(labels_path.split('.')[0] + '_inertia.txt', 'w') as f:
        f.write(str(kmeans_inertia))
    print('Kmeans inertia saved')

    print('Plotting clusters on UMAP')
    umap_embedding = np.load(umap_path)
    fig, ax = plt.subplots(figsize = (10, 10))
    if n_clusters <= 20:
        palette = 'tab20'
    else:
        palette = 'Spectral'
    sns.scatterplot(x = umap_embedding[:, 0], y = umap_embedding[:, 1], size = 0.1, hue=kmeans_labels, palette = palette, legend='full')
    plt.title(f'Kmeans {n_clusters} clusters')
    plt.legend(bbox_to_anchor=(1.1, 1.05))
    plt.savefig(labels_path.replace('.npy', '.png'))
    plt.clf()

def add_labels_to_metadata(labels_path, raw_metadata_path, filtered_metadata_path, save_path, n_clusters, output_suffix = 'clustering'):

    output_path = f'{save_path}/{output_suffix}/{n_clusters}_clusters'
    metadata_with_clusters_path = os.path.join(output_path, 'metadata_with_cluster_labels.csv')
    if os.path.exists(metadata_with_clusters_path):  #if clustering already exists, skip
        print('Cluster labels already added to metadata, skipping')
        return
    
    cluster_labels = np.load(labels_path)
    raw_metadata = pd.read_csv(raw_metadata_path, index_col = 0)
    filtered_metadata = pd.read_csv(filtered_metadata_path, index_col = 0)

    print("Raw metadata shape before clusters added: ", raw_metadata.shape)

    # Create a mapping of filtered indices to cluster labels
    index_to_cluster = pd.Series(cluster_labels, index=filtered_metadata.index).to_dict()
    # Add the cluster label column to raw_metadata with default value 0
    raw_metadata['cluster_label'] = raw_metadata.index.map(index_to_cluster).fillna(0).astype(int)

    print("Raw metadata shape after clusters added: ", raw_metadata.shape)
    raw_metadata.to_csv(metadata_with_clusters_path, index = True)

def assign_cellphenotype(clustering_results_dir, n_clusters, cluster_labels):
    metadata_with_cluster_labels_path = os.path.join(clustering_results_dir, 'clustering', f'{n_clusters}_clusters', 'metadata_with_cluster_labels.csv')
    metadata_with_cluster_labels = pd.read_csv(metadata_with_cluster_labels_path)

    #add a column to the metadata file assigning cluster labels cell types
    #map(): The map() function in pandas is used to map values from a dictionary to a DataFrame column.
    metadata_with_cluster_labels['cell_type'] = metadata_with_cluster_labels['cluster_label'].map(cluster_labels)
    metadata_with_cluster_labels.to_csv(metadata_with_cluster_labels_path, index=False)


    
    