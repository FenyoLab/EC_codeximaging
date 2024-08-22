import sys
import os
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import pdb

def proportion_per_cluster(sample_names_path, labels_path, plot_dir, n_clusters, slides = None):

    sample_names = np.load(sample_names_path)
    unique_samples = np.unique(sample_names)
    
    labels = np.load(labels_path) 
    unique_labels = np.unique(labels) 

    proportion_matrix = np.zeros((len(unique_samples), len(unique_labels))) 

    for i, sample in enumerate(unique_samples):
        sample_indices = np.where(sample_names == sample)[0] 
        
        for j, label in enumerate(unique_labels):
            label_count = np.count_nonzero(labels[sample_indices] == label) 
            proportion_matrix[i, j] = label_count / len(sample_indices) 
    
    if n_clusters >= 35:
        plt.figure(figsize=(25, 10))
    else:
        plt.figure(figsize=(20, 10))
    sns.heatmap(proportion_matrix, cmap='Blues', annot=False, fmt=".2f", cbar_kws={'label': 'Proportion'}, vmin = 0, vmax = 1)
    plt.xlabel('Cluster', fontsize=18)
    plt.ylabel('Sample', fontsize=18)
    plt.xticks(ticks=np.arange(len(unique_labels)) + 0.5, labels=np.arange(1, len(unique_labels) + 1))
    plt.yticks(ticks=[i + 0.5 for i in range(len(slides))], labels=slides)
    plt.title('Proportion of Samples in Each Cluster')
    plt.tight_layout()
    plt.savefig(f'{plot_dir}/sample_per_cluster.png')
    print(f'sample per cluster fig saved for {n_clusters} clusters')
    plt.clf()

if __name__ == '__main__':
    main()