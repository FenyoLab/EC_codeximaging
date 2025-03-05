#!/bin/bash

#singularity shell -B"/media:/media" /media/ssd02/hp_test/valis.sif
cd /media/ssd02/lp2700/registration/src2
sample_names=$(find ../data/images/* -type d -exec basename {} \;)
for sample in $sample_names
do 
        echo $sample
    python -c "from main_register import run_registration; run_registration('$sample')"
done 


