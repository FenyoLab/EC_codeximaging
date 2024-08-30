import os
import numpy as np
from types import SimpleNamespace
from utils import helper

#import config
config_yaml= '/gpfs/home/as18894/projects/as18894/FenyoLab/Endometrial/EC_codeximaging/config/config_cellsegmentation.yaml'
run_config = helper.load_yaml_file(config_yaml)
config = SimpleNamespace(**run_config)

from src.omero_analysis import create_label_image, split_data_by_sample, convert_tiff_to_zarr

#paths
label_images_dir = os.path.join(config.out_dir, config.label_images_dir)
metadata_path = os.path.join(config.out_dir, config.clustering_dir, f'{config.n_clusters}_clusters/metadata_with_cluster_labels.csv')

split_data_by_sample.split_by_sample(tile_dir = config.segementation_data_dir, metadata_path= metadata_path, label_images_dir = label_images_dir, data_dir = config.data_dir, samples_to_remove = config.samples_to_skip)
create_label_image.create_label_image(data_dir = config.data_dir, label_images_dir = label_images_dir)
convert_tiff_to_zarr.convert_tiff_to_zarr(label_images_dir = label_images_dir)