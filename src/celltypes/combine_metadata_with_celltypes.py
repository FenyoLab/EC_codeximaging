import os
import pandas as pd
import sys

from types import SimpleNamespace
sys.path.append('/gpfs/home/as18894/projects/as18894/FenyoLab/Endometrial/EC_codeximaging')
from utils import helper

def main():
    #import config
    config_yaml= '/gpfs/home/as18894/projects/as18894/FenyoLab/Endometrial/EC_codeximaging/config/config_cellphenotyping.yaml'
    run_config = helper.load_yaml_file(config_yaml)
    config = SimpleNamespace(**run_config)

    metadata_path = os.path.join(config.segmentation_data_dir, 'metadata.csv')
    celltypes_path = os.path.join(config.out_dir, config.celltypes_dir, f'{config.n_clusters_celltypes}_clusters', 'cell_types.csv')

    combine_metadata_with_celltypes(metadata_path, celltypes_path)

def combine_metadata_with_celltypes(metadata_path, celltypes_path): 
    metadata = pd.read_csv(metadata_path, index_col=0)
    celltypes = pd.read_csv(celltypes_path, index_col=0)

    celltypes.index = celltypes.index - 1
    assert metadata.index.equals(celltypes.index) 

    metadata['cluster_label'] = celltypes['cluster_label']
    metadata['cell_type'] = celltypes['cell_type']

    print(metadata.shape)
    print(metadata.head())

    output_dir = os.path.dirname(celltypes_path)
    metadata.to_csv(os.path.join(output_dir, 'metadata_with_celltypes.csv'))

if __name__ == '__main__':
    main()