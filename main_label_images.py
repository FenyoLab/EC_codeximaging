import os
import numpy as np
from types import SimpleNamespace
from utils import helper

#import config
config_yaml= 'config/config_cellsegmentation.yaml'
run_config = helper.load_yaml_file(config_yaml)
config = SimpleNamespace(**run_config)

from src.label_images import split_data_by_sample, create_label_image, convert_tiff_to_zarr

split_data_by_sample.split_by_sample(segmentation_data_dir = config.segmentation_data_dir, 
                                    label_images_dir = config.label_images_dir)
create_label_image.create_label_image(data_dir = config.data_dir, label_images_dir = config.label_images_dir,
                                    label_image_name = 'cell_label_image')
convert_tiff_to_zarr.convert_tiff_to_zarr(label_images_dir = config.label_images_dir, tiff_file='cell_label_image.tiff', zarr_file='cell_label_image.zarr')