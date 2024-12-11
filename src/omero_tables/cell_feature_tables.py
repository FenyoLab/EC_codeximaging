import os
import sys
import pandas as pd
#from src.omero_tables.create_omero_table import create_omero_table
from create_omero_table import create_omero_table

from types import SimpleNamespace
sys.path.append('/gpfs/home/as18894/projects/as18894/FenyoLab/Endometrial/EC_codeximaging')
from utils import helper

def main():
    #import config
    config_yaml= '/gpfs/home/as18894/projects/as18894/FenyoLab/Endometrial/EC_codeximaging/config/config_cellsegmentation.yaml'
    run_config = helper.load_yaml_file(config_yaml)
    config = SimpleNamespace(**run_config)

    metadata_path = os.path.join(config.segmentation_data_dir)
    save_path = os.path.join(config.segmentation_data_dir, config.omero_table_dir)
    omero_dict = config.omero_image_dict
    table_name = 'cell_features'

    cell_feature_tables(metadata_path, save_path, omero_dict, table_name)

def cell_feature_tables(metadata_path, save_path, omero_dict, table_name, samples_to_remove=None):

    metadata = pd.read_csv(os.path.join(metadata_path, 'metadata.csv'))

    for sample in metadata['slide_id'].unique():
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
        sample_area = sample_metadata["area"]
        sample_perimeter = sample_metadata["perimeter"]
        sample_axis_ratio = sample_metadata["axis_ratio"]
        metadata_df = pd.DataFrame({
            'area': sample_area,
            'perimeter': sample_perimeter,
            'axis_ratio': sample_axis_ratio
        })
        roi_value = omero_dict.get(sample, {}).get('roi_id')

        omero_df = create_omero_table(metadata_df, roi_value)
        print(omero_df.head())
        omero_df.to_csv(table_path, index = False)
        print(f'Omero table of cell types saved for sample {sample}')

if __name__ == "__main__":
    main()