#!/bin/bash
#SBATCH --job-name=move_label_images_to_research_drive
#SBATCH --mail-type=FAIL # Mail events (NONE, BEGIN, END, FAIL, ALL)
#SBATCH --ntasks=2
#SBATCH --output=../logs/upload_to_omero_%j.txt
#SBATCH --mem=100G
#SBATCH --time=4:00:00
#SBATCH --partition=data_mover

# make sure you are in a datamover node and have mounted the research drive before running this
# can also run directly on datamover node in terminal if research drive access is weird
source set_up_conda.sh
module load condaenvs/new/omero2

source .env

cd ..
python main_label_images_csv.py
