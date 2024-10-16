#!/bin/bash
#SBATCH --job-name=cell_segmentation_analysis
#SBATCH --mail-type=FAIL # Mail events (NONE, BEGIN, END, FAIL, ALL)
#SBATCH --ntasks=1
#SBATCH --output=../logs/cell_segmentation_analysis_%j.txt
#SBATCH --error=../logs/cell_segmentation_analysis_err_%j.txt
#SBATCH --mem=200G
#SBATCH --time=48:00:00
#SBATCH --cpus-per-task=1
#SBATCH --partition=cpu_medium

module load condaenvs/new/deepcell

cd ../
python main_cell_segmentation_analysis.py