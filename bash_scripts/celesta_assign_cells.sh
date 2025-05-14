#!/bin/bash
#SBATCH --partition=fn_medium
#SBATCH --nodes=1
#SBATCH --job-name=celesta_assign_cells
#SBATCH --output=/gpfs/data/proteomics/home/yb2612/results/logs/%x_%j.out  # EDIT PATH TO LOGS DIR
#SBATCH --error=/gpfs/data/proteomics/home/yb2612/results/logs/%x_%j.err   # EDIT PATH TO LOGS DIR
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=50GB
#SBATCH --time=48:00:00

source set_up_conda.sh
conda activate celesta

# make sure you run this script from /path/to/bash_scripts
cd ../src/celesta/

# EDIT ARGUMENTS
Rscript celesta_assign_cells.R \
  --project_title "endometrial_1T_raw_noarcsinh" \
  --celesta_obj_path "/gpfs/data/proteomics/home/yb2612/results/celesta/endometrial_1T_raw_noarcsinh/endometrial_1T_raw_noarcsinh_unassigned_CelestaObj.rds" \
  --output_dir "/gpfs/data/proteomics/home/yb2612/results/celesta" \
  --high_anchor 1 0.8 0.9 0.7 0.7 0.7 0.7 0.5 0.5 0.8 \
  --high_iter 1 0.7 0.8 0.6 0.6 0.6 0.6 0.5 0.5 0.7 \
  --low_anchor 1 1 1 1 1 1 1 1 1 1 \
  --low_iter 1 1 1 1 1 1 1 1 1 1

wait

echo "All jobs completed."