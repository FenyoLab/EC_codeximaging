import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from types import SimpleNamespace
sys.path.append('/gpfs/home/as18894/projects/as18894/FenyoLab/Endometrial/EC_codeximaging')
from utils import helper

def main():
    #import config
    config_yaml= 'barcharts.yaml'
    run_config = helper.load_yaml_file(config_yaml)
    config = SimpleNamespace(**run_config)
    group_name = 'Recurrence'

    save_path = os.path.join(config.cell_types_dir, 'figures')

    celltype_barchart_grouped(cell_types_dir = config.cell_types_dir, custom_colors_dict = config.custom_colors, 
                            group_dict = config.recurrence_status, group_name = group_name, save_path = save_path)

def celltype_barchart_grouped(cell_types_dir, custom_colors_dict, group_dict, group_name, save_path):
    cell_types = pd.read_csv(os.path.join(cell_types_dir, 'cell_types.csv'), index_col=0)
    cell_types = cell_types[cell_types['cell_type'] != 'Artifact']
    cell_types = cell_types.copy()  
    cell_types['cell_type'] = cell_types['cell_type'].replace( #combine immune cell types for visualization
        ['CD20+ and CD3e+ cells', 'CD20+ and CD4+ cells', 
        'CD20+ and CD8+ cells', 'CD4+ and CD8+ T cells'], 
        'Immune cells (mixed)'
    )

    custom_order = list(custom_colors_dict.keys())

    # Proportion calculations
    proportions = cell_types.groupby(['cell_type', 'slide_id']).size().unstack(fill_value=0)
    proportions = proportions.reindex(custom_order)
    proportions = proportions.div(proportions.sum(axis=0), axis=1)

    # Extract sample groups based on the group_dict (e.g., response status)
    group_samples = {status: [sample for sample, status_val in group_dict.items() if status_val == status] 
                    for status in set(group_dict.values())}
    # Create a MultiIndex DataFrame for the grouped data
    grouped_dfs = []
    for status, samples in group_samples.items():
        grouped_dfs.append(proportions[samples])
    
    # Combine the DataFrames into one with MultiIndex columns
    organized_df = pd.concat(grouped_dfs, axis=1)
    #print(organized_df.shape)
    #print(organized_df.head())
    organized_df.columns = pd.MultiIndex.from_tuples(
        [(status, col) for status, samples in group_samples.items() for col in proportions.columns if col in samples],
        names=[group_name, "Slide ID"]
    )   

    # Melt the DataFrame for plotting
    df_melted = (
        organized_df
        .reset_index()  # Convert index (cell types) into columns
        .melt(id_vars=["cell_type"], var_name=[group_name, "Slide ID"], value_name="Proportion")
    )

    # Get unique slide IDs for each group
    group_data = {
        status: df_melted[df_melted[group_name] == status] for status in group_samples.keys()
    }

    # Get unique cell types
    cell_types = df_melted["cell_type"].unique()

    # Initialize a figure with subplots (one for each group)
    if len(group_samples) > 3:
        fig, axes = plt.subplots(1, len(group_samples), figsize=(18, 10), sharey=True)
    else:
        fig, axes = plt.subplots(1, len(group_samples), figsize=(14, 10), sharey=True)

    plt.suptitle(f'{group_name} Status', fontsize=20)

    for i, (status, data) in enumerate(group_data.items()):
        slides = data["Slide ID"].unique()
        plot_group(axes[i], data, cell_types, custom_colors_dict, slides, status)
    
    # Adjust layout
    fig.tight_layout()

    # Add a legend outside the plot
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='lower right', ncol=1, title="Cell Types", bbox_to_anchor=(0.97, 0.08))

    # Save the figure
    plt.tight_layout()
    print(f'Saving celltypes_barchart_{group_name.lower()} to {save_path}')
    plt.savefig(os.path.join(save_path, f'celltypes_barchart_{group_name.lower()}.png'), dpi=300)

def plot_group(ax, data, cell_types, custom_colors_dict, slides, title):
    # Create a zero baseline for stacking
    bar_bottom = np.zeros(len(slides))

    for cell_type in cell_types:
        # Get proportions for each slide and cell type
        proportions = [
            data[(data["Slide ID"] == slide) & (data["cell_type"] == cell_type)]["Proportion"].sum()
            for slide in slides
        ]
        # Plot horizontal bars
        ax.barh(slides, proportions, left=bar_bottom, color=custom_colors_dict[cell_type], label=cell_type)
        # Update the baseline
        bar_bottom += proportions

    # Title and labels
    ax.set_title(title, fontsize=18)
    ax.set_xlabel("Proportion", fontsize=14)
    if ax == 0:
        ax.set_ylabel("Slides", fontsize=16)

if __name__ == "__main__":
    main()