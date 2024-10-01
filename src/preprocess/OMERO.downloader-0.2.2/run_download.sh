#!/bin/bash
#SBATCH --job-name=download_HE
#SBATCH --mail-type=FAIL # Mail events (NONE, BEGIN, END, FAIL, ALL)
#SBATCH --ntasks=1
#SBATCH --output=download4_%A_%a.out
#SBATCH --error=download4_%A_%a.err
#SBATCH --mem=32G
#SBATCH --time=10:00:00
#SBATCH -p fn_short


for variable in 544833 544800 544812 544830 657369 544818 544821 544806 544797 544803 544827 544794 657363 657366 544809 544815 544776 544791 544788 544782 544779
do 
        echo $variable
	./download.sh -b '/gpfs/data/proteomics/data/Endometrial_mIF/SVS_HE' -s omero.nyumc.org -u mh6486 -w 'PASSWORD' -f binary Image:$variable
done 


