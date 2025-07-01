import math
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd 
import os
import json
from scipy.stats import ttest_ind, mannwhitneyu
from scipy.stats import linregress
from collections import defaultdict

# paths
all_pct_dfs_path = "/gpfs/data/proteomics/data/Cervical_mIF/output/seurat_objects/plots/dist_group_response_comparison_plots/dist_group_dfs.json"
output_dir = "/gpfs/data/proteomics/data/Cervical_mIF/output/seurat_objects/plots"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# variables
normalize_cols = ["dist_group"]
celltype_cols = ["Fine.cell.type", "Final.cell.type", "Parent.cell.type", "Grandparent.cell.type"]
distance_order=['Near', 'Peri', 'Far']

# colors
cell_type_colors_path = "../../config/color_palettes/fine_cell_type_colors.json"
with open(cell_type_colors_path, "r") as f:
    cell_type_colors = json.load(f)

# compute linear slopes
def compute_linear_slopes(df_long, celltype_col, distance_order=["Near", "Peri", "Far"]):
    """
    Compute linear slope of pct across distance_order per sample and cell type.
    
    Parameters:
    - df_long: DataFrame with columns ['orig.ident', celltype_col, 'dist_group', 'pct']
    - distance_order: list of ordered distance groups
    
    Returns:
    - slope_df: DataFrame with columns ['orig.ident', celltype_col, 'slope']
    """
    # ensure dist_group is ordered categorical
    df_long = df_long.copy()
    df_long['dist_group'] = pd.Categorical(df_long['dist_group'], categories=distance_order, ordered=True)
    
    slopes = []
    x = np.arange(len(distance_order))  # [0,1,2]

    # group by sample, cell type, response
    group_cols = ['orig.ident', celltype_col,'Response']
    grouped = df_long.groupby(group_cols)
    for group_keys, group in grouped:
        # reindex to ensure all distance points are present, fill missing with np.nan
        group = group.set_index('dist_group').reindex(distance_order).reset_index()
        y = group['pct'].values
        
        # if all y are nan or <2 points, skip
        if np.isnan(y).all() or np.sum(~np.isnan(y)) < 2:
            slope = np.nan
        else:            
            mask = ~np.isnan(y)  # use points where y is not nan
            slope, _, _, _, _ = linregress(x[mask], y[mask])  # slope, int, rval, pval
        
        result = dict(zip(group_cols, group_keys))
        result['slope'] = slope
        slopes.append(result)
        
    slope_df = pd.DataFrame(slopes) 
    return slope_df

# significance testing
def compare_slopes_sig(slope_df, celltype_col, method="wilcoxon"):
    """
    Compare slope distributions between 'Yes' and 'No' responses for each celltype_col
    
    Parameters:
    - slope_df: DataFrame with columns [celltype_col, 'Response', 'slope']
    - method: "ttest" or "wilcoxon"

    Returns:
    - result_df: DataFrame with columns:
        [celltype_col, 'n_Yes', 'n_No', 'mean_Yes', 'mean_No', 'pval']
    """
    results = []

    for cell_type, group in slope_df.groupby(celltype_col):
        # group slopes by response
        slopes_yes = group[group["Response"] == "Yes"]["slope"].dropna()
        slopes_no = group[group["Response"] == "No"]["slope"].dropna()

        # skip if not enough samples
        if len(slopes_yes) < 2 or len(slopes_no) < 2:
            pval = None
        elif method == "ttest":
            _, pval = ttest_ind(slopes_yes, slopes_no, equal_var=False)
        elif method == "wilcoxon":
            _, pval = mannwhitneyu(slopes_yes, slopes_no, alternative="two-sided")
        else:
            raise ValueError(f"Unsupported method: {method}")
            stat, pval = ttest_ind(slopes_yes, slopes_no, equal_var=False)

        results.append({
            celltype_col: cell_type,
            "n_Yes": len(slopes_yes),
            "n_No": len(slopes_no),
            "mean_Yes": slopes_yes.mean() if len(slopes_yes) > 0 else None,
            "mean_No": slopes_no.mean() if len(slopes_no) > 0 else None,
            "pval": pval
        })

    sig_df = pd.DataFrame(results)
    return sig_df

# slope boxplots
def plot_slope_by_response(
    slope_dfs,  # from compute_linear_slopes()
    slope_ttest_results,  # from compare_slopes_by_response()
    contexts,
    celltype_col,
    output_dir,
    filename_suffix="wilcoxon"
):
    for context in contexts:
        slope_df = slope_dfs[context]
        sig_df = slope_ttest_results.get(context, None)

        # Drop NaNs in critical columns just in case
        slope_df = slope_df.dropna(subset=["slope", "Response"])

        # get all cell types that are not the current context
        cell_types = sorted([ct for ct in slope_df[celltype_col].unique() if ct != context])

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
        fig.suptitle(f"Distance from {context} (grouped by Response)", fontsize=16)

        colors = {"Yes": "#66c2a5", "No": "#fc8d62"}  # yes green, no orange

        for idx, cell_type in enumerate(cell_types):
            ax = axes[idx]

            # subset to current cell type
            sub_df = slope_df[slope_df[celltype_col] == cell_type]

            groups = ["Yes", "No"]  # group by response
            data = [sub_df[sub_df["Response"] == g]["slope"].values for g in groups]

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

            ax.set_ylabel("Slope")
            ax.set_xlabel("Response")

            # autoscale y-axis with padding
            if len(sub_df) > 0:
                y_min = sub_df["slope"].min()
                y_max = sub_df["slope"].max()
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

        output_path = f"{output_dir}/{context}_slope_comparison_{filename_suffix}.png"
        plt.savefig(output_path)
        plt.show()
        plt.close()

