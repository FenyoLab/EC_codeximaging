import os
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans

def get_data_subset(cell_sample_names, matrix):
    """
    Extracts 10% of rows for each unique sample from the matrix.
    Parameters:
        cell_sample_names (numpy array): Array of sample names corresponding to rows in the matrix.
        matrix (numpy array): 2D array (matrix) where rows correspond to samples.
    Returns:
        numpy array: Subset of the matrix with 10% of rows from each sample.
    """
    subset_indices = []

    # Iterate through unique samples
    for sample in np.unique(cell_sample_names):
        print(f'Processing sample: {sample}')
        sample_indices = np.where(cell_sample_names == sample)[0] # Get indices of the current sample
        print(f'Number of cells in sample: {len(sample_indices)}')
        num_sampled_rows = max(1, int(len(sample_indices) * 0.1))  # Calculate the number of rows to sample (10% of rows)
        sampled_indices = np.random.choice(sample_indices, size=num_sampled_rows, replace=False) # Randomly select 10% of indices
        print(f'Number of cells sampled: {len(sampled_indices)}')
        subset_indices.extend(sampled_indices) # Add sampled indices to the list

    subset_matrix = matrix[subset_indices, :] # Extract the rows corresponding to the sampled indices
    return subset_matrix

def create_elbow_plot(matrix, save_path):
    cluster_range = range(5, 55, 5)
    wcss = []

    for k in cluster_range:
        kmeans = KMeans(n_clusters=k, random_state=2024)
        kmeans.fit(matrix)
        wcss.append(kmeans.inertia_)
    
    plt.figure(figsize=(8, 6))
    plt.plot(cluster_range, wcss, marker='o', linestyle='-', color='b')
    plt.title('Elbow Plot for Cell Phenotype Clustering')
    plt.xlabel('Number of Clusters')
    plt.ylabel('Within-Cluster Sum of Squares (WCSS)')
    plt.xticks(cluster_range)
    plt.grid()
    plt.tight_layout()

    plt.savefig(f'{save_path}/subset_elbow_plot.png')
    plt.close()