#!/bin/bash
#SBATCH --job-name=preprocessing
#SBATCH --mail-type=FAIL # Mail events (NONE, BEGIN, END, FAIL, ALL)
#SBATCH --ntasks=1
#SBATCH --output=../logs/preprocessing_%j.txt
#SBATCH --mem=600G
#SBATCH --time=24:00:00
#SBATCH --cpus-per-task=30
#SBATCH --partition=fn_medium

source ~/.bashrc
conda activate canvas 

cd ../
python run_preprocess.py 