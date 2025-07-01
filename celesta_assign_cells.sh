#!/bin/bash
#SBATCH --partition=cpu_medium
#SBATCH --nodes=1
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=10GB
#SBATCH --time=48:00:00

sample=$1

cd src/celesta/

echo "Running sample: $sample"

Rscript celesta_assign_cells.R "$sample"