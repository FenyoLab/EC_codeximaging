import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

import sklearn.cluster as cluster

def clustering(emb_path, umap_path, n_clusters, save_path, output_suffix = 'clustering'):

    output_path = f'{save_path}/{output_suffix}' #create output directory 
    os.makedirs(output_path, exist_ok = True)
    
    labels_path = os.path.join(output_path, 'kmeans_labels.npy')
    if os.path.exists(labels_path):  #if clustering already exists, skip
        print('UMAP already exists, skipping')
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

def add_labels_to_metadata(labels_path, metadata_path, save_path, output_suffix = 'clustering'):

    output_path = f'{save_path}/{output_suffix}'
    metadata_with_clusters_path = os.path.join(output_path, 'metadata_with_cluster_labels.csv')
    if os.path.exists(metadata_with_clusters_path):  #if clustering already exists, skip
        print('Cluster labels already added to metadata, skipping')
        return
    
    cluster_labels = np.load(labels_path)
    metadata = pd.read_csv(metadata_path)
    print("Metadata shape before clusters added: ", metadata.shape)

    metadata['cluster_labels'] = cluster_labels
    print("Metadata shape after clusters added: ", metadata.shape)

    metadata.to_csv(metadata_with_clusters_path, index = False)
    print('Cluster labels added to metadata')

if __name__ == '__main__':
    main()
