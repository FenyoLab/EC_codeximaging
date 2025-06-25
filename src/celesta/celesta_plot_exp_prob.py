import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import argparse
import os
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

exp_prob_csv_path = f"{results_dir}/{project_title}/{project_title}_marker_exp_prob.csv"
save_path = f"{results_dir}/{project_title}/plot_exp_prob"
if not os.path.exists(save_path):
    os.makedirs(save_path)

def plot_exp_prob(df, x_col='X', y_col='Y', marker_cols=None,
                  breaks=[-np.inf, 0.5, 0.6, 0.7, 0.8, 0.9, np.inf],
                  labels=["≤0.5", ">0.5", ">0.6", ">0.7", ">0.8", ">0.9"],
                  colors=[
                        "#333333",  # Dark gray
                        "#6A00A8",  # purple
                        "#B12A90",  # magenta
                        "#E16462",  # coral
                        "#FCA636",  # orange
                        "#F0F921",  # yellow
                  ],
                  point_size=1.5, 
                  title_prefix="Expression probability of ",
                  save_path="./plots"):
    """
    Plots binned expression levels for each marker in a given DataFrame.
    """

    # auto-detect marker columns if not given
    if marker_cols is None:
        marker_cols = [col for col in df.columns if col not in [x_col, y_col]]

    color_map = dict(zip(labels, colors))

    for marker in marker_cols:
        # prepare plotting df
        plot_df = df[[x_col, y_col]].copy()
        expr_vals = df[marker]
        
        # bin expression values
        plot_df["expr_bin"] = pd.cut(expr_vals, bins=breaks, labels=labels, right=True)
        plot_df["expr_bin"] = pd.Categorical(plot_df["expr_bin"], categories=labels, ordered=True)

        # drop NA
        plot_df = plot_df.dropna(subset=["expr_bin"])

        # sort to draw higher bins later (on top)
        plot_df = plot_df.sort_values("expr_bin")

        # plot
        plt.figure(figsize=(18, 16), facecolor='black')
        ax = plt.gca()
        # fig, ax = plt.subplots(figsize=figsize, facecolor='black')
        ax.set_facecolor('black')

        ax.invert_yaxis()  # match mIF spatial orientation

        # points
        plt.scatter(
            plot_df[x_col], plot_df[y_col],
            c=plot_df["expr_bin"].map(color_map),
            s=point_size, edgecolors='none'
        )

        # title
        plt.title(f"{title_prefix}{marker}", fontsize=24, color='white')

        # axes formatting
        plt.tick_params(axis='both', colors='white', labelsize=16)
        for spine in ax.spines.values():
            spine.set_edgecolor('white')

        # legend handles
        handles = [
            mpatches.Patch(color=color_map[cat], label=cat)
            for cat in plot_df["expr_bin"].cat.categories
        ]

        # legend outside plot (right side)
        legend = plt.legend(
            handles=handles,
            title="Probability",
            loc='upper left',
            bbox_to_anchor=(1.05, 1),
            frameon=False,
            title_fontsize=18,
            fontsize=16,
            markerscale=10,
            handletextpad=0.5,
            borderpad=0.5,
            labelcolor='white'
        )
        legend.get_title().set_color('white')

        # save
        plt.tight_layout()
        out_path = os.path.join(save_path, f"{marker}_exp_prob.png")
        plt.savefig(out_path, dpi=300, bbox_inches='tight')
        plt.close()


if __name__ == "__main__":
    print("------------------------------------")
    print("Project title:", project_title)
    print("Plotting expression probability for:", exp_prob_csv_path)
    print("------------------------------------")

    df = pd.read_csv(exp_prob_csv_path)
    plot_exp_prob(df, x_col='Y', y_col='X', save_path=save_path)

    print("Done. Plots saved to:", save_path)