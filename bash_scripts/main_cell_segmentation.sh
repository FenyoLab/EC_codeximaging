#!/bin/bash
#SBATCH --job-name=cell_segmentation
#SBATCH --mail-type=FAIL # Mail events (NONE, BEGIN, END, FAIL, ALL)
#SBATCH --ntasks=1
#SBATCH --output=../logs/cell_segmentation_%j.txt
#SBATCH --mem=200G
#SBATCH --time=72:00:00
#SBATCH --cpus-per-task=1
#SBATCH --partition=fn_medium

module load condaenvs/new/deepcell

cd ../
python main_cell_segmentation.py