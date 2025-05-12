#!/bin/bash

# run the singularity command first!! then run this file
# singularity shell -B"/media:/media" /media/ssd02/hp_test/valis.sif
cd /media/ssd02/lp2700/registration/src2
# sh arrange_files.sh

# sample_names=$(find ../data/images/* -type d -exec basename {} \;) # catalogs file names from folders in images folder, good for if ../data/images/* is removed within a run
# sample_names=$(find '/media/ssd02/lp2700/landing_pad' -type f -name "*.qptiff" ! -name "._*") # only processes images currently in the landing pad
sample_names=$(find '/media/ssd02/lp2700/landing_pad' -type f -name "*.qptiff" ! -name '._*' -exec basename {} \;)
for sample in $sample_names # can input specific files if needed, I need to include a command to delete images after run to save space
do 
        echo $sample
    python -c "from main_register import run_registration; run_registration('$sample')"
done 


