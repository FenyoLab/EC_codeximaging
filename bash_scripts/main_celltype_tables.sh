#!/bin/bash
#SBATCH --job-name=celltype_omero_tables
#SBATCH --mail-type=FAIL # Mail events (NONE, BEGIN, END, FAIL, ALL)
#SBATCH --mail-type=END
#SBATCH --ntasks=2
#SBATCH --output=../logs/celltype_omero_tables_%j.txt
#SBATCH --mem=20G
#SBATCH --time=1:00:00
#SBATCH --partition=cpu_short

source ~/.bashrc
conda activate omero

source .env

cd ../
python main_celltype_tables.py