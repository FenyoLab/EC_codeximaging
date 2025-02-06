#!/bin/bash
#SBATCH --job-name=create_marker_tables
#SBATCH --mail-type=FAIL # Mail events (NONE, BEGIN, END, FAIL, ALL)
#SBATCH --mail-type=END
#SBATCH --ntasks=1
#SBATCH --output=../logs/assign_celltypes_%j.txt
#SBATCH --mem=50G
#SBATCH --time=1:00:00
#SBATCH --partition=fn_short

module load condaenvs/new/deepcell

cd ../
python main_assign_celltypes.py