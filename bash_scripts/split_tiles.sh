#!/bin/bash
#SBATCH --job-name=get_top5_means
#SBATCH --mail-type=FAIL # Mail events (NONE, BEGIN, END, FAIL, ALL)
#SBATCH --ntasks=1
#SBATCH --output=../logs/get_top5_means_%j.txt
#SBATCH --error=../logs/get_top5_means_err_%j.txt
#SBATCH --mem=50G
#SBATCH --time=4:00:00
#SBATCH --cpus-per-task=1
#SBATCH --partition=cpu_short

cd /gpfs/home/as18894/projects/as18894/FenyoLab/Endometrial/EC_codeximaging/src/preprocessing 

module load condaenvs/new/deepcell
python split_tiles.py