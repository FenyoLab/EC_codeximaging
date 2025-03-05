#!/bin/bash

# you should have created 
# mkdir -p /gpfs/data/proteomics/data/Cervical_mIF/registration_ROIs
# and placed the *.csv files from ExportROIsFromOmero.js in it
# no filename editing needed, it's included in the python script

source /gpfs/data/proteomics/home/lp2700/python_scripts/github_testing/CC_codeximaging/bash_scripts/.env 

conda activate /gpfs/data/proteomics/projects/miniconda3/envs/canvas

cd /gpfs/data/proteomics/home/lp2700/python_scripts/github_testing/CC_codeximaging/src/preprocess/

python add_annotation_exported_roi_JP.py 

