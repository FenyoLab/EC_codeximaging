import pandas as pd
import argparse
import os
import plotly.express as px
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
    fig.update_xaxes(showgrid=False, zeroline=False, title=None)
    fig.update_yaxes(showgrid=False, zeroline=False, autorange='reversed', title=None)

    if save_path:
        fig.write_html(save_path)

#---------------------------------
# DEFINE CELL TYPE COLORS
#---------------------------------
cell_type_colors_path = "../../config/color_palettes/celesta_cell_type_colors_dark.json"
with open(cell_type_colors_path, "r") as f:
    cell_type_colors = json.load(f)

if __name__ == "__main__":
    print("------------------------------------")
    print("Project title:", project_title)
    print("Plotting interactive cell assignments for:", project_title)
    print("------------------------------------")

    for file in os.listdir(save_path):
        if file.endswith("final_cell_type_assignment.csv"):
            file_prefix = file.replace("final_cell_type_assignment.csv", "")
            cell_assignments_csv = os.path.join(save_path, file)
            print("Plotting results for:", file_prefix)
            
            df = pd.read_csv(cell_assignments_csv)

            plot_interactive_cell_assignments(
                df,
                x_col='Y',
                y_col='X',
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