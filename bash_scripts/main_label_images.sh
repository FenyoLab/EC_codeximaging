#!/bin/bash
#SBATCH --job-name=create_label_images
#SBATCH --mail-type=FAIL # Mail events (NONE, BEGIN, END, FAIL, ALL)
#SBATCH --ntasks=1
#SBATCH --output=../logs/main_label_images_%j.txt
#SBATCH --mem=100G
#SBATCH --time=4:00:00
#SBATCH --cpus-per-task=1
#SBATCH --partition=cpu_short

source ~/.bashrc
conda activate omero

cd ../
python main_label_images.py