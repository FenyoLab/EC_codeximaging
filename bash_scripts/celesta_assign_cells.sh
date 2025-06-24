#!/bin/bash
#SBATCH --partition=cpu_medium
#SBATCH --nodes=1
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=10GB
#SBATCH --time=48:00:00

sample=$1

source set_up_conda.sh
conda activate celesta

cd ../src/celesta/

echo "Running sample: $sample"

# edit arguments
Rscript celesta_assign_cells.R \
    --project_title "cervical_${sample}_raw_arcsinh" \
    --results_dir "/gpfs/data/proteomics/home/yb2612/results/celesta/detailed_cell_types" \
    --high_anchor 0.7 0.7 0.9 0.7 0.7 0.7 0.7 0.7 0.7 0.7 0.7 0.7 0.7 0.7 \
    --high_iter 0.5 0.5 0.6 0.5 0.5 0.5 0.5 0.5 0.5 0.5 0.5 0.5 0.5 0.5