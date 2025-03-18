import os
import numpy as np
from types import SimpleNamespace
from utils import helper

#import config
config_yaml= 'config/config_test.yaml'
run_config = helper.load_yaml_file(config_yaml)
config = SimpleNamespace(**run_config)

from src.label_images.csv_input import upload_label_image

upload_label_image.omero_label_image(base_dir = config.research_drive_dir, 
                                    seg_data_path = config.segmentation_data_dir,
                                    image_id_dict = config.omero_image_dict, 
                                    channel_names = config.channel_names, 
                                    tile_size = config.tile_size)

