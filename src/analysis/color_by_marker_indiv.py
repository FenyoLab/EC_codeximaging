import sys
import os
import numpy as np
import matplotlib.pyplot as plt
import sys
from matplotlib.colors import LinearSegmentedColormap
from color_by_marker import find_first_positive_percentile 

def pca_by_marker_indiv(pca_path, marker_path, matrix_path, plot_dir, channel_names=None):
    pca_embedding = np.load(pca_path)
    markers = np.load(marker_path)
    matrix = np.load(matrix_path)
    
    channels_of_interest = ['CD4', 'CD20', 'CD163', 'CD68', 'CD8', 'CD3e']
    percentile_dict = find_first_positive_percentile(matrix_path, channels_of_interest, channel_names, plot_dir)

    for i, marker in enumerate(channel_names):
        if marker != 'CD8':
            continue 
        print(marker)
        marker_color = markers[:, i]

        if marker in percentile_dict:
            print(f'upper percentile: {percentile_dict[marker]}')
            m_min, m_max = np.percentile(marker_color, [5, percentile_dict[marker]])
        else:
            m_min, m_max = np.percentile(marker_color, [5, 97])

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

save_path = '/gpfs/data/proteomics/projects/Endometrial_mIF/EC_codeximaging_results/out_12-2-24'
pca_coord_path = os.path.join(save_path, 'pca/coord.npy')
marker_path = os.path.join(save_path, 'normalized_matrix/matrix_normal.npy')
matrix_path = os.path.join(save_path, 'thresholded_matrix/matrix.npy')
plot_dir = os.path.join(save_path, 'analysis_figures')
channel_names = ['DAPI', 'MPO', 'Ecadherin', 'PDL1', 'CD163', 'PD1', 'CD47', 'GAL3', 'PARP1', 'LAG3', 'CD4', 'PI3KCA', 'TIM3', 'CD68', 'ER', 'PR', 'MSH2', 'CD8', 'MSH6', 'bCatenin1', 'HLAABC', 'MLH1', 'Ki67', 'CD20', 'ARID1A', 'IFNG', 'CD31', 'PMS', 'CD44', 'PanCytokeratin', 'CD3e']

pca_by_marker_indiv(pca_coord_path, marker_path, matrix_path, plot_dir, channel_names)

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

#if __name__ == '__main__':
#    main()
