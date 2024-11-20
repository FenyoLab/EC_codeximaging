import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

data_path = '/gpfs/data/proteomics/projects/Endometrial_mIF/EC_codeximaging_results/out_11-14-24'
cell_types_dir = 'cell_types/27_clusters'

custom_colors = {
    'Tumor cells': 'skyblue',
    'Endothelial cells': 'yellow',
    'Neutrophils': 'orange',
    'Helper T cells': 'lightgreen',
    'Cytotoxic T cells': 'darkgreen',
    'T cells (other)': 'turquoise',
    'B cells': 'royalblue',
    'Macrophages (CD163-)': 'lightpink',
    'Macrophages (CD163+)': 'magenta',
    'Stromal cells (undefined)': 'lightgray',
}
custom_order = list(custom_colors.keys())

# Load the data
# Replace 'cell_types.csv' with your file path
df = pd.read_csv(os.path.join(data_path, cell_types_dir, 'cell_types.csv'), index_col=0)
print('Cell types shape:', df.shape)
df = df[df['cell_type'] != 'Artifact']
print('Cell types shape without Artifacts:', df.shape)

# Calculate proportions of cell types for each slide
proportions = df.groupby(['slide_id', 'cell_type']).size().unstack(fill_value=0)
proportions = proportions[custom_order]
proportions = proportions.div(proportions.sum(axis=1), axis=0)

# Set up the figure
fig, ax = plt.subplots(figsize=(10, 12))

# Define colors for each cell type
colors = plt.cm.tab10(np.linspace(0, 1, len(custom_order)))

# Create the stacked bar chart
left = np.zeros(len(proportions))
for cell_type, color in custom_colors.items():
    ax.barh(
        proportions.index, 
        proportions[cell_type], 
        left=left, 
        color=color, 
        label=cell_type
    )
    left += proportions[cell_type]

# Adjust the y-axis limits
ax.set_ylim(-0.5, len(proportions) - 0.5) 

# Add labels, legend, and title
ax.set_ylabel('Slide ID', fontsize=12)
ax.set_xlabel('Proportion', fontsize=12)
ax.set_title('Proportions of Cell Types by Slide', fontsize=16)
ax.legend(title='Cell Types', bbox_to_anchor=(1.05, 1), loc='upper left')

# Adjust layout
plt.tight_layout()

# Save the plot
plt.savefig(os.path.join(data_path, cell_types_dir, 'celltype_proportions_barchart.png'), dpi = 300)

# Show the plot
plt.show()