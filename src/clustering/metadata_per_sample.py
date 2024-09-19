import os
import numpy as np
import pandas as pd

def split_metadata_by_sample(metadata_path, save_path, data_dir, n_clusters, samples_to_remove= None):

    metadata = pd.read_csv(metadata_path)

    os.makedirs(save_path, exist_ok=True)
    unique_sample_names = os.listdir(data_dir)
    

    for sample in unique_sample_names:
        if samples_to_remove is not None:
            if sample in samples_to_remove:
                print(f"Skipping sample: {sample}")
                continue
        if sample == 'common_channels.txt':
            continue
        
        sample_dir = os.path.join(save_path, f'{n_clusters}_clusters', sample)
        os.makedirs(sample_dir, exist_ok=True)
        
        sample_metadata_path = os.path.join(sample_dir, 'sample_metadata.csv') #if sample_metadata already exists, skip this sample
        if os.path.exists(sample_metadata_path):
            print('Metadata already exists for this sample, skipping')
            continue

        print(f"Processing sample: {sample}")
        
        sample_metadata = metadata[metadata['slide_id'] == sample]
        sample_metadata = sample_metadata.reset_index(drop=True)
        sample_metadata.index += 1
        sample_metadata['label_image_cell_index'] = sample_metadata.index

        sample_metadata.to_csv(sample_metadata_path, index=False)