import os
import sys
import numpy as np
import pandas as pd
from omero_utils import create_omero_table, upload_omero_table

from types import SimpleNamespace
sys.path.append('../..')
from utils import helper

#set password in env first: export YOUR_PASSWORD='your_password'

def main():
    config_yaml= '/gpfs/home/as18894/projects/as18894/FenyoLab/Endometrial/EC_codeximaging/config/config_cellsegmentation.yaml'
    run_config = helper.load_yaml_file(config_yaml)
    config = SimpleNamespace(**run_config)

    omero_mean_marker_tables(segmentation_data_dir = config.segementation_data_dir, channel_names = config.channel_names, omero_dict = config.omero_image_dict, 
                        save_dir = config.label_images_dir)


def omero_mean_marker_tables(segmentation_data_dir, channel_names, omero_dict, save_dir):
    
    #check that kerberos and password is in env
    password = os.getenv('PASSWORD')
    kerberosid = os.getenv('KERBEROSID')

    if password is None:
        raise ValueError('No password provided in environment variable PASSWORD')
    elif kerberosid is None:
        raise ValueError('No kerberos provided in environment variable KERBEROSID')

    matrix = np.load(os.path.join(segmentation_data_dir, 'matrix.npy'))
    cell_sample_names = np.load(os.path.join(segmentation_data_dir, 'cell_sample_names.npy'))
    
    unique_samples = np.unique(cell_sample_names)

    for sample in unique_samples:
        print(f'Processing {sample}')
        os.makedirs(os.path.join(save_dir, sample), exist_ok =True)

        sample_indices = np.where(cell_sample_names == sample)
        sample_matrix = matrix[sample_indices]
        
        sample_matrix_df = pd.DataFrame(sample_matrix, columns = channel_names)
        roi_value = omero_dict.get(sample, {}).get('roi_id')
        
        omero_df = create_omero_table(sample_matrix_df, roi_value)
        print(omero_df.head())

        table_name = 'raw_biomarker_means'
        table_path = os.path.join(save_dir, sample, 'biomarker_means_omero_table.csv')
        omero_df.to_csv(table_path, index = False)
        image_id = omero_dict.get(sample, {}).get('image_id')
        
        #upload omero table
        upload_omero_table(table_path, sample, table_name, image_id, roi_value, kerberosid, password)
        print(f'Omero table uploaded for {sample}')

def create_omero_table()

if __name__ == "__main__":
    main()