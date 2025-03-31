#!/bin/bash
#SBATCH --job-name=preprocessing
#SBATCH --mail-type=FAIL # Mail events (NONE, BEGIN, END, FAIL, ALL)
#SBATCH --ntasks=2
#SBATCH --output=../logs/preprocessing_%j.txt
#SBATCH --mem=600GB
#SBATCH --time=4:00:00
#SBATCH --partition=fn_medium,fn_short,fn_long

# conda set up and activation
source set_up_conda.sh
conda activate canvas
conda info

pwd
cd ..
python run_preprocess.py
