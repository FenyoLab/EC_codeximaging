import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from types import SimpleNamespace
sys.path.append('/gpfs/home/as18894/projects/as18894/FenyoLab/Endometrial/EC_codeximaging')
from utils import helper

def main():
    #import config
    config_yaml= 'barcharts.yaml'
    run_config = helper.load_yaml_file(config_yaml)
    config = SimpleNamespace(**run_config)

    celltype_barchart(cell_types_dir = config.cell_types_dir, custom_colors_dict = config.custom_colors)

def celltype_barchart(cell_types_dir, custom_colors_dict):
    #Load the cell types data
    cell_types = pd.read_csv(os.path.join(cell_types_dir, 'cell_types_visuals.csv'), index_col=0)
    cell_types = cell_types[cell_types['cell_type_visuals'] != 'Artifact'] #remove artifacts

    #cell types ordered for visualization
    custom_order = list(custom_colors_dict.keys())

    #Calculate proportions of cell types for each slide
    proportions = cell_types.groupby(['slide_id', 'cell_type_visuals']).size().unstack(fill_value=0)
    proportions = proportions.iloc[::-1]
    proportions = proportions[custom_order]
    proportions = proportions.div(proportions.sum(axis=1), axis=0)

    fig, ax = plt.subplots(figsize=(12, 10))

    # Define colors for each cell type
    colors = plt.cm.tab10(np.linspace(0, 1, len(custom_order)))

    # Create the stacked bar chart
    left = np.zeros(len(proportions))
    for cell_type, color in custom_colors_dict.items():
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
    ax.set_ylabel('Slide ID', fontsize=14)
    ax.set_xlabel('Proportion', fontsize=14)
    ax.set_title('Cell Type Proportions Per Slide', fontsize=16)
    ax.legend(title='Cell Types', bbox_to_anchor=(1.05, 1), loc='upper left', fontsize = 14)
    
    plt.tight_layout()
    plt.savefig(os.path.join(cell_types_dir, 'figures/celltype_barchart.png'), dpi = 300)

if __name__ == "__main__":
    main()