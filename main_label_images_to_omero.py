import os
import numpy as np
from types import SimpleNamespace
from utils import helper

'''this script must be run from datamover node with omero conda environment activated'''
'''first mount the research drive directly in terminal and then run the script (from sbatch)'''
'''if running srun: have to do source .env before running'''

#load in config
config_yaml= 'config/config_cellsegmentation.yaml'
run_config = helper.load_yaml_file(config_yaml)
config = SimpleNamespace(**run_config)

from src.label_images import move_to_omero

move_to_omero.move_label_images_to_omero(label_images_dir = config.label_images_dir, 
                                        base_dir = config.research_drive_dir, 
                                        image_id_dict = config.omero_image_dict)