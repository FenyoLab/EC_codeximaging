import os
import numpy as np
from types import SimpleNamespace
from utils import helper

# Make sure you are in a datamover node and have mounted the research drive before running this

# Load in config
config_yaml= 'config/config_cellsegmentation.yaml'
run_config = helper.load_yaml_file(config_yaml)
config = SimpleNamespace(**run_config)

from src.label_images.tiff_input_old import move_to_omero

out_suffix = os.path.basename(config.out_dir)
date = "_".join(out_suffix.split("_")[1:])

move_to_omero.move_label_images_to_omero(label_images_dir = config.label_images_dir, 
                                        research_dir = config.research_drive_dir, 
                                        omero_dir = config.omero_dir,
                                        image_id_dict = config.omero_image_dict, 
                                        image_name = 'cell_label_image', date = date)
