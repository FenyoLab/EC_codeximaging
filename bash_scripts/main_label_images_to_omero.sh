#!/bin/bash
#SBATCH --job-name=move_label_images_to_research_drive
#SBATCH --mail-type=FAIL # Mail events (NONE, BEGIN, END, FAIL, ALL)
#SBATCH --ntasks=2
#SBATCH --output=../logs/move_to_research_drive_%j.txt
#SBATCH --error=../logs/move_to_research_drive_err_%j.txt
#SBATCH --mem=2G
#SBATCH --time=2:00:00
#SBATCH --partition=data_mover

source ~/.bashrc
conda activate omero

source .env

cd ../
python main_label_images_to_omero.py