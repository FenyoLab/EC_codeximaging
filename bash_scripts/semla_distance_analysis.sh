#!/bin/bash
#SBATCH --partition=gpu8_short
#SBATCH --nodes=1
#SBATCH --job-name=semla_distance_analysis
#SBATCH --output=../logs/%x_%j.out
#SBATCH --error=../logs/%x_%j.err
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=100GB
#SBATCH --time=12:00:00

source set_up_conda.sh
conda activate seurat_v5

cd ../src/distance_analysis/

Rscript semla_distance_analysis.R