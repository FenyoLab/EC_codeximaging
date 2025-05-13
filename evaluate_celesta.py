import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from sklearn.metrics import classification_report, precision_score, recall_score, f1_score, confusion_matrix
import argparse
import os

#----------------------------------------
### PARSE ARGUMENTS
#----------------------------------------
#  arg parsing
parser = argparse.ArgumentParser(description='Evaluating CELESTA results with ground truth.')
parser.add_argument('--project_title', type=str, default="evaluate_celesta", help='Project title')
parser.add_argument('--celesta_results', type=str, default=None, help='CSV file containing celesta results')
parser.add_argument('--metadata', type=str, default=None, help='CSV file containing metadata with ground truth labels')
parser.add_argument('--output_dir', type=str, default=None, help='Tumor type to restrict the analysis to')
args = parser.parse_args()

# set dirs
data_dir = "/gpfs/data/courses/aio2025/yb2612/data/musical"
results_dir = "/gpfs/data/courses/aio2025/yb2612/results/musical_models"
model_path = f"{results_dir}/{args.project_title}.pkl"

print("------------------------------------")
print("Project title:", args.project_title)
print(f"Using {args.project_title} model with restriction {args.tumor_type}.")
print("------------------------------------")


#----------------------------------------
### DEFINE FUNCTIONS
#----------------------------------------

#---------------------------------
# LOAD CELESTA RESULTS
#---------------------------------
def load_celesta_results(results_csv, metadata_csv, replace_unknown=False):

    # load data
    celesta_df = pd.read_csv(results_csv)  # celesta results
    metadata = pd.read_csv(metadata_csv)  # metadata with ground truth labels

    # match X and Y cols
    celesta_df[['X', 'Y']] = celesta_df[['X', 'Y']].round(6)
    metadata[['absolute_x', 'absolute_y']] = metadata[['absolute_x', 'absolute_y']].round(6)
    metadata.rename(columns={'absolute_x': 'X', 'absolute_y': 'Y'}, inplace=True)

    # merge on X and Y columns
    celesta_df = pd.merge(celesta_df, metadata[['X', 'Y', 'cell_type']], on=['X', 'Y'], how='left')
    celesta_df.rename(columns={'Final cell type':'celesta_cell_type', 'cell_type':'manual_cell_type'}, inplace=True)

    # replace Unknown with "Stromal cells (undefined)"
    if replace_unknown==True:
        celesta_df['celesta_cell_type'] = celesta_df['celesta_cell_type'].replace("Unknown", "Stromal cells (undefined)")

    # order/remove duplicate cols
    columns_order = ['celesta_cell_type', 'manual_cell_type'] + [col for col in celesta_df.columns if col not in ['celesta_cell_type', 'manual_cell_type']]
    celesta_df = celesta_df[columns_order]
    celesta_df = celesta_df.loc[:, ~celesta_df.columns.duplicated()]

    # print cell types
    print("Manual cell types:\n")
    print(celesta_df["manual_cell_type"].value_counts())
    print("\nCelesta cell types:\n")
    print(celesta_df["celesta_cell_type"].value_counts())
    
    return celesta_df

#---------------------------------
# PLOT MATCH
#---------------------------------
def plot_match(df, include_cell_types=None, exclude_cell_types=["Artifact", "CD20+ and CD4+ cells"]):

    # Compute cell type counts
    counts = df['manual_cell_type'].value_counts().sort_values()
    cell_types = counts.index.tolist()

    # Filter based on inclusion/exclusion
    if include_cell_types is not None:
        cell_types = [ct for ct in cell_types if ct in include_cell_types]
    elif exclude_cell_types is not None:
        cell_types = [ct for ct in cell_types if ct not in exclude_cell_types]
        
    # Exclude specified manual cell types
    df_filtered = df[df['manual_cell_type'].isin(cell_types)].copy()
    
    # Add match column
    df_filtered['match'] = df_filtered['manual_cell_type'].astype(str) == df_filtered['celesta_cell_type'].astype(str)
    match_counts = df_filtered['match'].value_counts()
    
    # Calculate percentages
    total = match_counts.sum()
    percentages = (match_counts / total) * 100
    
    # Ensure "Match" (True) comes first, then "Mismatch" (False)
    match_counts = match_counts.sort_index(ascending=False)
    
    # Define colors
    colors = ['#28a745', '#d3d3d3']  # Match = green, Mismatch = light gray
    
    # Assign labels
    labels = [
        f'Match \n({match_counts.get(True, 0)}, {percentages.get(True, 0):.1f}%)',
        f'Mismatch \n({match_counts.get(False, 0)}, {percentages.get(False, 0):.1f}%)'
    ]
    
    # Create donut plot
    fig, ax = plt.subplots(figsize=(6, 6))
    wedges, texts, autotexts = ax.pie(match_counts, labels=labels, autopct='',
                                      startangle=90, wedgeprops={'width': 0.4}, colors=colors)
    
    ax.set_title("Match vs Mismatch (Excluding Specific Cell Types)", fontsize=14)
    plt.tight_layout()
    plt.show()

