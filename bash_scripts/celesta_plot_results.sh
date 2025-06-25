#!/bin/bash
#SBATCH --partition=cpu_short
#SBATCH --nodes=1
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=5GB
#SBATCH --time=12:00:00

sample=$1

source set_up_conda.sh
conda activate celesta

cd ../src/celesta/

echo "Running sample: $sample"

python -u celesta_plot_results.py --sample "$sample"
