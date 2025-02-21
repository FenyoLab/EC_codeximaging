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

    neutrophil_percentage_df_path = '/gpfs/data/proteomics/projects/Endometrial_mIF/EC_codeximaging_results/out_12-2-24/remove_necrosis'
    omero_tables_path = '/gpfs/data/proteomics/projects/Endometrial_mIF/EC_codeximaging_results/out_12-2-24/omero_tables'
    omero_dict = config.omero_image_dict
    table_name = 'neutrophil_percentage'

    neutrophil_percentage_table(neutrophil_percentage_df_path, omero_tables_path, omero_dict, table_name)

def neutrophil_percentage_table(neutrophil_percentage_df_path, omero_tables_path, omero_dict, table_name, samples_to_remove=None):
    
    for sample in os.listdir(neutrophil_percentage_df_path):
        if samples_to_remove is not None and sample in samples_to_remove:
            print(f"Skipping sample: {sample}")
            continue
        
        os.makedirs(os.path.join(omero_tables_path, sample), exist_ok = True)
        table_path = os.path.join(omero_tables_path, sample, f'{table_name}.csv')
        #if os.path.exists(table_path):
        #    print(f'Omero table of cell types already saved for sample {sample}')
        #    continue
        
        print(f"Processing sample: {sample}")

        neutrophil_percentage_df = pd.read_csv(os.path.join(neutrophil_percentage_df_path, sample, 'neutrophil_percentage.csv'), index_col = 0)
        roi_value = omero_dict.get(sample, {}).get('tile_roi_id')

        omero_df = create_omero_table(neutrophil_percentage_df, roi_value)
        print(omero_df.head())
        omero_df.to_csv(table_path, index = False)
        print(f'Omero table of cell types saved for sample {sample}')

if __name__ == "__main__":
    main()