#---------------------------------
# PLOT CELL PROPORTIONS
#---------------------------------
def plot_cell_proportions(df, color_map=None, normalize=True):
    # Count values
    manual_counts = df['manual_cell_type'].value_counts()
    celesta_counts = df['celesta_cell_type'].value_counts()

    # All unique cell types (consistent order)
    all_cell_types = sorted(set(manual_counts.index) | set(celesta_counts.index))

    # Build aligned DataFrame
    counts_df = pd.DataFrame({
        'manual': [manual_counts.get(ct, 0) for ct in all_cell_types],
        'celesta': [celesta_counts.get(ct, 0) for ct in all_cell_types]
    }, index=all_cell_types)

    if normalize:
        counts_df = counts_df.div(counts_df.sum(axis=0), axis=1)

    # Colors
    if color_map is None:
        cmap = plt.cm.get_cmap('tab20', len(all_cell_types))
        color_map = {cell_type: cmap(i) for i, cell_type in enumerate(all_cell_types)}

    # Plot setup
    fig, ax = plt.subplots(figsize=(6, 10), facecolor='black')
    ax.set_facecolor('black')

    bottom_manual = 0
    bottom_celesta = 0

    for cell_type in all_cell_types:
        color = color_map.get(cell_type, 'gray')
        manual_val = counts_df.loc[cell_type, 'manual']
        celesta_val = counts_df.loc[cell_type, 'celesta']

        ax.bar('manual_cell_type', manual_val, bottom=bottom_manual,
               color=color, edgecolor='black', label=cell_type)
        ax.bar('celesta_cell_type', celesta_val, bottom=bottom_celesta,
               color=color, edgecolor='black')

        bottom_manual += manual_val
        bottom_celesta += celesta_val

    # White text for everything
    ax.set_ylabel('Proportion' if normalize else 'Count', color='white')
    ax.set_title('Cell Type Distribution: Manual vs Celesta', color='white')
    ax.tick_params(axis='x', colors='white')
    ax.tick_params(axis='y', colors='white')

    # White spines
    for spine in ax.spines.values():
        spine.set_edgecolor('white')

    # Deduplicated legend
    handles, labels = ax.get_legend_handles_labels()
    unique = dict(zip(labels, handles))
    legend = ax.legend(unique.values(), unique.keys(), bbox_to_anchor=(1.05, 1), loc='upper left',
                       title='Cell Type', frameon=False)
    plt.setp(legend.get_texts(), color='white')
    plt.setp(legend.get_title(), color='white')

    plt.tight_layout()
    plt.show()

