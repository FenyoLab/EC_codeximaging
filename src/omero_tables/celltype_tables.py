import os
import sys
import pandas as pd
from src.omero_tables.create_omero_table import create_omero_table

from types import SimpleNamespace
sys.path.append('../..')
from utils import helper

def celltype_tables(cell_types_path, save_path, omero_dict, n_clusters, table_name, samples_to_remove=None):

    metadata = pd.read_csv(os.path.join(cell_types_path, 'cell_types.csv'))
    sample_names = metadata["slide_id"]

    for sample in sample_names.unique():
        if samples_to_remove is not None and sample in samples_to_remove:
            print(f"Skipping sample: {sample}")
            continue
        
        os.makedirs(os.path.join(save_path, sample), exist_ok = True)
        table_path = os.path.join(save_path, sample, f'{table_name}.csv')
        if os.path.exists(table_path):
            print(f'Omero table of cell types already saved for sample {sample}')
            continue
        
        print(f"Processing sample: {sample}")
        
        sample_metadata = metadata[metadata["slide_id"] == sample]
        sample_cluster_labels = sample_metadata["cluster_label"]
        sample_cell_types = sample_metadata["cell_type"]
        celltype_df = pd.DataFrame({
            f'clusters_{n_clusters}': sample_cluster_labels,
            'cell_type': sample_cell_types
        })
        roi_value = omero_dict.get(sample, {}).get('roi_id')

        omero_df = create_omero_table(celltype_df, roi_value)
        print(omero_df.head())
        omero_df.to_csv(table_path, index = False)
        print(f'Omero table of cell types saved for sample {sample}')

if __name__ == "__main__":
    main()