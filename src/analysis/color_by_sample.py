import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import pdb

def pca_by_sample(pca_path, sample_names_path, plot_dir, n_clusters, cols = 4):

    if os.path.exists(f'{plot_dir}/pca_by_sample.png'):  #if clustering already exists, skip
        print('pca_by_sample plot already exists, skipping')
        return

    os.makedirs(plot_dir, exist_ok = True)

    pca_embedding = np.load(pca_path)
    sample_ids = np.load(sample_names_path)

    unique_samples = np.unique(sample_ids)
    print(unique_samples)
    print(f'Loaded {len(sample_ids)} samples, {len(unique_samples)} unique samples')

    rows = (len(unique_samples) - 1) // cols + 1
    fig, axes = plt.subplots(rows, cols, figsize=(cols * 5, rows * 4))

    if rows == 1 or cols == 1:
        axes = np.array([axes])
    
    for sample_i in range(len(unique_samples)):
        sample_name = unique_samples[sample_i]

        x = sample_i // cols
        y = sample_i % cols
        #sample_color = np.array([94, 47, 235, 255]) / 255
        sample_color = mcolors.to_rgba('tab:red')
        sample_indices = (sample_ids == sample_name)
    
        axes[x, y].scatter(pca_embedding[:, 0], pca_embedding[:, 1], s = 0.1, c = 'lightgray', marker = 'o', label = 'all')
        axes[x, y].scatter(pca_embedding[sample_indices, 0], pca_embedding[sample_indices, 1], s = 0.1, c = sample_color, marker = 'o', label = sample_name)

        axes[x, y].set_title(f'{sample_name} (n = {np.sum(sample_indices)})')
        axes[x, y].set_xticks([])
        axes[x, y].set_yticks([])
        axes[x, y].legend()

    # Clean up empty axes
    for i in range(len(unique_samples), rows * cols):
        axes[i // cols, i % cols].axis('off')

    for ax in axes.flat:
        ax.label_outer()

    plot_file_path = f'{plot_dir}/pca_by_sample.png'
    plt.savefig(plot_file_path, bbox_inches='tight')
    plt.clf()

def umap_by_sample(umap_path, sample_names_path, indices_one_percent_path, plot_dir, n_clusters, cols = 4):

    if os.path.exists(f'{plot_dir}/umap_by_sample.png'):  #if clustering already exists, skip
        print('umap_by_sample plot already exists, skipping')
        return

    os.makedirs(plot_dir, exist_ok = True)

    umap_embedding = np.load(umap_path)
    sample_ids = np.load(sample_names_path)
    indices_one_percent = np.load(indices_one_percent_path)

    sample_ids_subset = sample_names_path[indices_one_percent]

    unique_samples = np.unique(sample_ids_subset)
    print(unique_samples)
    print(f'Loaded {len(sample_ids_subset)} samples, {len(unique_samples)} unique samples')

    rows = (len(unique_samples) - 1) // cols + 1
    fig, axes = plt.subplots(rows, cols, figsize=(cols * 5, rows * 4))

    if rows == 1 or cols == 1:
        axes = np.array([axes])
    
    for sample_i in range(len(unique_samples)):
        sample_name = unique_samples[sample_i]

        x = sample_i // cols
        y = sample_i % cols
        #sample_color = np.array([94, 47, 235, 255]) / 255
        sample_color = mcolors.to_rgba('tab:red')
        sample_indices = (sample_ids_subset == sample_name)
    
        axes[x, y].scatter(umap_embedding[:, 0], umap_embedding[:, 1], s = 0.1, c = 'lightgray', label = 'all')
        axes[x, y].scatter(umap_embedding[sample_indices, 0], umap_embedding[sample_indices, 1], s = 0.1, c = sample_color, label = sample_name)

        axes[x, y].set_title(f'{sample_name} (n = {np.sum(sample_indices)})')
        axes[x, y].set_xticks([])
        axes[x, y].set_yticks([])
        axes[x, y].legend()

    # Clean up empty axes
    for i in range(len(unique_samples), rows * cols):
        axes[i // cols, i % cols].axis('off')

    for ax in axes.flat:
        ax.label_outer()

    plot_file_path = f'{plot_dir}/umap_by_sample.png'
    plt.savefig(plot_file_path, bbox_inches='tight')
    plt.clf()

if __name__ == '__main__':
    main()