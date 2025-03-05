#!/bin/bash
cd /gpfs/data/proteomics/data/Cervical_mIF/
for folded in 'qptiff_dat' 'svs_dat' 'registration_ROIs'
do
    for file in $folded/*
    do 
        echo $(basename "$file")
        rsync -avzP  "$file" epoch:/media/ssd02/lp2700/landing_pad/
    done
done
# needs to be made into slurm command?
rsync -avzrP /gpfs/data/proteomics/home/lp2700/python_scripts/github_testing/CC_codeximaging/src/preprocess/registration/ epoch:/media/ssd02/lp2700/registration/src2/