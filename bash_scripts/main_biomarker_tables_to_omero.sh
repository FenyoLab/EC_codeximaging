#!/bin/bash
#SBATCH --job-name=marker_tables_omero_upload
#SBATCH --mail-type=FAIL # Mail events (NONE, BEGIN, END, FAIL, ALL)
#SBATCH --mail-type=END
#SBATCH --ntasks=1
#SBATCH --output=../logs/marker_tables_omero_upload_%j.txt
#SBATCH --mem=20G
#SBATCH --time=4:00:00
#SBATCH --partition=fn_short

source ~/.bashrc
source .env

conda activate omero

cd ../
python main_biomarker_tables_to_omero.py