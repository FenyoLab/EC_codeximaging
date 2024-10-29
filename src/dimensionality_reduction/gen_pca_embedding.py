import os
import sys 
import numpy as np
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import seaborn as sns

def plot_pca(emb_path, pca_emb_path, save_path, random_state, output_suffix = 'pca'):

    output_path = f'{save_path}/{output_suffix}' #create output directory 
    os.makedirs(output_path, exist_ok = True)

    if os.path.exists(pca_emb_path): 
        print('PCA already exists, skipping')
        return
    
    embedding = np.load(emb_path)
    print(f'Embedding shape: {embedding.shape}')

    print('Generating PCA')
    pca_embedding = PCA(n_components=2, random_state = random_state).fit_transform(embedding)
    np.save(pca_emb_path, pca_embedding)

    plt.figure()
    plt.scatter(pca_embedding[:, 0], pca_embedding[:, 1], s = 0.1, marker = 'o')
    plt.savefig(pca_emb_path.replace('.npy', '.png'))
    plt.close()