#!/bin/bash
#SBATCH --job-name=cell_segmentation
#SBATCH --ntasks=1
#SBATCH --output=../logs/cell_segmentation_%j.txt
#SBATCH --partition gpu4_short,gpu8_short,gpu4_dev,gpu8_dev,gpu4_medium,gpu8_medium,gpu4_long,gpu8_long
#SBATCH --nodes=1
#SBATCH --cpus-per-task=1
#SBATCH --ntasks-per-node=1
#SBATCH --mem=300GB
#SBATCH --time=4:00:00
#SBATCH --gres=gpu:4

source .env
module load condaenvs/new/deepcell

cd ..
python main_cell_segmentation.py
