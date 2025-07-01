import math
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd 
import os
import json
from scipy.stats import ttest_ind, mannwhitneyu
from collections import defaultdict

# paths
all_proportion_dfs_path = "/gpfs/data/proteomics/data/Cervical_mIF/output/seurat_objects/plots/cell_proportion_plots/all_proportion_dfs.json"
sigdiff_output_dir = "/gpfs/data/proteomics/data/Cervical_mIF/output/seurat_objects/plots/cell_proportion_plots/wilcoxon_csv"
plots_output_dir = "/gpfs/data/proteomics/data/Cervical_mIF/output/seurat_objects/plots/cell_proportion_plots/"

if not os.path.exists(sigdiff_output_dir):
    os.makedirs(sigdiff_output_dir)

if not os.path.exists(plots_output_dir):
    os.makedirs(plots_output_dir)

print(f"All significance testing dfs saved to {sigdiff_output_dir}")
print(f"All plots saved to {plots_output_dir}\n")

# variables
normalize_cols = ["dist_group"]
celltype_cols = ["Fine.cell.type", "Final.cell.type", "Parent.cell.type", "Grandparent.cell.type"]

# colors
cell_type_colors_path = "../../config/color_palettes/fine_cell_type_colors.json"
with open(cell_type_colors_path, "r") as f:
    cell_type_colors = json.load(f)

# significance testing
def compare_proportions_sig(proportion_df, celltype_col, method="wilcoxon"):
    """
    Compare slope distributions between 'Yes' and 'No' responses for each Fine.cell.type.
    
    Parameters:
    - slope_df: DataFrame with columns ['Fine.cell.type', 'Response', 'slope']
    - method: "ttest" or "wilcoxon"

    Returns:
    - result_df: DataFrame with columns:
        ['Fine.cell.type', 'n_Yes', 'n_No', 'mean_Yes', 'mean_No', 'pval']
    """
    results = []

    for cell_type, group in proportion_df.groupby(celltype_col):
        # group proportions by response
        pct_yes = group[group["Response"] == "Yes"]["pct"].dropna()
        pct_no = group[group["Response"] == "No"]["pct"].dropna()

        # skip if not enough samples
        if len(pct_yes) < 2 or len(pct_no) < 2:
            pval = None
        elif method == "ttest":
            _, pval = ttest_ind(pct_yes, pct_no, equal_var=False)
        elif method == "wilcoxon":
            _, pval = mannwhitneyu(pct_yes, pct_no, alternative="two-sided")
        else:
            raise ValueError(f"Unsupported method: {method}")
            stat, pval = ttest_ind(pct_yes, pct_no, equal_var=False)

        results.append({
            celltype_col: cell_type,
            "n_Yes": len(pct_yes),
            "n_No": len(pct_no),
            "mean_Yes": pct_yes.mean() if len(pct_yes) > 0 else None,
            "mean_No": pct_no.mean() if len(pct_no) > 0 else None,
            "pval": pval
        })

    sig_df = pd.DataFrame(results)
    return sig_df

# stacked bar plot
def plot_stacked_proportions_by_response(proportion_df, celltype_col, cell_type_colors, output_dir=None, filename_suffix=""):
    """
    Create stacked bar plots showing proportions of each cell type,
    grouped by 'Response' (e.g., Yes vs No).
    """
    # aggregate to get mean proportion of each cell type per Response
    grouped = (
        proportion_df
        .groupby(["Response", celltype_col])["pct"]
        .mean()
        .reset_index()
    )

    # pivot to response columns, index=cell types
    pivot_df = grouped.pivot(index=celltype_col, columns="Response", values="pct").fillna(0)

    # normalize columns to 1 if desired
    pivot_df = pivot_df.div(pivot_df.sum(axis=0), axis=1)
    pivot_df = pivot_df[["Yes", "No"]]
    responses = pivot_df.columns.tolist()
    cell_types = pivot_df.index.tolist()

    # color map
    color_map = cell_type_colors

    fig, ax = plt.subplots(figsize=(6, 8))

    bottoms = np.zeros(len(responses))
    for cell_type in cell_types:
        heights = pivot_df.loc[cell_type].values
        ax.bar(responses, heights, bottom=bottoms,
               color=color_map[cell_type], edgecolor=None, label=cell_type)
        bottoms += heights

    ax.set_ylabel("Proportion")
    ax.set_xlabel("Response")
    ax.set_title(f"{celltype_col} proportions\n(grouped by Response)")

    # reverse legend order to match top-bottom stack
    ordered_labels = cell_types[::-1]
    ordered_handles = [plt.Rectangle((0, 0), 1, 1, color=color_map[ct]) for ct in ordered_labels]
    ax.legend(ordered_handles, ordered_labels,
              bbox_to_anchor=(1.05, 1), loc='upper left',
              title='Cell Type', frameon=False)

    plt.tight_layout()
    output_path = f"{output_dir}/{celltype_col}_stacked_proportions_by_response_{filename_suffix}.png"
    plt.savefig(output_path, dpi=300)
    plt.close()

