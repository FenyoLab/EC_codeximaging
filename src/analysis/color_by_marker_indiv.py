import sys
import os
import numpy as np
import matplotlib.pyplot as plt
import sys
from matplotlib.colors import LinearSegmentedColormap

def pca_by_marker_indiv(pca_path, marker_path, plot_dir, channel_names=None):
    pca_embedding = np.load(pca_path)
    markers = np.load(marker_path)

    for i, marker in enumerate(channel_names):
        if marker != 'MPO':
            continue 
        print(marker)
        marker_color = markers[:, i]
        
        m_min, m_max = np.percentile(marker_color, [1, 99])
        marker_color = np.clip(marker_color, m_min, m_max)
        marker_color = (marker_color - m_min) / (m_max - m_min + 1e-6)

        fig, ax = plt.subplots(figsize=(5, 4))
        sc = ax.scatter(pca_embedding[:, 0], pca_embedding[:, 1], s=0.1, c=marker_color, cmap='bwr')
        ax.set_title(f'Marker: {marker}', fontsize=16)
        ax.set_xticks([])
        ax.set_yticks([])
        fig.colorbar(sc, ax=ax)

        plot_file_path = f'{plot_dir}/pca_marker{marker}.png'
        plt.savefig(plot_file_path, bbox_inches='tight')
        plt.close()

def umap_by_marker_indiv(umap_path, marker_path, plot_dir, channel_names=None):
    umap_embedding = np.load(umap_path)
    markers = np.load(marker_path)

    for i, marker in enumerate(channel_names):
        if marker != 'MPO':
            continue 
        print(marker)
        marker_color = markers[:, i]
        
        m_min, m_max = np.percentile(marker_color, [5, 95])
        marker_color = np.clip(marker_color, m_min, m_max)
        marker_color = (marker_color - m_min) / (m_max - m_min + 1e-6)

        fig, ax = plt.subplots(figsize=(5, 4))
        sc = ax.scatter(umap_embedding[:, 0], umap_embedding[:, 1], s=0.1, c=marker_color, cmap='bwr')
        ax.set_title(f'Marker: {marker}', fontsize=16)
        ax.set_xticks([])
        ax.set_yticks([])
        fig.colorbar(sc, ax=ax)

        plot_file_path = f'{plot_dir}/umap_marker{marker}.png'
        plt.savefig(plot_file_path, bbox_inches='tight')
        plt.close()

if __name__ == '__main__':
    main()
