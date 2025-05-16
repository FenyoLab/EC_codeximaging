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
args = parser.parse_args()

project_title = args.project_title
exp_prob_csv_path = f"{args.results_dir}/{project_title}/{project_title}_marker_exp_prob.csv"
save_path = f"{args.results_dir}/{project_title}/plot_exp_prob"
if not os.path.exists(save_path):
    os.makedirs(save_path)

def plot_exp_prob(df, x_col='X', y_col='Y', marker_cols=None,
                                   breaks=[-np.inf, 0.5, 0.6, 0.7, 0.8, 0.9, np.inf],
                                   labels=["≤0.5", ">0.5", ">0.6", ">0.7", ">0.8", ">0.9"],
                                   colors=[
                                      "#D3D3D3",  # Light gray
                                      "#E1B07A",  # Beige
                                      "#F1D302",  # Yellow
                                      "#FFB347",  # Light orange
                                      "#FF6F59",  # Coral red
                                      "#D32F2F",  # Dark red
                                  ],
                                   point_size=10.0, figsize=(6, 4), title_prefix="Expression of ",
                                   save_path=save_path):
    """
    Plots binned expression levels for each marker in a given DataFrame.
    """

    # Auto-detect marker columns if not given
    if marker_cols is None:
        marker_cols = [col for col in df.columns if col not in [x_col, y_col]]

    color_map = dict(zip(labels, colors))

    for marker in marker_cols:
        # Prepare the plotting DataFrame
        plot_df = df[[x_col, y_col]].copy()
        expr_vals = df[marker]
        
        # Bin the expression values
        plot_df["expr_bin"] = pd.cut(expr_vals, bins=breaks, labels=labels, right=True)
        plot_df["expr_bin"] = pd.Categorical(plot_df["expr_bin"], categories=labels, ordered=True)

        # Drop NA (from out-of-bin values or NaNs in expression)
        plot_df = plot_df.dropna(subset=["expr_bin"])

        # Sort to draw higher bins later (on top)
        plot_df = plot_df.sort_values("expr_bin")

        # Plot
        plt.figure(figsize=figsize)
        plt.scatter(plot_df[x_col], plot_df[y_col],
                    c=plot_df["expr_bin"].map(color_map),
                    s=point_size, edgecolors='none')
        
        plt.title(f"{title_prefix}{marker}", fontsize=10)
        
        # Create legend handles
        handles = [
            mpatches.Patch(color=color_map[cat], label=cat)
            for cat in plot_df["expr_bin"].cat.categories
        ]
        
        # Add legend outside plot (right side)
        plt.legend(
            handles=handles,
            title="Expression",
            loc='center left',
            bbox_to_anchor=(1.05, 0.5),
            fontsize=8,
            title_fontsize=9,
            frameon=True
        )
        
        # Show box (turn axis back on)
        plt.axis('on')
        
        # Optional: remove ticks but keep box
        plt.xticks([])
        plt.yticks([])
        
        plt.gca().set_aspect('equal')

        plt.savefig(f"{save_path}/{marker}_exp_prob.png", dpi=300, bbox_inches='tight')
        plt.close()

if __name__ == "__main__":
    print("------------------------------------")
    print("Project title:", project_title)
    print("Plotting expression probability for:", exp_prob_csv_path)
    print("------------------------------------")

    df = pd.read_csv(exp_prob_csv_path)
    plot_exp_prob(df, save_path=save_path)

    print("Done. Plots saved to:", save_path)