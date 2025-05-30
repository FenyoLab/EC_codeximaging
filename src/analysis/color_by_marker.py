import sys
import os
import json
import numpy as np
import matplotlib.pyplot as plt
import sys
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap

def main():
    save_path = '/gpfs/data/proteomics/projects/Endometrial_mIF/EC_codeximaging_results/out_12-2-24'
    pca_path = os.path.join(save_path, 'pca/coord.npy')
    marker_path = os.path.join(save_path, 'normalized_matrix/matrix_normal.npy')
    matrix_path = os.path.join(save_path, 'thresholded_matrix/matrix.npy')
    plot_dir = os.path.join(save_path, 'analysis_figures')
    channel_names = ['DAPI', 'MPO', 'Ecadherin', 'PDL1', 'CD163', 'PD1', 'CD47', 'GAL3', 'PARP1', 'LAG3', 'CD4', 'PI3KCA', 'TIM3', 'CD68', 'ER', 'PR', 'MSH2', 'CD8', 'MSH6', 'bCatenin1', 'HLAABC', 'MLH1', 'Ki67', 'CD20', 'ARID1A', 'IFNG', 'CD31', 'PMS', 'CD44', 'PanCytokeratin', 'CD3e']

    pca_by_marker(pca_path, marker_path, matrix_path, plot_dir, channel_names)


def pca_by_marker(pca_path, marker_path, matrix_path, plot_dir, channel_names = None, cols = 5):

    if os.path.exists(f'{plot_dir}/pca_by_marker.png'):  #if clustering already exists, skip
        print('pca_by_marker plot already exists, skipping')
        return

    pca_embedding = np.load(pca_path)
    print(pca_embedding.shape)
    markers = np.load(marker_path)
    print(markers.shape)
    
    rows = len(channel_names) // cols + 1
    #fig, axes = subplots(rows, cols, figsize=(cols * 50, rows * 40), font_size = 5)
    fig, axes = plt.subplots(rows, cols, figsize=(cols * 5, rows * 4))

    channels_of_interest = ['CD4', 'CD20', 'CD163', 'CD68', 'CD8', 'CD3e'] 
    percentile_dict = find_first_positive_percentile(matrix_path, channels_of_interest, channel_names, plot_dir)

    for marker_i, channel in enumerate(channel_names):
        marker_color = markers[:, marker_i]
        print(channel)

        if channel == 'CD163':
            print(f'upper percentile: {percentile_dict[channel]}')
            percentiles = [5, percentile_dict[channel]]
        elif channel == 'CD4':
            print(f'upper percentile: {percentile_dict[channel]}')
            percentiles = [5, 95]
        elif channel == 'CD68':
            print(f'upper percentile: {percentile_dict[channel]}')
            percentiles = [5, 95]
        elif channel == 'CD20':
            print(f'upper percentile: {percentile_dict[channel]}')
            percentiles = [5, 95]
        elif channel == 'CD8':
            print(f'upper percentile: {percentile_dict[channel]}')
            percentiles = [5, percentile_dict[channel]]
        else:
            percentiles = [5, 97]
        m_min, m_max = np.percentile(marker_color, percentiles)
        print(m_min, m_max)

        marker_color = np.clip(marker_color, m_min, m_max)
        marker_color = (marker_color - m_min) / (m_max - m_min + 1e-6)

        sc = axes[marker_i // cols, marker_i % cols].scatter(pca_embedding[:, 0], pca_embedding[:, 1], s = 0.1, c = marker_color, marker = 'o', cmap = 'bwr')
        axes[marker_i // cols, marker_i % cols].set_title(f'Marker: {channel}', fontsize=20)
        fig.colorbar(sc, ax=axes[marker_i // cols, marker_i % cols])

    # Clean up empty axes
    for i in range(len(channel_names), rows * cols):
        axes[i // cols, i % cols].axis('off')

    for ax in axes.flat:
        ax.label_outer()
    
    plot_file_path = f'{plot_dir}/pca_by_marker.png'
    plt.savefig(plot_file_path, bbox_inches='tight')
    plt.close()

def find_first_positive_percentile(matrix_path, channels_of_interest, channel_names, save_path):
    matrix = np.load(matrix_path)
    print(matrix.shape)

    percentile_dict = {}

    for channel in channels_of_interest:
        channel_index = channel_names.index(channel)
        print(f"Channel: {channel}, index: {channel_index}")

        channel_arr = matrix[:, channel_index]
        sorted_channel_arr = np.sort(channel_arr)
        cumulative_dist = np.cumsum(sorted_channel_arr) / np.sum(sorted_channel_arr)
        first_positive_index = np.searchsorted(sorted_channel_arr, 1, side='right')
        percentile_of_first_positive = (first_positive_index / len(channel_arr)) * 100

        percentile_dict[channel] = percentile_of_first_positive
    
    print(percentile_dict)
    #save percentile dict
    with open(os.path.join(save_path, 'pos_percentile_channel.json'), 'w') as json_file:
        json.dump(percentile_dict, json_file, indent=4)

    return percentile_dict

def umap_by_marker(umap_path, marker_path, plot_dir, channel_names = None, cols = 5):
    
    if os.path.exists(f'{plot_dir}/umap_by_marker.png'):  #if clustering already exists, skip
        print('umap_by_marker plot already exists, skipping')
        return
    
    umap_embedding = np.load(umap_path)
    markers = np.load(marker_path)
    
    rows = len(channel_names) // cols + 1
    #fig, axes = subplots(rows, cols, figsize=(cols * 50, rows * 40), font_size = 5)
    fig, axes = plt.subplots(rows, cols, figsize=(cols * 5, rows * 4))


    for marker_i in range(len(channel_names)):
        marker_color = markers[:, marker_i]
        print(channel_names[marker_i])
        
        m_min, m_max = np.percentile(marker_color, [1, 99])
        marker_color = np.clip(marker_color, m_min, m_max)
        #m_min = np.min(marker_color)
        #m_max = np.max(marker_color)
        print(m_min, m_max)
        marker_color = (marker_color - m_min) / (m_max - m_min + 1e-6)

        sc = axes[marker_i // cols, marker_i % cols].scatter(umap_embedding[:, 0], umap_embedding[:, 1], s = 0.1, c = marker_color, cmap = 'bwr')
        axes[marker_i // cols, marker_i % cols].set_title(f'Marker: {channel_names[marker_i]}').set_size(20)
        fig.colorbar(sc, ax=axes[marker_i // cols, marker_i % cols])

    # Clean up empty axes
    for i in range(len(channel_names), rows * cols):
        axes[i // cols, i % cols].axis('off')

    for ax in axes.flat:
        ax.label_outer()
    
    plot_file_path = f'{plot_dir}/umap_by_marker.png'
    plt.savefig(plot_file_path, bbox_inches='tight')
    plt.clf()

if __name__ == '__main__':
    main()

