import sys
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def gen_heatmap(matrix_path, cell_types_df_path, save_path, channel_names):
    matrix = np.load(matrix_path)
    print(matrix.shape)
    cell_types_df = pd.read_csv(cell_types_df_path)
    print(cell_types_df.shape)

    cell_types = cell_types_df['cell_type'].values
    cell_types = cell_types[cell_types != 'Artifact']
    print(cell_types.shape)

    assert matrix.shape[0] == cell_types.shape[0], "Matrix and cell types do not have the same number of rows"

    unique_cell_types = np.unique(cell_types)
    print(unique_cell_types)

    custom_order = [
        'Tumor cells',
        'Endothelial cells',
        'Neutrophils',
        'Cytotoxic T cells',
        'Helper T cells',
        'T cells (other)',
        'B cells',
        'Macrophages (CD163-)',
        'Macrophages (CD163+)',
        'Stromal cells (undefined)'
        ]
    
    unique_cell_types_ordered = sorted(unique_cell_types, key=lambda x: custom_order.index(x))

    heatmap_df = pd.DataFrame(index=unique_cell_types_ordered, columns=channel_names)

    for cell_type in unique_cell_types:
        indices = np.where(cell_types == cell_type)[0]
        mean_values = matrix[indices].mean(axis=0)
        heatmap_df.loc[cell_type] = mean_values
    
    heatmap_df = heatmap_df.astype(float)
    channels = ['Ecadherin', 'CD31', 'MPO', 'CD3e', 'CD8', 'CD4', 'CD20', 'CD68', 'CD163']
    filtered_df = heatmap_df.loc[:, channels]
    # Normalize each row separately
    #filtered_df_normalized = filtered_df.apply(lambda x: (x - x.min()) / (x.max() - x.min()), axis=1)
    #filtered_df_normalized = pd.concat([filtered_df_normalized, filtered_df.iloc[10:]])
    
    plt.figure(figsize=(12, 10))
    heatmap = sns.heatmap(filtered_df, annot=False, fmt=".2f", cmap='coolwarm', 
                              cbar=True, cbar_kws={'label': 'Normalized Mean Biomarker Expression'})
        
        # Set the colorbar label font size
    colorbar = heatmap.collections[0].colorbar
    colorbar.ax.yaxis.label.set_size(16)
    plt.title('Mean Biomarker Expression Per Cell Type', fontsize=20)
    plt.xlabel('Biomarker', fontsize=18)
    plt.xticks(fontsize=16, rotation=45)
    plt.yticks(fontsize=16)
    plt.ylabel('Cell Type', fontsize=18)
    plt.tight_layout()
    plt.savefig(os.path.join(save_path, 'celltypes_heatmap.png'))
    plt.clf()
    print('Heatmap saved to:', os.path.join(save_path, 'celltypes_heatmap.png'))

out_dir = '/gpfs/data/proteomics/projects/Endometrial_mIF/EC_codeximaging_results/out_11-14-24'
cell_types_dir = 'cell_types/27_clusters'

matrix_path = os.path.join(out_dir, 'normalized_matrix/matrix_normal_filtered_markers.npy')
cell_types_path = os.path.join(out_dir, cell_types_dir, 'cell_types.csv')
channel_names =  ['DAPI', 'MPO', 'Ecadherin', 'CD163', 'CD4', 'CD68', 'CD8', 'CD20', 'CD31', 'CD3e']
save_path = os.path.join(out_dir, cell_types_dir)
gen_heatmap(matrix_path, cell_types_path, save_path, channel_names)