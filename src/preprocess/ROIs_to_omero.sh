#!/bin/bash

cd /gpfs/data/proteomics/home/lp2700/python_scripts/github_testing/CC_codeximaging/
source bash_scripts/.env
# slurm command later?
conda activate omero

cd src/preprocess
python ROIs_to_Omero.py