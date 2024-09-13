#!/bin/bash
#SBATCH --job-name=cell_segmentation
#SBATCH --mail-type=FAIL # Mail events (NONE, BEGIN, END, FAIL, ALL)
#SBATCH --ntasks=1
#SBATCH --output=../logs/cell_segmentation_%j.txt
#SBATCH --error=../logs/cell_segmentation_err_%j.txt
#SBATCH --mem=50G
#SBATCH --time=36:00:00
#SBATCH --cpus-per-task=1
#SBATCH --partition=cpu_medium

cd /gpfs/home/as18894/projects/as18894/FenyoLab/Endometrial/EC_codeximaging
source ~/.bashrc

module load condaenvs/new/deepcell
python main_cell_segmentation_analysis.py