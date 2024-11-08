import argparse
from utils import helper
from types import SimpleNamespace
import pdb
import sys
import os

# import python files
#from preprocess.registration.registration_v2 import run_registration

#must run registration (H&E ROIS --> qptiff ROIS) prior on epoch!!

from src.preprocess.preprocess import run_preprocess

def get_args_parser():
    parser = argparse.ArgumentParser('CODEX Analysis', add_help=False)
    #parser.add_argument('--n_clusters', type=int, help='Batch size per GPU (effective batch size is batch_size * accum_iter * # gpus)')
    return parser 

def update_config_from_args(config, args):
    # Update the in-memory config object with command-line arguments
    for key, value in vars(args).items():
        if value is not None:
            setattr(config, key, value)

def main():
    
    #Parse command-line arguments
    parser = get_args_parser()
    args = parser.parse_args()

    #load the default configuration
    config_yaml= "config/config_preprocessing.yaml"
    run_config = helper.load_yaml_file(config_yaml)
    config = SimpleNamespace(**run_config)

    update_config_from_args(config, args)

    # Add the directory containing your analysis scripts to the Python path
    # this is where the following analysis scripts are located OR change all the module paths in the analysis scripts
    
    sys.path.append(os.path.abspath('src'))

    #Analysis Scripts
    #run_registration(config_yaml)
    sys.path.remove('/gpfs/data/proteomics/projects/mh6486/FenyoLab/Endometrial/CANVAS_v2')
    #pdb.set_trace()
    run_preprocess(config_yaml)
    

#run main() when this analysis.py is run 
if __name__ == "__main__":
    main()