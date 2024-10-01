import os
import sys
import pandas as pd
from omero_utils import create_omero_table, upload_omero_table

from types import SimpleNamespace
sys.path.append('../..')
from utils import helper

def create_celltype_clusters_df(clustering_path, save_path, omero_dict, n_clusters, samples_to_remove=None, out_suffix=None):

    password = os.getenv('PASSWORD')
    kerberosid = os.getenv('KERBEROSID')

    if password is None:
        raise ValueError('No password provided in environment variable PASSWORD')
    elif kerberosid is None:
        raise ValueError('No kerberos provided in environment variable KERBEROSID')

    metadata = pd.read_csv(os.path.join(clustering_path, 'phenotype_clusters.csv'))
    sample_names = metadata["slide_id"]

    for sample in sample_names.unique():
        if samples_to_remove is not None and sample in samples_to_remove:
            print(f"Skipping sample: {sample}")
            continue
        
        table_path = os.path.join(sample_dir, f'celltype_{n_clusters}clusters.csv')
        if os.path.exists(table_path):
            print(f'Cluster information already exists for this {sample}, skipping')
            continue
        
        print(f"Processing sample: {sample}")
        sample_dir = os.path.join(save_path, sample)
        os.makedirs(sample_dir, exist_ok=True)
        
        sample_metadata = metadata[metadata["slide_id"] == sample]
        sample_cluster_labels = sample_metadata["cluster_label"]

        kmeans_df = pd.DataFrame(sample_cluster_labels).rename(columns={"cluster_label": f'{n_clusters}_clusters'})
        roi_value = omero_dict.get(sample, {}).get('roi_id')

        omero_df = create_omero_table(kmeans_df, roi_value)
        print(omero_df.head())

        date = "_".join(out_suffix.split("_")[1:])
        table_name = f'celltype_{n_clusters}clusters_{date}'
        omero_df.to_csv(table_path, index = False)
        image_id = omero_dict.get(sample, {}).get('image_id')

        upload_omero_table(table_path, sample, table_name, image_id, roi_value, kerberosid, password)
        print(f'Omero table uploaded for {sample}')

if __name__ == "__main__":
    main()