#---------------------------------
# PLOT CELL ASSIGNMENTS
#---------------------------------
def plot_cell_assignments(
    df,
    x_col='X',
    y_col='Y',
    cell_type_col='manual_cell_type',
    cell_type_colors=None,
    base_layer='Stromal cells (undefined)',
    mid_layer='Tumor cells',
    include_cell_types=None,
    exclude_cell_types=None,
    title='Cell Type Distribution',
    alpha=0.7
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

    plt.figure(figsize=(10, 8), facecolor='black')
    ax = plt.gca()
    ax.set_facecolor('black')

    # Plot base layer first
    if base_layer in cell_types:
        subset = df[df[cell_type_col] == base_layer]
        plt.scatter(subset[x_col], subset[y_col], label=base_layer,
                    color='gray', s=10, alpha=alpha, zorder=1)
        cell_types.remove(base_layer)

    # Plot mid layer second
    if mid_layer in cell_types:
        subset = df[df[cell_type_col] == mid_layer]
        plt.scatter(subset[x_col], subset[y_col], label=mid_layer,
                    color=cell_type_colors.get(mid_layer, 'white'), s=10, alpha=alpha, zorder=2)
        cell_types.remove(mid_layer)

    # Plot remaining in descending count order
    for i, cell_type in enumerate(reversed(cell_types)):
        subset = df[df[cell_type_col] == cell_type]
        plt.scatter(subset[x_col], subset[y_col], label=cell_type,
                    color=cell_type_colors[cell_type], s=10, alpha=alpha, zorder=3+i)

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
    plt.show()

#---------------------------------
# EVALUATE CLASSIFICIATION
#---------------------------------
def evaluate_classification(df, true_col='manual_cell_type', pred_col='celesta_cell_type'):
    # Ensure categorical
    if not isinstance(df[true_col].dtype, pd.CategoricalDtype):
        df[true_col] = df[true_col].astype('category')

    class_names = df[true_col].cat.categories.tolist()
    y_true = df[true_col]
    y_pred = df[pred_col]

    # Classification report as text
    print("\n--- Classification Report ---")
    print(classification_report(y_true, y_pred, labels=class_names, zero_division=1))

    # Classification report as dict for plotting
    report = classification_report(y_true, y_pred, output_dict=True, zero_division=1)
    report_df = pd.DataFrame(report).T

    # Add overall accuracy row
    report_df.loc['overall'] = {
        'precision': precision_score(y_true, y_pred, average='weighted', zero_division=1),
        'recall': recall_score(y_true, y_pred, average='weighted', zero_division=1),
        'f1-score': f1_score(y_true, y_pred, average='weighted', zero_division=1),
        'support': len(y_true)
    }

    # Prepare for plotting
    metrics_to_plot = ['precision', 'recall', 'f1-score']
    plot_df = report_df.loc[class_names + ['overall'], metrics_to_plot]

    # Plot
    ax = plot_df.plot(kind='bar', figsize=(12, 6), colormap='viridis', edgecolor='black')
    plt.title("Classification Metrics by Cell Type (Including Overall)", fontsize=14)
    plt.ylabel("Score")
    plt.ylim(0, 1.05)
    plt.xticks(rotation=45, ha='right')
    plt.legend(title='Metric')
    plt.grid(axis='y', linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.show()

#---------------------------------
# PLOT CONFUSION MATRIX
#---------------------------------
def plot_normalized_confusion_matrix(df, true_col='manual_cell_type', pred_col='celesta_cell_type'):
    # Ensure categorical
    if not isinstance(df[true_col].dtype, pd.CategoricalDtype):
        df[true_col] = df[true_col].astype('category')

    class_names = df[true_col].cat.categories.tolist()
    y_true = df[true_col]
    y_pred = df[pred_col]

    # Confusion matrix
    conf_matrix = confusion_matrix(y_true, y_pred, labels=class_names)
    conf_matrix_normalized = conf_matrix.astype(float) / conf_matrix.sum(axis=1, keepdims=True)

    # Plot
    plt.figure(figsize=(10, 7))
    ax = sns.heatmap(
        conf_matrix_normalized, annot=True, fmt='.2f', cmap='Blues',
        xticklabels=class_names, yticklabels=class_names, cbar=True
    )

    # Highlight diagonal
    for i in range(len(class_names)):
        ax.add_patch(plt.Rectangle((i, i), 1, 1, fill=False, edgecolor='red', lw=2))

    plt.xlabel('Predicted', fontsize=12)
    plt.ylabel('True', fontsize=12)
    plt.title('Normalized Confusion Matrix', fontsize=14)
    plt.xticks(rotation=90)
    plt.yticks(rotation=0)
    plt.tight_layout()
    plt.show()

#---------------------------------
# DEFINE CELL TYPE COLORS
#---------------------------------
cell_type_colors = {
    'Artifact': '#888888',                     # medium gray
    'CD20+ and CD4+ cells': '#888888',          # medium gray
    'CD20+ and CD3e+ cells': '#888888',          # medium gray
    'Stromal cells (undefined)': '#A9A9A9',    # dark gray
    'Tumor cells': '#FF6347',                  # tomato red
    'Endothelial cells': '#FFFF00',            # yellow
    'Neutrophils': '#FFFFFF',                  # white
    'Macrophages (CD163-)': '#C71585',         # medium violet red (pinkish)
    'Macrophages (CD163+)': '#9370DB',         # medium purple
    'Cytotoxic T cells': '#DC143C',            # crimson
    'T cells (other)': '#228B22',              # forest green
    'Helper T cells': '#00FF7F',               # spring green (distinct)
    'B cells': '#1E90FF',                      # dodger blue
}

#----------------------------------------
### MAIN
#----------------------------------------

# load celesta results
df = load_celesta_results(
    "/gpfs/home/yb2612/yb2612_fenyo/results/celesta/endometrial_1T_raw_noarcsinh_initial/endometrial_1T_raw_noarcsinh_initial_final_cell_type_assignment.csv", 
    "/gpfs/home/yb2612/yb2612_fenyo/data/celesta/endometrial_test/metadata_1T.csv",
    replace_unknown=True)

#---------------------------------
# PLOT PROPORTION OF MATCHING CELLS
# overall
print("All cell types:")
plot_match(df, exclude_cell_types=["Artifact", "CD20+ and CD4+ cells"])

# common cell types
print("\nTumor, endothelial, stromal cells:")
plot_match(df, include_cell_types=["Tumor cells", "Stromal cells (undefined)", "Endothelial cells"], exclude_cell_types=["Artifact", "CD20+ and CD4+ cells"])

# rare cell types
print("\nRare cell types:")
plot_match(df, exclude_cell_types=["Tumor cells", "Stromal cells (undefined)", "Endothelial cells", "Artifact", "CD20+ and CD4+ cells"])
#---------------------------------

# classification report
evaluate_classification(df)

# confusion matrix
plot_normalized_confusion_matrix(df)

# plot cell proportions
plot_cell_proportions(df, color_map=cell_type_colors)

#---------------------------------
# PLOT CELL ASSIGNMENTS
# ground truth
plot_cell_assignments(
    df,
    cell_type_col='manual_cell_type',
    cell_type_colors=cell_type_colors
)
# celesta
plot_cell_assignments(
    df,
    cell_type_col='celesta_cell_type',
    cell_type_colors=cell_type_colors
)
#---------------------------------