# plot cell type proportion by response
def plot_proportion_boxplot(
    proportion_dfs,
    proportion_sig_results,
    celltype_col,
    output_dir,
    filename_suffix="wilcoxon"
):

    proportion_df = proportion_dfs[celltype_col]
    sig_df = proportion_sig_results.get(celltype_col, None)

    # drop nas (just in case)
    proportion_df = proportion_df.dropna(subset=["pct", "Response"])

    # get all cell types that are not the current context
    cell_types = sorted([ct for ct in proportion_df[celltype_col].unique()])

    # setting up subplots (= no of cell types)
    n_cells = len(cell_types)
    n_cols = 4
    n_rows = math.ceil(n_cells / n_cols)
    fig, axes = plt.subplots(
        n_rows, n_cols,
        figsize=(n_cols * 4, n_rows * 3),
        sharey=False  # independent y-axis scaling per subplot
    )
    axes = axes.flatten()
    fig.suptitle(f"{celltype_col} proportions (grouped by Response)", fontsize=16)

    colors = {"Yes": "#66c2a5", "No": "#fc8d62"}  # yes green, no orange

    for idx, cell_type in enumerate(cell_types):
        ax = axes[idx]

        # subset to current cell type
        sub_df = proportion_df[proportion_df[celltype_col] == cell_type]

        groups = ["Yes", "No"]  # group by response
        data = [sub_df[sub_df["Response"] == g]["pct"].values for g in groups]

        # filter out empty or all-NaN data groups
        valid_data = []
        valid_positions = []
        valid_colors = []
        valid_group_labels = []

        for i, group_data in enumerate(data):
            if len(group_data) == 0 or np.all(np.isnan(group_data)):
                print(f"Skipping empty or NaN-only group '{groups[i]}' for cell type '{cell_type}'")
            else:
                valid_data.append(group_data)
                valid_positions.append(i)
                valid_colors.append(colors[groups[i]])
                valid_group_labels.append(groups[i])

        if len(valid_data) == 0:
            # no valid data for this cell type, skip plotting
            ax.set_visible(False)
            continue

        # boxplot with valid data
        box = ax.boxplot(
            valid_data,
            positions=valid_positions,
            widths=0.6,
            patch_artist=True,
            showfliers=True
        )

        # color boxes
        for patch, color in zip(box['boxes'], valid_colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.6)

        # median lines: black dotted
        for median_line in box['medians']:
            median_line.set_color('black')
            median_line.set_linestyle('dotted')
            median_line.set_linewidth(1.5)

        # scatter points with jitter for valid groups
        for i, group_data in zip(valid_positions, valid_data):
            x = np.random.normal(i, 0.08, size=len(group_data))
            ax.scatter(x, group_data, color='black', alpha=0.7, s=20, edgecolor='none')

        ax.set_xticks(valid_positions)
        ax.set_xticklabels(valid_group_labels)
        ax.set_title(cell_type, fontsize=10)

        ax.set_ylabel("Proportion")
        ax.set_xlabel("Response")

        # autoscale y-axis with padding
        if len(sub_df) > 0:
            y_min = sub_df["pct"].min()
            y_max = sub_df["pct"].max()
            y_range = y_max - y_min if y_max != y_min else 1
            pad_bottom = y_range * 0.15
            pad_top = y_range * 0.3  # more padding on top for stars
            ax.set_ylim(y_min - pad_bottom, y_max + pad_top)

        # add significance stars
        if sig_df is not None:
            sig_row = sig_df[sig_df[celltype_col] == cell_type]
            if not sig_row.empty:
                pval = sig_row["pval"].values[0]
                if pval < 0.001:
                    stars = "***"
                elif pval < 0.01:
                    stars = "**"
                elif pval < 0.05:
                    stars = "*"
                else:
                    stars = ""

                if stars:
                    y_pos = y_max + pad_top * 0.5
                    ax.text(0.5, y_pos, stars, ha='center', va='bottom', fontsize=14, color='red')

    # remove unused axes
    for j in range(n_cells, len(axes)):
        fig.delaxes(axes[j])

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.subplots_adjust(top=0.9)

    output_path = f"{output_dir}/{celltype_col}_proportion_comparison_{filename_suffix}.png"
    plt.savefig(output_path)
    plt.close()

if __name__ == "__main__":

    #--------------------------------
    # LOAD JSON
    #--------------------------------
    # load all_proportion_dfs from json
    with open(all_proportion_dfs_path, 'r') as f:
        all_proportion_dfs_loaded = json.load(f)

    # store converted dfs
    all_proportion_dfs = defaultdict(pd.DataFrame)

    # print structure
    print("all_proportion_dfs")
    for celltype_col, records in all_proportion_dfs_loaded.items():
        df = pd.DataFrame(records)
        all_proportion_dfs[celltype_col] = df
        print(f"  └── {celltype_col:<25} → DataFrame shape: {df.shape}")

    #--------------------------------
    # SIGNIFICANCE TESTING
    #--------------------------------
    proportion_sig_results = {}
    method="wilcoxon"

    print()
    print(f"\nPerforming significance testing using {method}...")
    for celltype_col in celltype_cols:
        print(f"\n{celltype_col}")
        sig_df = compare_proportions_sig(all_proportion_dfs[celltype_col], celltype_col, method=method)
        sig_rows = sig_df[sig_df["pval"] < 0.05]
        
        if sig_rows.shape[0] > 0:
            print(f"{len(sig_rows)} significant differences")
            print(sig_rows)
            print()
        else:
            print(f"No significant differences")

        proportion_sig_results[celltype_col] = sig_df
        sigdiff_output_csv_path = os.path.join(sigdiff_output_dir, f"{celltype_col}_proportions_{method}.csv")
        proportion_sig_results[celltype_col].to_csv(sigdiff_output_csv_path, index=False)

    #--------------------------------
    # PLOTTING
    #--------------------------------
    for celltype_col in celltype_cols:
        print(celltype_col)
        # bar plot
        print(" > Plotting stacked bar plot")
        plot_stacked_proportions_by_response(
            all_proportion_dfs[celltype_col],
            celltype_col,
            cell_type_colors,
            output_dir=plots_output_dir,
            filename_suffix=method
        )
        # bar plot
        print(" > Plotting box plot")
        plot_proportion_boxplot(
            all_proportion_dfs,
            proportion_sig_results,
            celltype_col,
            output_dir=plots_output_dir,
            filename_suffix=method
        )