import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import argparse
import os

#  arg parsing
parser = argparse.ArgumentParser(description='Plot expression probability.')
parser.add_argument('--project_title', type=str, default="celesta_test", help='Same title as in create_celesta_obj.sh, name of subdirectory in results_dir.')
parser.add_argument('--results_dir', type=str, default="/gpfs/data/proteomics/home/yb2612/results/celesta", help='Path to results directory created by create_celesta_obj.sh')
parser.add_argument('--cell_assignments_csv', type=str, help='Path to final cell type assignments CSV.')
args = parser.parse_args()

project_title = args.project_title

save_path = f"{args.results_dir}/{project_title}/plot_results"
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
    # Count cell types
    counts = df[cell_type_col].value_counts().sort_index()

    if normalize:
        counts = counts / counts.sum()

    # Define colors
    all_cell_types = counts.index.tolist()
    if color_map is None:
        cmap = plt.cm.get_cmap('tab20', len(all_cell_types))
        color_map = {cell_type: cmap(i) for i, cell_type in enumerate(all_cell_types)}

    colors = [color_map.get(ct, 'gray') for ct in all_cell_types]

    # Plot
    fig, ax = plt.subplots(figsize=(4, 10), facecolor='black')
    ax.set_facecolor('black')

    bottom = 0
    for ct, val, color in zip(all_cell_types, counts, colors):
        ax.bar("Cells", val, bottom=bottom, color=color, edgecolor='black', label=ct)
        bottom += val

    # Aesthetic settings
    ax.set_ylabel('Proportion' if normalize else 'Count', color='white')
    ax.set_title('Cell Type Proportions', color='white')
    ax.tick_params(axis='x', colors='white')
    ax.tick_params(axis='y', colors='white')
    for spine in ax.spines.values():
        spine.set_edgecolor('white')

    # Legend
    handles, labels = ax.get_legend_handles_labels()
    unique = dict(zip(labels, handles))
    legend = ax.legend(unique.values(), unique.keys(), bbox_to_anchor=(1.05, 1), loc='upper left',
                       title='Cell Type', frameon=False)
    plt.setp(legend.get_texts(), color='white')
    plt.setp(legend.get_title(), color='white')

    plt.tight_layout()

    plt.savefig(f"{save_path}/plot_cell_proportions.png", dpi=300, bbox_inches='tight')
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
    alpha=0.7,
    point_size=10,
    save_path=None
):
    df[cell_type_col] = df[cell_type_col].astype('category')

    # Compute cell type counts
    counts = df[cell_type_col].value_counts().sort_values()
    cell_types = counts.index.tolist()

    # Filter based on inclusion/exclusion
    if include_cell_types is not None:
        cell_types = [ct for ct in cell_types if ct in include_cell_types]
    elif exclude_cell_types is not None:
        cell_types = [ct for ct in cell_types if ct not in exclude_cell_types]

    # Initialize colors
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

    # Plot base layer first
    if base_layer in cell_types:
        subset = df[df[cell_type_col] == base_layer]
        plt.scatter(subset[x_col], subset[y_col], label=base_layer,
                    color='gray', s=point_size, alpha=alpha, zorder=1)
        cell_types.remove(base_layer)

    # Plot remaining in descending count order
    for i, cell_type in enumerate(reversed(cell_types)):
        subset = df[df[cell_type_col] == cell_type]
        plt.scatter(subset[x_col], subset[y_col], label=cell_type,
                    color=cell_type_colors[cell_type], s=point_size, alpha=alpha, zorder=2+i)

    # Plot styling
    plt.title(title, color='white')
    plt.xlabel(x_col, color='white')
    plt.ylabel(y_col, color='white')
    plt.tick_params(axis='both', colors='white')
    plt.grid(False)
    for spine in ax.spines.values():
        spine.set_edgecolor('white')

    plt.legend(title='Cell Type', bbox_to_anchor=(1.05, 1), loc='upper left',
               frameon=False, title_fontsize=12, fontsize=10,
               facecolor='black', edgecolor='white', labelcolor='white')

    plt.tight_layout()

    plt.savefig(f"{save_path}/plot_cell_assignments.png", dpi=300, bbox_inches='tight')
    plt.close()

#---------------------------------
# DEFINE CELL TYPE COLORS
#---------------------------------
cell_type_colors = {
    'Stromal cells (undefined)': '#A9A9A9',    # dark gray
    'Tumor cells': '#FF6347',                  # tomato red
    'Endothelial cells': '#FFFF00',            # yellow
    'Neutrophils': '#FFFFFF',                  # white
    'Macrophages (CD163-)': '#C71585',         # medium violet red (pinkish)
    'Macrophages (CD163+)': '#9370DB',         # medium purple
    'CD8 T cells': '#DC143C',            # crimson
    'T cells (other)': '#228B22',              # forest green
    'CD4 T cells': '#00FF7F',               # spring green (distinct)
    'B cells': '#1E90FF',                      # dodger blue
}

cell_type_colors = {
    'Stromal_Undefined': '#A9A9A9',    # dark gray
    'Tumor': '#A42A2A',                  # crimson
    'Endothelial': '#33FD02',            # green
    'Neutrophil': '#34FEFF',                  # cyan
    'Macrophage': '#FB22FF',         # magenta
    'Macrophage (CD163-)': '#FB22FF',         # magenta
    'Macrophage (CD163+)': '#FFC5D3',         # lightpink
    'CD8_T': '#FFFE04',            # yellow
    'T': '#008B8B',              # dark cyan
    'CD4_T': '#FC8001',               # orange
    'B': '#FFFFFF',                      # white
}

if __name__ == "__main__":
    print("------------------------------------")
    print("Project title:", project_title)
    print("Plotting cell proportions and assignments for:", args.cell_assignments_csv)
    print("------------------------------------")

    df = pd.read_csv(args.cell_assignments_csv)
    
    plot_cell_proportions(df, cell_type_col='Final cell type', save_path=save_path)

    plot_cell_assignments(
        df,
        x_col='X',
        y_col='Y',
        cell_type_col='Final cell type',
        cell_type_colors=cell_type_colors,
        base_layer='Stromal cells (undefined)',
        include_cell_types=None,
        exclude_cell_types=None,
        title='Cell Assignments',
        alpha=0.7,
        point_size=0.5,
        save_path=save_path
    )

    print("Done. Plots saved to:", save_path)