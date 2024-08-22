import sys
import os
import numpy as np
import umap
import matplotlib.pyplot as plt

def plot_umap(emb_path, umap_emb_path, save_path, output_suffix = 'umap'):

    output_path = f'{save_path}/{output_suffix}' #create output directory 
    os.makedirs(output_path, exist_ok = True)
    if os.path.exists(umap_emb_path):  #if UMAP already exists, skip
        print('UMAP already exists, skipping')
        return

    embedding = np.load(emb_path)
    print(f'Embedding shape: {embedding.shape}')

    print('Generating umap')
    umap_embedding = umap.UMAP(random_state=2021, init = 'spectral').fit_transform(embedding)
    np.save(umap_emb_path, umap_embedding)

    plt.figure()
    plt.scatter(umap_embedding[:, 0], umap_embedding[:, 1], s = 0.1)
    plt.savefig(umap_emb_path.replace('.npy', '.png'))
    plt.close()

if __name__ == '__main__':
    main()
