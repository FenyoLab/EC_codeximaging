#!/bin/bash
#SBATCH --partition=cpu_short
#SBATCH --nodes=1
#SBATCH --job-name=celesta_assign_cells
#SBATCH --output=/gpfs/data/proteomics/home/yb2612/results/logs/%x_%j.out  # EDIT PATH TO LOGS DIR
#SBATCH --error=/gpfs/data/proteomics/home/yb2612/results/logs/%x_%j.err   # EDIT PATH TO LOGS DIR
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=10GB
#SBATCH --time=12:00:00

source set_up_conda.sh
conda activate celesta

# make sure you run this script from /path/to/bash_scripts
cd ../src/celesta/

# EDIT ARGUMENTS
Rscript celesta_assign_cells.R \
  --project_title "cervical_10103_raw_arcsinh" \
  --results_dir "/gpfs/data/proteomics/home/yb2612/results/celesta" \
#   --high_anchor 0.8 0.8 0.8 0.8 0.8 0.8 0.8 0.8 0.8 0.8 0.8 0.8 0.8 0.8 \
#   --high_iter 0.7 0.7 0.7 0.7 0.7 0.7 0.7 0.7 0.7 0.7 0.7 0.7 0.7 0.7 \
#   --low_anchor 1 1 1 1 1 1 1 1 1 1 1 1 1 1 \
#   --low_iter 1 1 1 1 1 1 1 1 1 1 1 1 1 1

Rscript celesta_assign_cells.R \
  --project_title "cervical_28873_raw_arcsinh" \
  --results_dir "/gpfs/data/proteomics/home/yb2612/results/celesta" \

Rscript celesta_assign_cells.R \
  --project_title "cervical_34933_raw_arcsinh" \
  --results_dir "/gpfs/data/proteomics/home/yb2612/results/celesta" \

Rscript celesta_assign_cells.R \
  --project_title "cervical_02433_raw_arcsinh" \
  --results_dir "/gpfs/data/proteomics/home/yb2612/results/celesta" \

wait

echo "All jobs completed."