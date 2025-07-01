import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import argparse
import os
import json
import yaml

#  arg parsing
parser = argparse.ArgumentParser()
parser.add_argument('--sample', type=str, required=True, help='Sample name (used to construct paths)')
args = parser.parse_args()

# load config
with open("../../config/config_celesta_pipeline.yaml", "r") as f:
    config = yaml.safe_load(f)

project_title_prefix = config["project_title_prefix"]
project_title = f"{project_title_prefix}_{args.sample}"
results_dir = config["paths"]["results_dir"]

save_path = f"{results_dir}/{project_title}"
if not os.path.exists(save_path):
    os.makedirs(save_path)

#---------------------------------
# PLOT CELL PROPORTIONS
#---------------------------------
def plot_cell_proportions(df, cell_type_col, color_map=None, normalize=True, save_path=None):
    """
    Plot the proportions or counts of cell types in a single dataset.

    Parameters:
    - df: pandas DataFrame containing cell type information.
    - cell_type_col: Column name in df that contains the cell type.
    - color_map: Optional dictionary mapping cell types to colors.
    - normalize: If True, plot proportions; otherwise, plot raw counts.
    - save_path: Optional path to save the figure. If None, plot is shown.
    """
    # count cell types
    counts = df[cell_type_col].value_counts(ascending=True)

    if normalize:
        counts = counts / counts.sum()

    # define colors
    all_cell_types = counts.index.tolist()
    if color_map is None:
        cmap = plt.cm.get_cmap('tab20', len(all_cell_types))
        color_map = {cell_type: cmap(i) for i, cell_type in enumerate(all_cell_types)}

    colors = [color_map.get(ct, 'gray') for ct in all_cell_types]

    # plot
    fig, ax = plt.subplots(figsize=(4, 10), facecolor='black')
    ax.set_facecolor('black')

    bottom = 0
    for ct, val, color in zip(all_cell_types, counts, colors):
        ax.bar("Cells", val, bottom=bottom, color=color, edgecolor='black', label=ct)
        bottom += val

    if normalize:
        ax.set_ylim(0, 1)

    ax.set_ylabel('Proportion' if normalize else 'Count', color='white')
    ax.set_title('Cell Type Proportions', color='white', pad=20)
    ax.tick_params(axis='x', colors='white')
    ax.tick_params(axis='y', colors='white')
    for spine in ax.spines.values():
        spine.set_edgecolor('white')

    # legend (same order as bar plot)
    ordered_labels = counts.index.tolist()[::-1]  # reverse order for legend
    ordered_handles = [plt.Rectangle((0,0),1,1, color=color_map[ct]) for ct in ordered_labels]

    legend = ax.legend(ordered_handles, ordered_labels,
                    bbox_to_anchor=(1.05, 1), loc='upper left',
                    title='Cell Type', frameon=False)

    plt.setp(legend.get_texts(), color='white')
    plt.setp(legend.get_title(), color='white')

    plt.tight_layout()

    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()

#---------------------------------
# PLOT CELL ASSIGNMENTS
#---------------------------------
def plot_cell_assignments(
    df,
    x_col='X',
    y_col='Y',
    cell_type_col='Final cell type',
    cell_type_colors=None,
    base_layer='Stromal cells (undefined)',
    include_cell_types=None,
    exclude_cell_types=None,
    title='Cell Assignments',
    alpha=1,
    point_size=0.5,
    save_path=None
):
    df[cell_type_col] = df[cell_type_col].astype('category')

    # cell type counts
    counts = df[cell_type_col].value_counts().sort_values()
    cell_types = counts.index.tolist()

    # include/exclude cell types
    if include_cell_types is not None:
        cell_types = [ct for ct in cell_types if ct in include_cell_types]
    elif exclude_cell_types is not None:
        cell_types = [ct for ct in cell_types if ct not in exclude_cell_types]

    # define colors
    if cell_type_colors is None:
        cmap = plt.cm.get_cmap('tab20', len(cell_types))
        cell_type_colors = {cell_type: cmap(i) for i, cell_type in enumerate(cell_types)}
    else:
        for ct in cell_types:
            if ct not in cell_type_colors:
                cell_type_colors[ct] = 'white'

    plt.figure(figsize=(20, 16), facecolor='black')
    ax = plt.gca()
    ax.set_facecolor('black')

    ax.invert_yaxis()

    # plot base layer first
    if base_layer in cell_types:
        subset = df[df[cell_type_col] == base_layer]
        plt.scatter(subset[x_col], subset[y_col], label=base_layer,
                    color='gray', s=point_size, alpha=alpha, zorder=1)
        cell_types.remove(base_layer)

    # plot remaining in descending count order
    for i, cell_type in enumerate(reversed(cell_types)):
        subset = df[df[cell_type_col] == cell_type]
        plt.scatter(subset[x_col], subset[y_col], label=cell_type,
                    color=cell_type_colors[cell_type], s=point_size, alpha=alpha, zorder=2+i)

    # plot
    plt.title(title, color='white', fontsize=24)
    plt.tick_params(axis='both', colors='white', labelsize=16)
    plt.grid(False)
    for spine in ax.spines.values():
        spine.set_edgecolor('white')

    plt.legend(
        title='Cell Type',
        bbox_to_anchor=(1.05, 1),
        loc='upper left',
        frameon=False,
        title_fontsize=18,        
        fontsize=16,              
        markerscale=10,            
        handletextpad=0.5,
        borderpad=0.5,
        labelcolor='white'
    )

    plt.tight_layout()

    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()

#---------------------------------
# DEFINE CELL TYPE COLORS
#---------------------------------
cell_type_colors_path = "../../config/color_palettes/celesta_cell_type_colors_dark.json"
with open(cell_type_colors_path, "r") as f:
    cell_type_colors = json.load(f)

if __name__ == "__main__":
    print("------------------------------------")
    print("Project title:", project_title)
    print("Plotting cell proportions and assignments for:", project_title)
    print("------------------------------------")

    for file in os.listdir(save_path):
        if file.endswith("final_cell_type_assignment.csv"):
            file_prefix = file.replace("final_cell_type_assignment.csv", "")
            cell_assignments_csv = os.path.join(save_path, file)
            print("Plotting results for:", file_prefix)
            
            df = pd.read_csv(cell_assignments_csv)
            
            plot_cell_proportions(
                df, 
                cell_type_col='Final cell type', 
                color_map=cell_type_colors,
                save_path=f"{save_path}/{file_prefix}_cell_proportions.png")

            plot_cell_assignments(
                df,
                x_col='X',
                y_col='Y',
                cell_type_col='Final cell type',
                cell_type_colors=cell_type_colors,
                base_layer='Stromal_Undefined',
                include_cell_types=None,
                exclude_cell_types=None,
                title='Cell Assignments',
                alpha=1,
                point_size=0.5,
                save_path=f"{save_path}/{file_prefix}_cell_assignments.png"
            )

            print("Done. Plots saved to:", save_path)