import numpy as np
import argparse
import matplotlib.pyplot as plt
import pandas as pd
from collections import Counter
import os

def get_args_parser():
    parser = argparse.ArgumentParser('CANVAS Preprocessing Pipeline', add_help=False)
    parser.add_argument('--config_root', type=str, help='Root directory of the config files')
    parser.add_argument('--data_root', type=str, help='Root directory of all the data')
    parser.add_argument('--data_type', type=str, help='Type of data being processed')
    parser.add_argument('--input_ext', type=str, help='Extension of the input files')
    parser.add_argument('--input_pixel_per_um', type=int, help='Resolution of the input images in pixels per micrometer')
    parser.add_argument('--inference_window_um', type=int, help='Size of the inference window in micrometers')
    parser.add_argument('--ref_channel', type=int, help='channel used for background removal. Ideally DAPI')
    parser.add_argument('--ROI_path', type=str, help='relative to the Region of Interest (ROI) file with annotations')
    parser.add_argument('--selected_region', type=str, help='names of region in ROI_path for analysis')
    parser.add_argument('--raw_image_path', type=str, default='image_files', help='relative path to the raw image files')
    parser.add_argument('--input_path', type=str, default='raw_data', help='relative path to the input data')
    parser.add_argument('--selected_channel_color_file', type=str, help='Full path to the file containing selected channel colors')
    parser.add_argument('--channel_strength_file', type=str, help='Full path to the file containing channel strength information')
    parser.add_argument('--tiles_dir', type=str, default='tiles', help='Directory name containing image tiles')
    return parser