if __name__ == "__main__":

    #--------------------------------
    # LOAD JSON
    #--------------------------------
    # load json
    with open(all_pct_dfs_path, 'r') as f:
        all_pct_dfs_loaded = json.load(f)

    # initialize nested structure
    all_pct_dfs = defaultdict(lambda: defaultdict(dict))

    # convert nested dicts to df
    for celltype_col, normalize_dict in all_pct_dfs_loaded.items():
        for normalize_col, context_dict in normalize_dict.items():
            for context, records in context_dict.items():
                # Convert list of dicts back to DataFrame
                df = pd.DataFrame(records)
                all_pct_dfs[celltype_col][normalize_col][context] = df

    # display tree
    for celltype_col, normalize_dict in all_pct_dfs.items():
        print(celltype_col)
        for normalize_col, context_dict in normalize_dict.items():
            print(f"  Normalized by: {normalize_col}")
            for context, df in context_dict.items():
                print(f"    └── Context: {context:<15} → DataFrame shape: {df.shape}")

    # compute slopes
    slope_dfs = {}
    print("\nComputing slopes...")
    for celltype_col in celltype_cols:
        print(f" > {celltype_col}")
        slope_dfs[celltype_col] = {}
        for normalize_col in normalize_cols:
            slopes_output_dir = os.path.join(output_dir, f"{normalize_col}_response_comparison_plots/{normalize_col}_slopes/slope_dfs/{celltype_col}")
            if not os.path.exists(slopes_output_dir):
                os.makedirs(slopes_output_dir)
            # get contexts
            contexts = list(all_pct_dfs[celltype_col][normalize_col].keys())
            slope_dfs[celltype_col][normalize_col] = {}
            for context in contexts:
                slope_dfs[celltype_col][normalize_col][context] = compute_linear_slopes(all_pct_dfs[celltype_col][normalize_col][context], celltype_col)
                slope_dfs[celltype_col][normalize_col][context].to_csv(f"{slopes_output_dir}/{context}_slope_df.csv", index=False)

    # significance testing
    method="wilcoxon"
    slope_sig_results = {}
    print(f"\nPerforming significance testing using {method}...")
    for celltype_col in celltype_cols:
        print()
        print(celltype_col)
        slope_sig_results[celltype_col] = {}
        for normalize_col in normalize_cols:
            print(normalize_col)
            sigtest_output_dir = os.path.join(output_dir, f"{normalize_col}_response_comparison_plots/{normalize_col}_slopes/{method}_csv/{celltype_col}")
            if not os.path.exists(sigtest_output_dir):
                os.makedirs(sigtest_output_dir)
            print("Results will be saved to:", sigtest_output_dir)
            # get contexts
            contexts = list(all_pct_dfs[celltype_col][normalize_col].keys())
            slope_sig_results[celltype_col][normalize_col] = {}
            for context in contexts:
                sig_df = compare_slopes_sig(slope_dfs[celltype_col][normalize_col][context], celltype_col, method=method)
                sig_rows = sig_df[sig_df["pval"] < 0.05]
            
                if sig_rows.shape[0] > 0:
                    print(f"{context}: {len(sig_rows)} significant rows")
                    print(sig_rows)
                    print()
        
                slope_sig_results[celltype_col][normalize_col][context] = sig_df
                slope_sig_results[celltype_col][normalize_col][context].to_csv(f"{sigtest_output_dir}/{context}_slope_{method}.csv", index=False)

    # box plots
    print("\nGenerating box plots...")
    for celltype_col in celltype_cols:
        print(f" > {celltype_col}")
        for normalize_col in normalize_cols:
            print(f"  >> {normalize_col}")
            plots_output_dir = os.path.join(output_dir, f"{normalize_col}_response_comparison_plots/{normalize_col}_slopes/{celltype_col}")
            if not os.path.exists(plots_output_dir):
                os.makedirs(plots_output_dir)
            # get contexts
            contexts = list(all_pct_dfs[celltype_col][normalize_col].keys())
            plot_slope_by_response(
                slope_dfs[celltype_col][normalize_col],
                slope_sig_results[celltype_col][normalize_col],
                contexts,
                celltype_col,
                output_dir=plots_output_dir,
                filename_suffix=method
            )
            print(f"  >> All plots saved to {plots_output_dir}")