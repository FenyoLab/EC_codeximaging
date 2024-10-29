import sys
import os
import numpy as np
import umap.umap_ as umap
import matplotlib.pyplot as plt

def plot_umap(emb_path, umap_emb_path, save_path, random_state, output_suffix = 'umap'):

    output_path = f'{save_path}/{output_suffix}' #create output directory 
    os.makedirs(output_path, exist_ok = True)

    if os.path.exists(umap_emb_path):  #if UMAP already exists, skip
        print('UMAP already exists, skipping')
        return

    embedding = np.load(emb_path)
    print(f'Embedding shape: {embedding.shape}')

    print('Generating umap')
    umap_embedding = umap.UMAP(random_state= random_state, init = 'spectral').fit_transform(embedding)
    np.save(umap_emb_path, umap_embedding)

    plt.figure()
    plt.scatter(umap_embedding[:, 0], umap_embedding[:, 1], s = 0.1)
    plt.savefig(umap_emb_path.replace('.npy', '.png'))
    plt.close()

if __name__ == '__main__':
    main()

def subset_one_percent(normal_data_dir, save_path, output_suffix = 'umap'):

    output_path = f'{save_path}/{output_suffix}' #create output directory 
    os.makedirs(output_path, exist_ok = True)
    
    matrix = np.load(os.path.join(normal_data_dir, 'matrix_normal_filtered_markers.npy'))
    sample_names = np.load(os.path.join(normal_data_dir, 'cell_sample_names_filtered.npy'))
    print("Full matrix shape:", matrix.shape)

    selected_indices = []

    for sample in np.unique(sample_names):
        # Get the indices of rows corresponding to the current sample
        sample_indices = np.where(sample_names == sample)[0]
        
        # Calculate the number of rows to select (1%)
        n_select = max(1, int(0.01 * len(sample_indices)))  # Ensure at least one row is selected

        # Randomly select 1% of the rows from the sample
        selected_sample_indices = np.random.choice(sample_indices, n_select, replace=False)
        selected_sample_indices = sorted(selected_sample_indices)
        
        # Add selected indices to the final list
        selected_indices.extend(selected_sample_indices)

    # Save the selected indices to a file
    matrix_subset = matrix[selected_indices]
    print("1 percent of matrix shape:", matrix_subset.shape)
    print("Length of selected indices:", len(selected_indices))
    np.save(os.path.join(output_path, 'matrix_one_percent.npy'), matrix_subset)
    np.save(os.path.join(output_path, 'indices_one_percent.npy'), np.array(selected_indices))