import os
import sys
import pandas as pd
from omero_utils import create_omero_table, upload_omero_table

from types import SimpleNamespace
sys.path.append('../..')
from utils import helper

def celltype_cluster_tables(clustering_path, save_path, omero_dict, n_clusters, table_name, samples_to_remove=None, out_suffix=None):

    metadata = pd.read_csv(os.path.join(clustering_path, 'phenotype_clusters.csv'))
    sample_names = metadata["slide_id"]

    for sample in sample_names.unique():
        if samples_to_remove is not None and sample in samples_to_remove:
            print(f"Skipping sample: {sample}")
            continue
        
        os.makedirs(os.path.join(save_path, sample), exist_ok = True)
        table_path = os.path.join(sample_dir, f'{table_name}.csv')
        if os.path.exists(table_path):
            print(f'Omero table of cell type clusters already saved for sample {sample}')
            continue
        
        print(f"Processing sample: {sample}")
        
        sample_metadata = metadata[metadata["slide_id"] == sample]
        sample_cluster_labels = sample_metadata["cluster_label"]
        kmeans_df = pd.DataFrame(sample_cluster_labels).rename(columns={"cluster_label": f'{n_clusters}_clusters'})
        roi_value = omero_dict.get(sample, {}).get('roi_id')

        omero_df = create_omero_table(kmeans_df, roi_value)
        print(omero_df.head())
        omero_df.to_csv(table_path, index = False)

if __name__ == "__main__":
    main()