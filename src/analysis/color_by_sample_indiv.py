import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

def umap_by_sample_indiv(umap_path, sample_ids_path, plot_dir):
    # Load the data
    umap_embedding = np.load(umap_path)
    sample_ids = np.load(sample_ids_path)

    unique_samples = np.unique(sample_ids)
    #print(unique_samples)
    print(f'Loaded {len(sample_ids)} samples, {len(unique_samples)} unique samples')

    # Ensure the output directory exists
    os.makedirs(plot_dir, exist_ok=True)

    # Loop through each unique sample
    for sample_i, sample_name in enumerate(unique_samples):
        if sample_name != '20230922-3869-1O_Scan1':
            continue
        print(sample_name)
        sample_color = mcolors.to_rgba('tab:red')
        sample_indices = sample_ids == sample_name

        # Create a new plot for each sample
        plt.figure(figsize=(5, 4))
        plt.scatter(umap_embedding[:, 0], umap_embedding[:, 1], s=0.1, c='lightgray', label='all')
        plt.scatter(umap_embedding[sample_indices, 0], umap_embedding[sample_indices, 1], s=0.1, c=sample_color, label=sample_name)
        #plt.title(f'{sample_name} (n = {np.sum(sample_indices)})')
        plt.title(f'Sample: {sample_name}', fontsize = 14)
        plt.xticks([])
        plt.yticks([])
        #plt.legend()

        # Save the plot
        
        plot_file_path = f'{plot_dir}/umap_{sample_name}.png'
        plt.savefig(plot_file_path, bbox_inches='tight')
        plt.clf()
