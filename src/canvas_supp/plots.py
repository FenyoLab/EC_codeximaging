import os
import argparse
import pandas as pd
import numpy as np
import zarr
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

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
    base_path = os.path.join(args.data_root,"processed_data/data")

    print("Loading cluster assignments and tile metadata...")
    clusters = np.load(clusters_path)
    tile_locations = np.load(os.path.join(tile_embedding_path, "tile_location.npy"))
    sample_names = np.load(os.path.join(tile_embedding_path, "sample_name.npy"))

    print(f"Total clusters: {len(clusters)}")
    print(f"Total tile locations: {len(tile_locations)}")
    print(f"Total sample names: {len(sample_names)}")

    # Verify all arrays have the same length
    assert len(clusters) == len(tile_locations) == len(sample_names), "Metadata arrays have different lengths!"

    print(f"Sample names (first 10): {sample_names[:10]}")
    print(f"Tile locations (first 5): {tile_locations[:5]}")
    print(f"Clusters (first 10): {clusters[:10]}")

    # Function to extract tile data from zarr
    def extract_tile_data(zarr_path, h, w, tile_size=128):
        """Extract a 128x128 tile from zarr at position (h, w)"""
        data_zarr = zarr.open(zarr_path, mode='r')
        
        # Extract the tile (zarr shape is [C, H, W] where C=9 channels)
        # So we extract [:, h:h+tile_size, w:w+tile_size] and transpose to [H, W, C]
        tile_data = data_zarr[:, h:h+tile_size, w:w+tile_size]
        
        # Transpose from [C, H, W] to [H, W, C] for easier processing
        tile_data = np.transpose(tile_data, (1, 2, 0))
        
        return tile_data

    # Extract tile data using the exact metadata
    print("\nExtracting tile data using CANVAS metadata...")

    all_channel_averages = []  # List of [9 channel averages] for each tile
    all_cluster_assignments = []  # Corresponding cluster for each tile
    all_sample_names = []  # Which image each tile came from

    # Process each tile using the metadata
    for tile_idx in range(len(clusters)):
        # Get metadata for this tile
        sample_name = sample_names[tile_idx]
        h, w = tile_locations[tile_idx]
        cluster_id = clusters[tile_idx]
        
        # Construct zarr path for this sample
        zarr_path = os.path.join(base_path, sample_name, "data.zarr")
        
        # Extract tile data
        try:
            tile_data = extract_tile_data(zarr_path, int(h), int(w))
            
            # Calculate average intensity for each channel
            # tile_data shape should be (128, 128, 9)
            channel_averages = np.mean(tile_data, axis=(0, 1))  # Average over spatial dimensions
            
            # Store results
            all_channel_averages.append(channel_averages)
            all_cluster_assignments.append(cluster_id)
            all_sample_names.append(sample_name)
            
        except Exception as e:
            print(f"Error processing tile {tile_idx} from {sample_name} at ({h}, {w}): {e}")
            continue
        
        # Progress update
        if (tile_idx + 1) % 1000 == 0:
            print(f"  Processed {tile_idx + 1}/{len(clusters)} tiles")

    # Convert to numpy arrays
    all_channel_averages = np.array(all_channel_averages)
    all_cluster_assignments = np.array(all_cluster_assignments)

    print(f"\nSuccessfully processed {len(all_channel_averages)} tiles")
    print(f"Channel averages shape: {all_channel_averages.shape}")
    print(f"Unique clusters: {np.unique(all_cluster_assignments)}")

    # Check sample distribution
    unique_samples, sample_counts = np.unique(all_sample_names, return_counts=True)
    print(f"\nSample distribution:")
    for sample, count in zip(unique_samples, sample_counts):
        print(f"  {sample}: {count} tiles")

    # Define channel names and colors based on the YAML config
    channel_names = [
        'E-cadherin',    # Channel 0 - Epithelial cells
        'CD31',          # Channel 1 - Endothelial cells  
        'CD3e',          # Channel 2 - T cells
        'CD68',          # Channel 3 - Macrophages
        'CD163',         # Channel 4 - M2 macrophages
        'MPO',           # Channel 5 - Neutrophils
        'CD20',          # Channel 6 - B cells
        'CD8',           # Channel 7 - Cytotoxic T cells
        'CD4'            # Channel 8 - Helper T cells
    ]

    # Define colors for each channel (convert RGB to normalized values)
    channel_colors = [
        np.array([255, 0, 0]) / 255,      # E-cadherin - red
        np.array([0, 255, 0]) / 255,      # CD31 - green
        np.array([0, 0, 255]) / 255,      # CD3e - blue
        np.array([50, 205, 50]) / 255,    # CD68 - lime green
        np.array([0, 255, 255]) / 255,    # CD163 - cyan
        np.array([255, 255, 0]) / 255,    # MPO - yellow
        np.array([255, 0, 255]) / 255,    # CD20 - magenta
        np.array([255, 165, 0]) / 255,    # CD8 - orange
        np.array([128, 0, 128]) / 255     # CD4 - purple
    ]

    # Create DataFrame for easier plotting
    data_list = []
    for tile_idx in range(len(all_channel_averages)):
        cluster_id = all_cluster_assignments[tile_idx]
        sample_name = all_sample_names[tile_idx]
        for channel_idx in range(9):  # 9 channels
            channel_avg = all_channel_averages[tile_idx, channel_idx]
            data_list.append({
                'tile_idx': tile_idx,
                'cluster': cluster_id,
                'channel': channel_idx,
                'channel_name': channel_names[channel_idx],
                'sample_name': sample_name,
                'average_intensity': channel_avg
            })

    df = pd.DataFrame(data_list)
    print(f"Created DataFrame with {len(df)} rows")

    # Create the visualization: 10 plots (one per cluster), each with 9 violins (one per channel)
    fig, axes = plt.subplots(2, 5, figsize=(25, 12))
    axes = axes.flatten()

    for cluster_id in range(10):
        ax = axes[cluster_id]
        
        # Get data for this cluster
        cluster_data = df[df['cluster'] == cluster_id]
        
        if len(cluster_data) == 0:
            ax.set_title(f'Cluster {cluster_id} (No Data)', fontsize=14, fontweight='bold')
            ax.set_visible(False)
            continue
        
        # Prepare data for violin plot - one violin per channel
        violin_data = []
        for channel_idx in range(9):
            channel_cluster_data = cluster_data[cluster_data['channel'] == channel_idx]['average_intensity'].values
            violin_data.append(channel_cluster_data)
        
        # Create violin plot
        parts = ax.violinplot(violin_data, positions=range(9), widths=0.8, showmeans=True, showmedians=True)
        
        # Apply channel-specific colors
        for pc, color in zip(parts['bodies'], channel_colors):
            pc.set_facecolor(color)
            pc.set_alpha(0.7)
        
        # Customize the plot
        num_tiles = len(cluster_data) // 9  # Each tile contributes 9 rows (one per channel)
        ax.set_title(f'Cluster {cluster_id} ({num_tiles} tiles)', fontsize=14, fontweight='bold')
        ax.set_xlabel('Protein Markers', fontsize=11)
        ax.set_ylabel('Average Intensity', fontsize=11)
        ax.set_xticks(range(9))
        ax.set_xticklabels([name for name in channel_names], rotation=45, ha='right', fontsize=9)
        ax.grid(True, alpha=0.3)

    plt.tight_layout()

    # Add overall title
    fig.suptitle('Protein Marker Expression by Cluster', 
                fontsize=20, fontweight='bold', y=1.02)

    plt.subplots_adjust(top=0.92, bottom=0.15)
    plt.savefig(os.path.join(output_path,'protein_expression_by_cluster.png'), dpi=300, bbox_inches='tight')
    plt.show()

    # Print summary statistics for each cluster
    print("\n=== Cluster Summary Statistics ===")
    for cluster_id in range(10):
        cluster_data = df[df['cluster'] == cluster_id]
        if len(cluster_data) == 0:
            print(f"\nCluster {cluster_id}: No tiles")
            continue
            
        num_tiles = len(cluster_data) // 9  # Each tile contributes 9 rows (one per channel)
        
        # Sample distribution within this cluster
        cluster_samples = cluster_data.groupby('sample_name')['tile_idx'].nunique()
        sample_info = ", ".join([f"{sample}: {count}" for sample, count in cluster_samples.items()])
        
        print(f"\nCluster {cluster_id}: {num_tiles} tiles ({sample_info})")
        
        for channel_idx in range(9):
            channel_data = cluster_data[cluster_data['channel'] == channel_idx]
            if len(channel_data) > 0:
                print(f"  {channel_names[channel_idx]}: mean={channel_data['average_intensity'].mean():.3f}, "
                    f"std={channel_data['average_intensity'].std():.3f}")

    # # Create a legend for the protein markers
    # fig_legend, ax_legend = plt.subplots(figsize=(12, 2))
    # ax_legend.axis('off')

    # # Create color patches for legend
    # from matplotlib.patches import Patch
    # legend_elements = [Patch(facecolor=color, label=name) 
    #                 for color, name in zip(channel_colors, channel_names)]

    # ax_legend.legend(handles=legend_elements, loc='center', ncol=9, 
    #                 title='Protein Marker Colors', title_fontsize=14, fontsize=12)

    # plt.tight_layout()
    # plt.savefig(os.path.join(output_path,'protein_marker_legend.png'), dpi=300, bbox_inches='tight')
    # plt.show()

    # Save the tile mapping for future reference
    mapping_df = pd.DataFrame({
        'tile_index': range(len(clusters)),
        'sample_name': sample_names,
        'h_coordinate': tile_locations[:, 0],
        'w_coordinate': tile_locations[:, 1],
        'cluster_id': clusters
    })

    mapping_df.to_csv(os.path.join(output_path,'tile_cluster_mapping.csv'), index=False)
    print(f"\nSaved tile-cluster mapping to 'tile_cluster_mapping.csv'")
    print(f"This file contains the exact mapping between tile indices, coordinates, samples, and clusters.")

if __name__ == "__main__":
    main()