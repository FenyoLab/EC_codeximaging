import os
import numpy as np
import pandas as pd
from types import SimpleNamespace
import omero2pandas

import sys
sys.path.append('../..')
from utils import helper

#set password in env first: export YOUR_PASSWORD='your_password'

def main():
    config_yaml= '/gpfs/home/as18894/projects/as18894/FenyoLab/Endometrial/EC_codeximaging/config/config_cellsegmentation.yaml'
    run_config = helper.load_yaml_file(config_yaml)
    config = SimpleNamespace(**run_config)

    omero_marker_tables(data_dir = config.segementation_data_dir, channel_names = config.channel_names, omero_info_dict = config.omero_image_info_dict, 
                        save_dir = config.label_images_dir, exclude_channel_names = config.exclude_channel_names, kerberosid = config.kerberosid)


def omero_marker_tables(data_dir, channel_names, omero_info_dict, save_dir, exclude_channel_names = None, kerberosid = None):

    matrix = np.load(os.path.join(data_dir, 'matrix.npy'))
    cell_sample_names = np.load(os.path.join(data_dir, 'cell_sample_names.npy'))
    metadata = pd.read_csv(os.path.join(data_dir, 'metadata.csv'), index_col = 0)

    unique_samples = np.unique(cell_sample_names)
    
    os.chdir(save_dir)

    for sample in unique_samples:
        print(f'Processing {sample}')
        os.makedirs(sample, exist_ok =True)

        sample_indices = np.where(cell_sample_names == sample)
        sample_matrix = matrix[sample_indices]
        print(sample_matrix.shape)

        sample_metadata = metadata.iloc[sample_indices]
        sample_metadata = sample_metadata.reset_index(drop=True)
        sample_metadata.index += 1
        sample_metadata['label_image_cell_index'] = sample_metadata.index
        print(sample_metadata.shape)

        roi_value = omero_info_dict.get(sample, {}).get('roi_id')

        omero_df = pd.DataFrame({
            'object': sample_metadata['label_image_cell_index'],
            'roi': roi_value,
        })

        for i, channel in enumerate(channel_names):
            if channel in exclude_channel_names:
                continue   
            omero_df[channel] = sample_matrix[:, i]

        # Save or process the DataFrame as needed
        print(omero_df.head())
        table_path = os.path.join(save_dir, sample, 'biomarker_means_omero_table.csv')
        omero_df.to_csv(table_path, index = False)
        

        table_name = 'raw_biomarker_means'
        image_id = omero_info_dict.get(sample, {}).get('image_id')
        password = os.getenv('YOUR_PASSWORD')


        ann_id = omero2pandas.upload_table(table_path, table_name,
                                        links=[("Image", image_id), ("Roi", roi_value)], 
                                        server="omero.nyumc.org", port=4064, username=kerberosid, password=password)
        print(f'Omero table uploaded for {sample}')

if __name__ == "__main__":
    main()