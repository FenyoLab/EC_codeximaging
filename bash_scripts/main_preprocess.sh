#!/bin/bash
#SBATCH --job-name=preprocessing
#SBATCH --output=../logs/preprocessing_%j.txt
#SBATCH --partition gpu4_short,gpu8_short,gpu4_dev,gpu8_dev,gpu4_medium,gpu8_medium,gpu4_long,gpu8_long
#SBATCH --nodes=1
#SBATCH --cpus-per-task=1
#SBATCH --ntasks-per-node=1
#SBATCH --mem=300GB
#SBATCH --time=4:00:00
#SBATCH --gres=gpu:4

# conda set up and activation
cd /gpfs/data/proteomics/home/lp2700/python_scripts/github_testing/CC_codeximaging/
source set_up_conda.sh
conda activate canvas
conda info

pwd
cd ..
python run_preprocess.py
