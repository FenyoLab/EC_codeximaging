import sys
import os
import numpy as np
import matplotlib.pyplot as plt
import sys
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap

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
        
        m_min, m_max = np.percentile(marker_color, [5, 95])
        marker_color = np.clip(marker_color, m_min, m_max)
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

