import os
import numpy as np
from types import SimpleNamespace
from utils import helper

#import config
config_yaml_cellseg= '/gpfs/data/proteomics/projects/mh6486/FenyoLab/Endometrial/EC_codeximaging/config/config_cellsegmentation_test.yaml'
run_config_cellseg = helper.load_yaml_file(config_yaml_cellseg)
config_cellseg = SimpleNamespace(**run_config_cellseg)

config_yaml_cellphen = '/gpfs/data/proteomics/projects/mh6486/FenyoLab/Endometrial/EC_codeximaging/config/config_cellphenotyping.yaml'
run_config_cellphen = helper.load_yaml_file(config_yaml_cellphen)
config_cellphen = SimpleNamespace(**run_config_cellphen)

from src.clustering import kmeans 

kmeans.assign_cellphenotype(clustering_results_dir = config_cellseg.out_dir, n_clusters = config_cellseg.n_clusters, cluster_labels = config_cellphen.cluster_celltype_labels)