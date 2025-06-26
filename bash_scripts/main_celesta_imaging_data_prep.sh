#!/bin/bash
#SBATCH --partition=cpu_short
#SBATCH --nodes=1
#SBATCH --job-name=celesta_imaging_data_prep
#SBATCH --output=/gpfs/data/proteomics/home/yb2612/results/logs/%x_%j.out  # EDIT PATH TO LOGS DIR
#SBATCH --error=/gpfs/data/proteomics/home/yb2612/results/logs/%x_%j.err   # EDIT PATH TO LOGS DIR
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=10GB
#SBATCH --time=12:00:00

source set_up_conda.sh
conda activate celesta

cd ../

python -u celesta_imaging_data_prep.py

wait

echo "All jobs completed."