def main():
    parser = get_args_parser()
    args = parser.parse_args()

    clusters_path = os.path.join(args.data_root, "analysis/kmeans/10/clusters.npy")
    tile_embedding_path = os.path.join(args.data_root, "analysis/tile_embedding")

    output_path = os.path.join(args.data_root, "analysis/plots")
    os.makedirs(output_path, exist_ok=True)

    print("Loading cluster assignments and tile metadata...")
    clusters = np.load(clusters_path)
    sample_names = np.load(os.path.join(tile_embedding_path, "sample_name.npy"))

    print(f"Total tiles: {len(clusters)}")
    print(f"Unique clusters: {np.unique(clusters)}")

    # Get unique images and their counts
    unique_images = np.unique(sample_names)
    n_images = len(unique_images)
    print(f"Number of images: {n_images}")
    print("Images found:")
    for i, img in enumerate(unique_images):
        count = np.sum(sample_names == img)
        print(f"  {i+1}. {img}: {count} tiles")

    # Define consistent cluster colors to match the UMAP visualization
    # These should match the colors from your UMAP plot
    cluster_colors = [
        '#1f77b4',  # Cluster 0 - Blue
        '#ff7f0e',  # Cluster 1 - Orange  
        '#2ca02c',  # Cluster 2 - Green
        '#d62728',  # Cluster 3 - Red
        '#9467bd',  # Cluster 4 - Purple
        '#8c564b',  # Cluster 5 - Brown
        '#e377c2',  # Cluster 6 - Pink
        '#7f7f7f',  # Cluster 7 - Gray
        '#bcbd22',  # Cluster 8 - Olive/Yellow-green
        '#17becf'   # Cluster 9 - Cyan
    ]

    # Calculate distribution matrix
    # Rows = clusters, Columns = images
    distribution_matrix = np.zeros((10, n_images))

    for cluster_id in range(10):
        cluster_mask = clusters == cluster_id
        cluster_samples = sample_names[cluster_mask]
        
        for img_idx, img_name in enumerate(unique_images):
            count = np.sum(cluster_samples == img_name)
            distribution_matrix[cluster_id, img_idx] = count

    # Convert to percentages for each cluster
    distribution_percentages = distribution_matrix / distribution_matrix.sum(axis=1, keepdims=True) * 100
    distribution_percentages = np.nan_to_num(distribution_percentages)  # Handle division by zero

    # Create the stacked bar chart
    fig, ax = plt.subplots(figsize=(14, 8))

    # X positions for bars
    x_pos = np.arange(10)
    bar_width = 0.8

    # Create stacked bars
    bottom = np.zeros(10)

    # Define distinct colors for each image/sample
    image_colors = [
        '#e41a1c',  # Red
        '#377eb8',  # Blue  
        '#4daf4a',  # Green
        '#984ea3',  # Purple
        '#ff7f00',  # Orange
        '#ffff33',  # Yellow
        '#a65628',  # Brown
        '#f781bf',  # Pink
        '#999999',  # Gray
        '#66c2a5'   # Teal
    ]

    # Use only as many colors as we have images
    sample_colors = image_colors[:n_images]

    for img_idx in range(n_images):
        # Use the same color for this image across all clusters
        img_color = sample_colors[img_idx]
        
        # Create bar segment for this image
        values = distribution_percentages[:, img_idx]
        bars = ax.bar(x_pos, values, bar_width, bottom=bottom, 
                    color=img_color, alpha=0.8, 
                    label=f'Image {img_idx+1}: {os.path.basename(unique_images[img_idx])}')
        
        # Add percentage labels on bars (only if percentage > 5% to avoid clutter)
        for i, (bar, value) in enumerate(zip(bars, values)):
            if value > 5:  # Only show labels for segments > 5%
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., bottom[i] + height/2,
                    f'{value:.1f}%', ha='center', va='center', 
                    fontsize=8, fontweight='bold', color='white')
        
        bottom += values

    # Customize the plot
    ax.set_xlabel('Cluster', fontsize=14, fontweight='bold')
    ax.set_ylabel('Percentage of Tiles', fontsize=14, fontweight='bold')
    ax.set_title('Cluster Composition by Image', 
                fontsize=16, fontweight='bold', pad=30)

    # Set x-axis
    ax.set_xticks(x_pos)
    ax.set_xticklabels([f'C{i}' for i in range(10)])

    # Set y-axis
    ax.set_ylim(0, 100)
    ax.set_yticks(np.arange(0, 101, 10))

    # Add grid for better readability
    ax.grid(True, alpha=0.3, axis='y')

    # Add legend
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10)

    # Add text with total tile counts per cluster
    for i, cluster_id in enumerate(range(10)):
        total_tiles = int(distribution_matrix[cluster_id].sum())
        ax.text(i, 102, f'n={total_tiles}', ha='center', va='bottom', 
            fontsize=9, fontweight='bold')

    # bm3772/canvas_examples/optimal_channels_combat/data/analysis
    plt.tight_layout()
    plt.savefig(os.path.join(output_path,'sample_distribution_by_cluster.png'), dpi=300, bbox_inches='tight')
    plt.show()

    # Create the second visualization: Cluster distribution by sample
    fig2, ax2 = plt.subplots(figsize=(14, 8))

    # X positions for bars (one per image)
    x_pos_img = np.arange(n_images)
    bar_width = 0.8

    # Calculate distribution matrix for samples (transpose of the original)
    # Rows = images, Columns = clusters
    sample_distribution_matrix = distribution_matrix.T

    # Convert to percentages for each sample
    sample_distribution_percentages = sample_distribution_matrix / sample_distribution_matrix.sum(axis=1, keepdims=True) * 100
    sample_distribution_percentages = np.nan_to_num(sample_distribution_percentages)  # Handle division by zero

    # Create stacked bars for samples
    bottom_sample = np.zeros(n_images)

    for cluster_id in range(10):
        # Use the cluster color for this cluster across all images
        cluster_color = cluster_colors[cluster_id]
        
        # Create bar segment for this cluster
        values = sample_distribution_percentages[:, cluster_id]
        bars = ax2.bar(x_pos_img, values, bar_width, bottom=bottom_sample, 
                    color=cluster_color, alpha=0.8, 
                    label=f'Cluster {cluster_id}')
        
        # Add percentage labels on bars (only if percentage > 5% to avoid clutter)
        for i, (bar, value) in enumerate(zip(bars, values)):
            if value > 5:  # Only show labels for segments > 5%
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2., bottom_sample[i] + height/2,
                        f'{value:.1f}%', ha='center', va='center', 
                        fontsize=8, fontweight='bold', color='white')
        
        bottom_sample += values

    # Customize the second plot
    ax2.set_xlabel('Image', fontsize=14, fontweight='bold')
    ax2.set_ylabel('Percentage of Tiles', fontsize=14, fontweight='bold')
    ax2.set_title('Image Composition by Cluster', 
                fontsize=16, fontweight='bold', pad = 30)

    # Set x-axis with abbreviated image names
    ax2.set_xticks(x_pos_img)
    short_names = [os.path.basename(img)[:20] + '...' if len(os.path.basename(img)) > 20 
                else os.path.basename(img) for img in unique_images]
    ax2.set_xticklabels(short_names, rotation=45, ha='right')

    # Set y-axis
    ax2.set_ylim(0, 100)
    ax2.set_yticks(np.arange(0, 101, 10))

    # Add grid for better readability
    ax2.grid(True, alpha=0.3, axis='y')

    # Add legend
    ax2.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10)

    # Add text with total tile counts per image
    for i, img_idx in enumerate(range(n_images)):
        total_tiles = int(sample_distribution_matrix[img_idx].sum())
        ax2.text(i, 102, f'n={total_tiles}', ha='center', va='bottom', 
            fontsize=9, fontweight='bold')

    plt.tight_layout()
    plt.savefig(os.path.join(output_path,'cluster_distribution_by_sample.png'), dpi=300, bbox_inches='tight')
    plt.show()

    # Print detailed statistics
    print("\n=== Detailed Cluster-Image Distribution ===")
    print("Tile counts (not percentages):")
    print("Cluster\t", end="")
    for img_idx, img_name in enumerate(unique_images):
        short_name = os.path.basename(img_name)[:15]  # Truncate for display
        print(f"{short_name}\t", end="")
    print("Total")

    for cluster_id in range(10):
        print(f"C{cluster_id}\t", end="")
        total = 0
        for img_idx in range(n_images):
            count = int(distribution_matrix[cluster_id, img_idx])
            print(f"{count}\t\t", end="")
            total += count
        print(f"{total}")

    print(f"\nTotal tiles: {distribution_matrix.sum()}")

    # Create a summary table
    summary_data = []
    for cluster_id in range(10):
        for img_idx, img_name in enumerate(unique_images):
            count = int(distribution_matrix[cluster_id, img_idx])
            percentage = distribution_percentages[cluster_id, img_idx]
            summary_data.append({
                'Cluster': cluster_id,
                'Image': os.path.basename(img_name),
                'Tile_Count': count,
                'Percentage': percentage
            })

    summary_df = pd.DataFrame(summary_data)
    summary_df.to_csv(os.path.join(output_path, 'cluster_image_distribution_summary.csv'), index=False)
    print(f"\nSaved detailed distribution to 'cluster_image_distribution_summary.csv'")


    print(f"\n=== Summary ===")
    print(f"Generated two visualizations:")
    print(f"1. 'sample_distribution_by_cluster.png' - Shows how each cluster is distributed across images")
    print(f"2. 'cluster_distribution_by_sample.png' - Shows how each image is distributed across clusters")

if __name__ == "__main__":
    main()