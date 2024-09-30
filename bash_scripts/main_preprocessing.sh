#!/bin/bash
#SBATCH --job-name=preprocessing
#SBATCH --mail-type=FAIL # Mail events (NONE, BEGIN, END, FAIL, ALL)
#SBATCH --ntasks=1
#SBATCH --output=../logs/preprocessing_%j.txt
#SBATCH --error=../logs/preprocessing_err_%j.txt
#SBATCH --mem=200G
#SBATCH --time=18:00:00
#SBATCH --cpus-per-task=1
#SBATCH --partition=cpu_medium

cd /gpfs/home/as18894/projects/as18894/FenyoLab/Endometrial/EC_codeximaging

module load condaenvs/new/deepcell
python main_preprocessing.py