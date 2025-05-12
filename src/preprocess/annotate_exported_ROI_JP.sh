#!/bin/bash

# you should have created 
# mkdir -p /gpfs/data/proteomics/data/Cervical_mIF/registration_ROIs_downloaded
# and placed the *.csv files from ExportROIsFromOmero.js in it
# no filename editing needed, it's included in the python script
# make sure that your actual csv files do not have a "._" in the name, they will be automatically removed in python script

source /gpfs/data/proteomics/home/lp2700/python_scripts/github_testing/CC_codeximaging/bash_scripts/.env 

conda activate /gpfs/data/proteomics/projects/miniconda3/envs/canvas

cd /gpfs/data/proteomics/home/lp2700/python_scripts/github_testing/CC_codeximaging/src/preprocess/
python add_annotation_exported_roi_JP.py 

cd /gpfs/data/proteomics/data/Cervical_mIF/
# needs to be made into slurm command?
for file in /gpfs/data/proteomics/data/Cervical_mIF/registration_ROIs_downloaded/*
do 
    echo $(basename "$file")
    rsync -avzP  "$file" epoch:/media/ssd02/lp2700/landing_pad/
    mv "$file" /gpfs/data/proteomics/data/Cervical_mIF/registration_ROIs/
done

rsync -avzrP /gpfs/data/proteomics/home/lp2700/python_scripts/github_testing/CC_codeximaging/src/preprocess/registration/ epoch:/media/ssd02/lp2700/registration/src2/
