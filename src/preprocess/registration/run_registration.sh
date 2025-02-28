#!/bin/bash

# singularity shell -B"/media:/media" /media/ssd02/hp_test/valis.sif
cd /media/ssd02/lp2700/registration/data/images/
for variable in *
do 
        echo $variable
	cd /media/ssd02/lp2700/registration/src
    python main_regster.run_registration($variable)
done 


