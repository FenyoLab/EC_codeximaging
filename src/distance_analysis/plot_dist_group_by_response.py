import math
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd 
import os
import json
from scipy.stats import ttest_ind, mannwhitneyu
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

# significance testing
def compare_dist_group_sig(context_dfs_long, contexts, celltype_col, method="wilcoxon", atol=1e-6):
    """
    Compute statistical tests comparing 'Yes' vs. 'No' responses at each distance and cell type per context.
    Skips test when groups are nearly identical or have zero variance.

    Parameters:
    - context_dfs_long: dict of DataFrames per context
    - contexts: list of context names
    - method: "ttest" (parametric) or "wilcoxon" (Mann-Whitney U, non-parametric)
    - atol: absolute tolerance for detecting near-identical distributions

    Returns:
    - Dict of DataFrames: context -> DataFrame with columns ['Fine.cell.type', 'dist_group', 'pval']
    """
    sig_df = {}

    for context in contexts:
        df = context_dfs_long[context]
        results = []

        for (cell, distance), group_df in df.groupby([celltype_col, 'dist_group'], observed=True):
            yes_vals = group_df[group_df['Response'] == 'Yes']['pct'].values
            no_vals = group_df[group_df['Response'] == 'No']['pct'].values

            if len(yes_vals) >= 2 and len(no_vals) >= 2:
                yes_std = np.std(yes_vals)
                no_std = np.std(no_vals)
                mean_diff = np.abs(np.mean(yes_vals) - np.mean(no_vals))

                if (yes_std < atol or no_std < atol or mean_diff < atol):
                    print(f"Skipping test for context={context}, cell={cell}, dist={distance}")
                    print(f"  YES group (n={len(yes_vals)}): mean={np.mean(yes_vals):.4f}, std={yes_std:.4e}, values={yes_vals.tolist()}")
                    print(f"  NO  group (n={len(no_vals)}): mean={np.mean(no_vals):.4f}, std={no_std:.4e}, values={no_vals.tolist()}")
                    print(f"  Mean difference: {mean_diff:.4e} | atol={atol}\n")
                    pval = np.nan
                else:
                    if method == "ttest":
                        _, pval = ttest_ind(yes_vals, no_vals, equal_var=False)
                    elif method == "wilcoxon":
                        _, pval = mannwhitneyu(yes_vals, no_vals, alternative="two-sided")
                    else:
                        raise ValueError(f"Unsupported method: {method}")
            else:
                print(f"Not enough data for context={context}, cell={cell}, dist={distance} — YES n={len(yes_vals)}, NO n={len(no_vals)}\n")
                pval = np.nan

            results.append({celltype_col: cell, 'dist_group': distance, 'pval': pval})

        sig_df[context] = pd.DataFrame(results)

    return sig_df

