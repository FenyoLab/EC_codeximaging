import os
import random
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns


def gen_boxplots(clinical_0, clinical_1, samples_0, samples_1, clinical_var,
                 proportion_type, region, sample_label, pval, effect_size,
                 boxplot_output_dir, add_color_points_stage, clinical_df,
                 figure_name, title_font_size, subtitle_font_size, y_tick_font_size,
                 x_tick_font_size, p_value_tick_font_size, x_tick_labels_dict,
                 y_axis_label_param, boxplot_shapes, plot_title_param=None,
                 sub_title_param=None, add_plot_title=False, range_0_1=False):
    """
    Generate and save a boxplot comparing two clinical groups.

    Parameters
    ----------
    clinical_0, clinical_1 : array-like
        Proportion/metric values for group 0 and group 1.
    samples_0, samples_1 : array-like
        Sample IDs corresponding to each group.
    clinical_var : str
        Name of the clinical variable being compared.
    proportion_type : str
        Label for the proportion metric (used in file naming).
    region : str
        Tissue region ('intra', 'peri', or 'whole_tissue').
    pval : float
        Mann-Whitney U p-value to display on plot.
    effect_size : float
        Median difference between groups.
    boxplot_output_dir : str
        Directory to save the output figure.
    add_color_points_stage : bool
        If True, color individual data points by tumor stage.
    range_0_1 : bool
        If True, constrain y-axis to [0, 1] range (for proportions).
    """
    plt.figure(figsize=(6, 6))

    all_proportions = np.concatenate([clinical_0, clinical_1]).flatten()
    df = pd.DataFrame({
        'slide_id': np.concatenate([samples_0, samples_1]),
        'proportion_cells': all_proportions,
        'clinical_var': [0] * len(samples_0) + [1] * len(samples_1)
    })

    df = df.dropna(subset=['proportion_cells'])
    if df.empty:
        print(f'Skipping boxplot: no valid data for {figure_name}')
        return

    ax = sns.boxplot(
        data=df, x='clinical_var', y='proportion_cells',
        linewidth=1.2, fliersize=0,
        boxprops=dict(edgecolor='black', facecolor='none', linewidth=1.2),
        medianprops=dict(color='black', linewidth=2),
        whiskerprops=dict(color='black'),
        capprops=dict(color='black'),
        zorder=1, width=0.7
    )

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_linewidth(1.5)
    ax.spines['left'].set_linewidth(1.5)

    max_val = df['proportion_cells'].max()
    min_val = df['proportion_cells'].min()

    if add_color_points_stage:
        if 'Stage' not in df.columns:
            df = df.merge(clinical_df[['slide_id', 'Stage']], on='slide_id', how='left')
        df['Stage'] = df['Stage'].astype(str)
        stage_colors = {'0': '#1B9E77', '1': '#9E3D9E'}

        sns.stripplot(
            data=df, x='clinical_var', y='proportion_cells',
            hue='Stage', palette=stage_colors,
            jitter=True, marker=boxplot_shapes[clinical_var],
            size=12, dodge=False, alpha=0.8
        )
        legend_handles = [
            mpatches.Patch(color='#1B9E77', label='Stage: Low'),
            mpatches.Patch(color='#9E3D9E', label='Stage: High')
        ]
        ax.legend(handles=legend_handles, loc='upper right', fontsize=10, title_fontsize=8)

    else:
        sns.stripplot(
            data=df[df['clinical_var'] == 0],
            x='clinical_var', y='proportion_cells',
            jitter=True, marker=boxplot_shapes[clinical_var],
            edgecolor='black', facecolor='none',
            linewidth=1.5, size=12, zorder=3
        )
        sns.stripplot(
            data=df[df['clinical_var'] == 1],
            x='clinical_var', y='proportion_cells',
            jitter=True, alpha=0.9,
            marker=boxplot_shapes[clinical_var],
            color='black', size=12, zorder=2
        )

    ax.set_xlim(-0.5, 1.5)

    if sample_label:
        for i, row in df.iterrows():
            if not pd.isna(row['proportion_cells']) and row['proportion_cells'] >= 0:
                x = 0 if row['clinical_var'] == 0 else 1
                jitter_x = x + (random.uniform(-0.1, 0.1))
                jitter_y = row['proportion_cells'] + (
                    random.uniform(-0.02, 0.02) * (df['proportion_cells'].max() - df['proportion_cells'].min())
                )
                plt.text(jitter_x, jitter_y, row['slide_id'], fontsize=8, ha='center', va='bottom')

    if range_0_1:
        range_val = max_val - min_val
        pad = 0.1 * range_val
        max_val_param = min(1, max_val + pad) if max_val <= 1 else max_val + pad
        min_val_param = max(0, min_val - pad) if min_val >= 0 else min_val - pad
        ax.set_ylim(min_val_param, max_val_param)

    y_min, y_max = ax.get_ylim()
    ax.set_ylim(y_min, y_max + 0.15 * (y_max - y_min))

    yticks = np.linspace(y_min, y_max, 5)
    ax.set_yticks(yticks)
    tick_diff = np.diff(yticks).min()
    decimals = 3 if tick_diff < 0.01 else 2 if tick_diff < 0.1 else 1
    ax.set_yticklabels([f"{v:.{decimals}f}" for v in yticks], fontsize=y_tick_font_size)

    plt.ylabel(y_axis_label_param if y_axis_label_param is not None else proportion_type,
               fontsize=y_tick_font_size)
    plt.xticks([0, 1], x_tick_labels_dict[clinical_var], fontsize=x_tick_font_size)
    plt.yticks(fontsize=y_tick_font_size)
    plt.xlabel('')

    if add_plot_title and plot_title_param is not None:
        ax.set_title(plot_title_param, fontsize=title_font_size, pad=12)
        if sub_title_param is not None:
            ax.text(0.5, 1.02, sub_title_param, transform=ax.transAxes,
                    fontsize=subtitle_font_size, ha='center')

    # P-value bracket
    if pval is not None and not np.isnan(pval):
        x1, x2 = 0, 1
        y_min, y_max = ax.get_ylim()
        y = max_val + 0.05 * (y_max - y_min)
        ax.plot([x1, x2], [y, y], lw=1.5, c='black')

        if pval < 1e-4:
            p_text = "p < 1e-4"
        elif clinical_var == 'IO response':
            p_text = f"Effect size = {effect_size:.3g}"
        else:
            p_text = f"p = {pval:.3g}"

        ax.text((x1 + x2) * 0.5, y + 0.01 * (y_max - y_min),
                p_text, ha='center', va='bottom', fontsize=p_value_tick_font_size)

    mpl.rcParams['pdf.fonttype'] = 42
    mpl.rcParams['ps.fonttype'] = 42

    os.makedirs(boxplot_output_dir, exist_ok=True)
    plot_name = f'{figure_name}_stage_colored' if add_color_points_stage else figure_name
    suffix = 'labeled' if sample_label else 'unlabeled'
    plt.savefig(os.path.join(boxplot_output_dir, f'{plot_name}_{suffix}.png'),
                bbox_inches='tight', dpi=300)
    plt.close()
