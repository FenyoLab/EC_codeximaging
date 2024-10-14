import os
import sys
import numpy as np
import pandas as pd
from src.omero_tables.create_omero_table import create_omero_table

def biomarker_mean_tables(segmentation_data_dir, channel_names, omero_dict, save_dir, table_name = 'raw_biomarker_means'):

    matrix = np.load(os.path.join(segmentation_data_dir, 'matrix.npy'))
    cell_sample_names = np.load(os.path.join(segmentation_data_dir, 'cell_sample_names.npy'))
    
    unique_samples = np.unique(cell_sample_names)

    for sample in unique_samples:
        os.makedirs(os.path.join(save_dir, sample), exist_ok =True)
        table_path = os.path.join(save_dir, sample, f'{table_name}.csv')
        if os.path.exists(table_path):
            print(f'Omero table of biomarker means already saved for sample {sample}')
            continue

        print(f'Processing {sample}')

        sample_indices = np.where(cell_sample_names == sample)
        sample_matrix = matrix[sample_indices]
        
        sample_matrix_df = pd.DataFrame(sample_matrix, columns = channel_names)
        roi_value = omero_dict.get(sample, {}).get('roi_id')
        
        omero_df = create_omero_table(sample_matrix_df, roi_value)
        print(omero_df.head())

        omero_df.to_csv(table_path, index = False)
        print(f'Omero table of biomarker means saved for sample {sample}')

if __name__ == "__main__":
    main()