# line plots
def plot_pct_by_distance_and_response(
    context_dfs_long,
    contexts,
    celltype_col,
    distance_order=["Near", "Peri", "Far"],
    cell_type_colors=None,
    output_dir="./",
    figsize_per_plot=(4, 3),
    filename_suffix="avg_pct_per_sample",
    error_bars=False,
    indiv_traces=False,
    sig_df=None
):
    for context in contexts:
        df_long = context_dfs_long[context].copy()

        df_long["dist_group"] = pd.Categorical(df_long["dist_group"], categories=distance_order, ordered=True)
        df_long = df_long.sort_values([celltype_col, "Response", "dist_group"])

        # get all cell types that are not the current context
        cell_types = sorted([ct for ct in df_long[celltype_col].unique() if ct != context])

        # setting up subplots (= no of cell types)
        n_cells = len(cell_types)
        n_cols = 4
        n_rows = math.ceil(n_cells / n_cols)

        fig, axes = plt.subplots(
            n_rows, n_cols,
            figsize=(n_cols * figsize_per_plot[0], n_rows * figsize_per_plot[1]),
            sharex=True
        )
        axes = axes.flatten()
        fig.suptitle(f"Distance from {context} (grouped by Response)", fontsize=16)

        legend_handles = {}

        for idx, cell_type in enumerate(cell_types):
            ax = axes[idx]
            for response, linestyle in zip(["Yes", "No"], ["solid", "dotted"]):
                # get subset of df: current cell type and response
                subset = df_long[(df_long[celltype_col] == cell_type) & (df_long["Response"] == response)]

                x_vals = np.arange(len(distance_order))
                color = cell_type_colors.get(cell_type, "#cccccc") if cell_type_colors else "#cccccc"

                # PLOT INDIVIDIUAL TRACES
                if indiv_traces:
                    # group subset by sample
                    for _, sample_df in subset.groupby("orig.ident"):
                        # arrange rows acc to dist_group and then reset index
                        sample_df = sample_df.set_index("dist_group").reindex(distance_order).reset_index()
                        y = sample_df["pct"].values  # indiv trace
                        ax.plot(x_vals, y, color=color, linestyle=linestyle, alpha=0.5, linewidth=1, zorder=1)  # plot
                
                # PLOT T-TEST RESULTS
                if sig_df is not None:
                    sig_df = sig_df.get(context)
                    if sig_df is not None:
                        sig_subset = sig_df[sig_df[celltype_col] == cell_type]
                        for i, dist in enumerate(distance_order):
                            pval = sig_subset[sig_subset['dist_group'] == dist]['pval']
                            if not pval.empty and pval.iloc[0] < 0.05:
                                ax.axvline(x=i, color='red', linestyle='--', linewidth=1.5, zorder=0)
                
                # PLOT ERROR BARS
                # group data by dist, compute mean and sem
                grouped = subset.groupby("dist_group", observed=True)["pct"]
                mean_vals = grouped.mean().reindex(distance_order).values
                sem_vals = grouped.sem().reindex(distance_order).values
                if error_bars:  # plot shaded error bars
                    ax.fill_between(  
                        x_vals,
                        mean_vals - sem_vals,
                        mean_vals + sem_vals,
                        color=color,
                        alpha=0.3,
                        zorder=2
                    )

                # PLOT LINES BETWEEN POINTS
                line, = ax.plot(
                    x_vals,
                    mean_vals,
                    label=response,
                    color=color,
                    linestyle=linestyle,
                    marker="o",
                    linewidth=2,
                    zorder=3
                )

                # add legend entry once per response
                if idx == 0 and response not in legend_handles:
                    legend_handles[response] = line

            # plot settings
            ax.set_title(cell_type, fontsize=10)
            ax.set_xticks(x_vals)
            ax.set_xticklabels(distance_order)
            ax.set_ylabel("Proportion")
            ax.set_xlabel("Distance")
            ax.tick_params(labelbottom=True)

        # remove unused axes
        for j in range(len(cell_types), len(axes)):
            fig.delaxes(axes[j])

        # add legend in upper right corner
        fig.legend(
            handles=[legend_handles[r] for r in ["Yes", "No"] if r in legend_handles],
            labels=[r for r in ["Yes", "No"] if r in legend_handles],
            loc="upper right",
            fontsize=12,
            title="Response",
            title_fontsize=13
        )

        # plot and save fig
        plt.tight_layout(rect=[0, 0, 0.95, 0.97])
        output_path = f"{output_dir}/{context}_{filename_suffix}.png"
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

    for celltype_col in celltype_cols:
        print()
        print("-"*50)
        print(celltype_col)
        print("-"*50)
    
        for normalize_col in normalize_cols:
            print(normalize_col)

            # get contexts
            contexts = list(all_pct_dfs[celltype_col][normalize_col].keys())
        
            # significance testing
            method="wilcoxon"
            sigtest_results = compare_dist_group_sig(all_pct_dfs[celltype_col][normalize_col], contexts, celltype_col, method=method)
            sigtest_output_dir = os.path.join(output_dir, f"{normalize_col}_response_comparison_plots/{normalize_col}_proportions/{method}_csv/{celltype_col}")
            if not os.path.exists(sigtest_output_dir):
                os.makedirs(sigtest_output_dir)
            print(f" > Performing significance testing using {method}...")
            print(f" > All results saved to {sigtest_output_dir}\n")
            
            for context in contexts:
                sig_df = sigtest_results[context]
                sigtest_results[context].to_csv(f"{sigtest_output_dir}/{context}_avg_pct_by_{normalize_col}_{method}.csv", index=False)
                sig_rows = sig_df[sig_df["pval"] < 0.05]

                # print significant results
                if sig_rows.shape[0] > 0:
                    print(f"{context}: {len(sig_rows)} significant rows")
                    print(sig_rows)
                    print()
        
            # line plot
            plots_output_dir = os.path.join(output_dir, f"{normalize_col}_response_comparison_plots/{normalize_col}_proportions/{celltype_col}")
            if not os.path.exists(plots_output_dir):
                os.makedirs(plots_output_dir)
            print(f" > Plotting {normalize_col} proportions by distance and response...")
            plot_pct_by_distance_and_response(
                all_pct_dfs[celltype_col][normalize_col],
                contexts,
                celltype_col,
                distance_order,
                cell_type_colors,
                output_dir=plots_output_dir,
                filename_suffix=f"avg_pct_by_{normalize_col}_errorbars_{method}",
                error_bars=True,
                indiv_traces=False,
                sig_df=sigtest_results
            )
            print(f" > All plots saved to {plots_output_dir}")