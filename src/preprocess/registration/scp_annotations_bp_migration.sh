#!/bin/bash

cd /media/ssd02/lp2700/registration/data/annotations

#rsync -avzrP /media/ssdo2/lp2700/registration/data/annotations bp:/gpfs/data/proteomics/data/Cervical_mIF/

scp -r /media/ssd02/lp2700/registration/data/annotations lp2700@bigpurple:/gpfs/data/proteomics/projects/Cervical_mIF/CC_codeximaging_results
