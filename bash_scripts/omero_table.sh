#!/bin/bash
#SBATCH --job-name=create_omero_table
#SBATCH --mail-type=FAIL # Mail events (NONE, BEGIN, END, FAIL, ALL)
#SBATCH --ntasks=2
#SBATCH --output=../logs/create_omero_table_%j.txt
#SBATCH --error=../logs/create_omero_table_err_%j.txt
#SBATCH --mem=2G
#SBATCH --time=1:00:00
#SBATCH --partition=data_mover

source ~/.bashrc
conda activate omero

source .env
export YOUR_PASSWORD=$PASSWORD

cd src/omero_analysis
python omero_table.py