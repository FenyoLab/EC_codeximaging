import os
import numpy as np
from types import SimpleNamespace
from utils import helper

#make sure you are in a datamover node and have mounted the research drive before running this

#load in config
config_yaml= 'config/config_cellsegmentation.yaml'
run_config = helper.load_yaml_file(config_yaml)
config = SimpleNamespace(**run_config)

from src.label_images import move_to_omero

move_to_omero.move_label_images_to_omero(label_images_dir = config.label_images_dir, 
                                        base_dir = config.research_drive_dir, 
                                        image_id_dict = config.omero_image_dict)