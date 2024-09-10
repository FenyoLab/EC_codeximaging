#!/bin/bash
#SBATCH --job-name=create omero table
#SBATCH --mail-type=FAIL # Mail events (NONE, BEGIN, END, FAIL, ALL)
#SBATCH --ntasks=2
#SBATCH --output=../logs/create_omero_table_%j.txt
#SBATCH --error=../logs/create_omero_table_err_%j.txt
#SBATCH --mem=2G
#SBATCH --time=1:00:00
#SBATCH --partition=data_mover

source ~/.bashrc
conda activate omero

export YOUR_PASSWORD='your_password'
cd /gpfs/home/as18894/projects/as18894/FenyoLab/Endometrial/EC_codeximaging/src/omero_analysis
python omero_table.py