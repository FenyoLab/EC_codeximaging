import pandas as pd
import argparse
import os
import plotly.express as px

#  arg parsing
parser = argparse.ArgumentParser(description='Plot expression probability.')
parser.add_argument('--project_title', type=str, default="celesta_test", help='Same title as in create_celesta_obj.sh, name of subdirectory in results_dir.')
parser.add_argument('--results_dir', type=str, default="/gpfs/data/proteomics/home/yb2612/results/celesta", help='Path to results directory created by create_celesta_obj.sh')
args = parser.parse_args()

project_title = args.project_title

save_path = f"{args.results_dir}/{project_title}"
if not os.path.exists(save_path):
    os.makedirs(save_path)

#---------------------------------
# PLOT INTERACTIVE CELL ASSIGNMENTS
#---------------------------------
def plot_interactive_cell_assignments(
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
    point_size=1,
    save_path=None
):
    df[cell_type_col] = df[cell_type_col].astype('category')

    # Compute cell type counts
    counts = df[cell_type_col].value_counts().sort_values()
    cell_types = counts.index.tolist()

    # Filter based on inclusion/exclusion
    if include_cell_types is not None:
        cell_types = [ct for ct in cell_types if ct in include_cell_types]
        df = df[df[cell_type_col].isin(include_cell_types)]
    elif exclude_cell_types is not None:
        cell_types = [ct for ct in cell_types if ct not in exclude_cell_types]
        df = df[~df[cell_type_col].isin(exclude_cell_types)]

    # Setup default color mapping if not provided
    if cell_type_colors is None:
        cmap = plt.cm.get_cmap('tab20', len(cell_types))
        cell_type_colors = {cell_type: f'rgb{tuple(int(c*255) for c in cmap(i))}' for i, cell_type in enumerate(cell_types)}
    else:
        for ct in cell_types:
            if ct not in cell_type_colors:
                cell_type_colors[ct] = '#FFFFFF'

    # Plotly expects a discrete color map dict
    color_discrete_map = {k: v for k, v in cell_type_colors.items() if k in df[cell_type_col].unique()}

    # Create plot
    fig = px.scatter(
        df,
        x=x_col,
        y=y_col,
        color=cell_type_col,
        color_discrete_map=color_discrete_map,
        title=title,
        opacity=alpha,
        width=1200,
        height=1000,
        hover_data=[cell_type_col]
    )

    fig.update_traces(marker=dict(size=point_size))
    fig.update_layout(
        plot_bgcolor='black',
        paper_bgcolor='black',
        font=dict(color='white'),
        legend=dict(itemsizing='constant')
    )
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(showgrid=False, zeroline=False)

    if save_path:
        fig.write_html(save_path)

#---------------------------------
# DEFINE CELL TYPE COLORS
#---------------------------------
cell_type_colors = {
    'Unknown': '#808080',                       # gray
    'Stromal_Undefined': '#A9A9A9',             # dark gray
    'Stromal cells (undefined)': '#A9A9A9',     # dark gray
    'Tumor': '#A42A2A',                         # crimson
    'Tumor cells': '#A42A2A',                   # crimson
    'Endothelial': '#33FD02',                   # green
    'Endothelial cells': '#33FD02',             # green
    'Neutrophil': '#34FEFF',                    # cyan
    'Neutrophils': '#34FEFF',                   # cyan
    'Macrophage': '#FB22FF',                    # magenta
    'Macrophage (CD163-)': '#FB22FF',           # magenta
    'Macrophages (CD163-)': '#FB22FF',          # magenta
    'Macrophage (CD163+)': '#FFC5D3',           # lightpink
    'Macrophages (CD163+)': '#FFC5D3',          # lightpink
    'CD8_T': '#FFFE04',                         # yellow
    'Cytotoxic T cells': '#FFFE04',             # yellow
    'T': '#008B8B',                             # dark cyan
    'T cells (other)': '#008B8B',               # dark cyan
    'CD4_T': '#FC8001',                         # orange
    'Helper T cells': '#FC8001',                # orange
    'B': '#FFFFFF',                             # white
    'B cells': '#FFFFFF',                       # white
}

if __name__ == "__main__":
    print("------------------------------------")
    print("Project title:", project_title)
    print("Plotting interactive cell assignments for:", args.project_title)
    print("------------------------------------")

    for file in os.listdir(save_path):
        if file.endswith("final_cell_type_assignment.csv"):
            file_prefix = file.replace("final_cell_type_assignment.csv", "")
            cell_assignments_csv = os.path.join(save_path, file)
            print("Plotting results for:", file_prefix)
            
            df = pd.read_csv(cell_assignments_csv)

            plot_interactive_cell_assignments(
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
                point_size=3,
                save_path=f"{save_path}/{file_prefix}_interactive_cell_assignments.html"
            )

            print("Done. Plots saved to:", save_path)