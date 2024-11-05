import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import pdb

import sklearn.cluster as cluster

def clustering(emb_path, pca_path, n_clusters, save_path, random_state, output_suffix = 'clustering'):

    output_path = f'{save_path}/{output_suffix}/{n_clusters}_clusters' #create output directory 
    os.makedirs(output_path, exist_ok = True)
    
    labels_path = os.path.join(output_path, 'kmeans_labels.npy')
    if os.path.exists(labels_path):  #if clustering already exists, skip
        print('Kmeans labels already exist, skipping')
        return

    embedding = np.load(emb_path)
    print('Embedding loaded')
    kmeans = cluster.KMeans(n_clusters=n_clusters, random_state = random_state).fit(embedding)
    kmeans_labels = kmeans.labels_ + 1
    kmeans_inertia = kmeans.inertia_
    np.save(labels_path, kmeans_labels)
    print('Kmeans saved')
    with open(labels_path.split('.')[0] + '_inertia.txt', 'w') as f:
        f.write(str(kmeans_inertia))
    print('Kmeans inertia saved')

    print('Plotting clusters on PCA plot')
    pca_embedding = np.load(pca_path)
    fig, ax = plt.subplots(figsize = (10, 10))
    if n_clusters <= 20:
        palette = 'tab20'
    else:
        palette = 'Spectral'
    sns.scatterplot(x = pca_embedding[:, 0], y = pca_embedding[:, 1], size = 0.1, hue=kmeans_labels, marker = 'o', palette = palette, legend='full')
    plt.title(f'Kmeans {n_clusters} clusters')
    plt.legend(bbox_to_anchor=(1.1, 1.05))
    plt.savefig(labels_path.replace('.npy', '.png'))
    plt.clf()

def add_labels_to_metadata(labels_path, raw_metadata_path, filtered_metadata_path, save_path, n_clusters, output_suffix = 'clustering'):

    output_path = f'{save_path}/{output_suffix}/{n_clusters}_clusters'
    phenotype_clusters_df_path = os.path.join(output_path, 'phenotype_clusters.csv')
    if os.path.exists(phenotype_clusters_df_path):  #if clustering already exists, skip
        print('Cluster labels already added to metadata, skipping')
        return
    
    cluster_labels = np.load(labels_path)
    raw_metadata = pd.read_csv(raw_metadata_path, index_col = 0)
    filtered_metadata = pd.read_csv(filtered_metadata_path, index_col = 0)

    assert cluster_labels.shape[0] == filtered_metadata.shape[0], "Number of cells for kmeans and filtered metadata do not match!"

    phenotype_clusters_df = raw_metadata[['slide_id']].copy()
    phenotype_clusters_df.loc[:, 'cluster_label'] = 0
    phenotype_clusters_df.loc[filtered_metadata.index, 'cluster_label'] = cluster_labels
    phenotype_clusters_df.index = phenotype_clusters_df.index + 1

    assert raw_metadata.shape[0] == phenotype_clusters_df.shape[0], "Number of cells for raw metadata and phenotype clusters do not match!"

    phenotype_clusters_df.to_csv(phenotype_clusters_df_path, index = True)
    print('Cluster labels added to metadata and saved')

    
    