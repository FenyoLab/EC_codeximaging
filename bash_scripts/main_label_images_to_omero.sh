#!/bin/bash
#SBATCH --job-name=move_label_images_to_research_drive
#SBATCH --mail-type=FAIL # Mail events (NONE, BEGIN, END, FAIL, ALL)
#SBATCH --ntasks=2
#SBATCH --output=../logs/move_to_research_drive_%j.txt
#SBATCH --error=../logs/move_to_research_drive_err_%j.txt
#SBATCH --mem=2G
#SBATCH --time=2:00:00
#SBATCH --partition=data_mover

<<<<<<< HEAD:bash_scripts/move_to_omero.sh
source ~/.bashrc
conda activate omero

source .env

cd ../
python main_label_imgs_to_omero.py
=======
#make sure you are in a datamover node and have mounted the research drive before running this
source ~/.bashrc
conda activate omero

source bash_scripts/.env

cd ../
python main_label_images_to_omero.py
>>>>>>> 7b82f51368a16714324ece728f1ef598d284ae5f:bash_scripts/main_label_images_to_omero.sh
