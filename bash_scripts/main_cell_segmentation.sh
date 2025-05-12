#!/bin/bash
#SBATCH --job-name=cell_segmentation
#SBATCH --ntasks=1
#SBATCH --output=../logs/cell_segmentation_%j.txt
#SBATCH --partition gpu4_medium,gpu8_medium,gpu4_long,gpu8_long
#SBATCH --nodes=1
#SBATCH --cpus-per-task=1
#SBATCH --ntasks-per-node=1
#SBATCH --mem=300GB
#SBATCH --time=120:00:00
#SBATCH --gres=gpu:4

source .env
# source set_up_conda.sh
module load condaenvs/new/deepcell

cd ..
python main_cell_segmentation.py
