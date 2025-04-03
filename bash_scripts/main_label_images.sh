#!/bin/bash
#SBATCH --job-name=create_label_images
#SBATCH --output=../logs/main_label_images_%j.txt
#SBATCH --partition gpu4_short,gpu8_short,gpu4_dev,gpu8_dev,gpu4_medium,gpu8_medium,gpu4_long,gpu8_long
#SBATCH --nodes=1
#SBATCH --cpus-per-task=1
#SBATCH --ntasks-per-node=1
#SBATCH --mem=300GB
#SBATCH --time=4:00:00
#SBATCH --gres=gpu:4

source set_up_conda.sh
conda activate omero

cd ..
python main_label_images.py
