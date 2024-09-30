import os
import numpy as np
from types import SimpleNamespace
from utils import helper

#import config
config_yaml= '/gpfs/data/proteomics/projects/mh6486/FenyoLab/Endometrial/EC_codeximaging/config/config_cellsegmentation_test.yaml'
run_config = helper.load_yaml_file(config_yaml)
config = SimpleNamespace(**run_config)

from src.omero_analysis import split_data_by_sample, create_label_image, convert_tiff_to_zarr

metadata_path = os.path.join(config.segementation_data_dir, 'metadata.csv')

split_data_by_sample.split_by_sample(tile_dir = config.segementation_data_dir, metadata_path = metadata_path, label_images_dir = config.label_images_dir, data_dir = config.data_dir)
create_label_image.create_label_image(data_dir = config.data_dir, label_images_dir = config.label_images_dir)
convert_tiff_to_zarr.convert_tiff_to_zarr(label_images_dir = config.label_images_dir)