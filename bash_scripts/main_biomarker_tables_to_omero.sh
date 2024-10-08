#!/bin/bash
#SBATCH --job-name=marker_tables_omero_upload
#SBATCH --mail-type=FAIL # Mail events (NONE, BEGIN, END, FAIL, ALL)
#SBATCH --mail-type=END
#SBATCH --ntasks=1
#SBATCH --output=../logs/marker_tables_omero_upload_%j.txt
#SBATCH --error=../logs/marker_tables_omero_upload_err_%j.txt
#SBATCH --mem=20G
#SBATCH --time=4:00:00
#SBATCH --partition=cpu_short

source ~/.bashrc
conda activate omero

source bash_scripts/.env

cd ../
python main_biomarker_tables_to_omero.py