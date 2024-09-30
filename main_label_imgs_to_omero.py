import os
import numpy as np
from types import SimpleNamespace
from utils import helper

'''this script must be run from datamover node with omero conda environment activated'''
'''first mount the research drive directly in terminal and then run the script (from sbatch)'''

#load in config
config_yaml= '/gpfs/home/as18894/projects/as18894/FenyoLab/Endometrial/EC_codeximaging/config/config_cellsegmentation.yaml'
run_config = helper.load_yaml_file(config_yaml)
config = SimpleNamespace(**run_config)

label_images_dir = os.path.join(config.out_dir, config.label_images_dir)
out_suffix = os.path.basename(config.out_dir)

from src.label_images import move_to_omero

move_to_omero.move_label_images_to_omero(label_images_dir = label_images_dir, base_dir = config.research_drive_dir, 
                        image_id_dict = config.omero_image_info_dict, kerberosid = config.kerberosid)