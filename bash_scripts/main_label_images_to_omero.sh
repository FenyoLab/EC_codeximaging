#!/bin/bash
#SBATCH --job-name=move_label_images_to_research_drive
#SBATCH --mail-type=FAIL # Mail events (NONE, BEGIN, END, FAIL, ALL)
#SBATCH --ntasks=2
#SBATCH --output=../logs/move_to_research_drive_%j.txt
#SBATCH --mem=10G
#SBATCH --time=4:00:00
#SBATCH --partition=data_mover

# If backing up the data, make sure you are in a datamover node and have mounted the research drive before running this
source set_up_conda.sh
conda activate omero

source .env

cd ..
python main_label_images_to_omero.py
