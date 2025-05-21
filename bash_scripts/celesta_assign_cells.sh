#!/bin/bash
#SBATCH --partition=cpu_medium
#SBATCH --nodes=1
#SBATCH --job-name=celesta_assign_cells
#SBATCH --output=/gpfs/data/proteomics/home/yb2612/results/logs/%x_%j.out  # EDIT PATH TO LOGS DIR
#SBATCH --error=/gpfs/data/proteomics/home/yb2612/results/logs/%x_%j.err   # EDIT PATH TO LOGS DIR
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=10GB
#SBATCH --time=24:00:00

source set_up_conda.sh
conda activate celesta

# make sure you run this script from /path/to/bash_scripts
cd ../src/celesta/

# EDIT ARGUMENTS

# ## first 4 samples
# Rscript celesta_assign_cells.R \
#   --project_title "cervical_28873_raw_arcsinh" \
#   --results_dir "/gpfs/data/proteomics/home/yb2612/results/celesta" \
#   --high_anchor 0.7 0.7 0.8 0.7 0.8 0.9 0.7 0.7 0.7 0.7 \
#   # --high_iter 0.5 0.5 0.6 0.5 0.5 0.7 0.5 0.5 0.5 0.5 \
#   --low_anchor 1 1 1 1 1 1 1 1 1 1 \
#   --low_iter 1 1 1 1 1 1 1 1 1 1

# Rscript celesta_assign_cells.R \
#   --project_title "cervical_28873_raw_arcsinh" \
#   --results_dir "/gpfs/data/proteomics/home/yb2612/results/celesta" \
#   --high_anchor 0.7 0.7 0.8 0.7 0.7 0.9 0.7 0.7 0.7 0.7 \
#   # --high_iter 0.5 0.5 0.7 0.5 0.5 0.8 0.5 0.5 0.5 0.5 \
#   --low_anchor 1 1 1 1 1 1 1 1 1 1 \
#   --low_iter 1 1 1 1 1 1 1 1 1 1

# Rscript celesta_assign_cells.R \
#   --project_title "cervical_34933_raw_arcsinh" \
#   --results_dir "/gpfs/data/proteomics/home/yb2612/results/celesta" \
#   --high_anchor 0.7 0.7 0.9 0.7 0.7 0.7 0.7 0.7 0.7 0.7 \
#   # --high_iter 0.6 0.6 0.6 0.6 0.6 0.6 0.6 0.6 0.6 0.6 \
#   --low_anchor 1 1 1 1 1 1 1 1 1 1 \
#   --low_iter 1 1 1 1 1 1 1 1 1 1

# Rscript celesta_assign_cells.R \
#   --project_title "cervical_34933_raw_arcsinh" \
#   --results_dir "/gpfs/data/proteomics/home/yb2612/results/celesta" \
#   --high_anchor 0.7 0.7 0.8 0.7 0.7 0.7 0.7 0.7 0.7 0.7 \
#   # --high_iter 0.6 0.6 0.6 0.6 0.6 0.6 0.6 0.6 0.6 0.6 \
#   --low_anchor 1 1 1 1 1 1 1 1 1 1 \
#   --low_iter 1 1 1 1 1 1 1 1 1 1

# Rscript celesta_assign_cells.R \
#   --project_title "cervical_28873_raw_arcsinh" \
#   --results_dir "/gpfs/data/proteomics/home/yb2612/results/celesta" \

# Rscript celesta_assign_cells.R \
#   --project_title "cervical_34933_raw_arcsinh" \
#   --results_dir "/gpfs/data/proteomics/home/yb2612/results/celesta" \

# Rscript celesta_assign_cells.R \
#   --project_title "cervical_02433_raw_arcsinh" \
#   --results_dir "/gpfs/data/proteomics/home/yb2612/results/celesta" \

# <100k
# Rscript celesta_assign_cells.R \
#   --project_title "cervical_39367_raw_arcsinh" \
#   --results_dir "/gpfs/data/proteomics/home/yb2612/results/celesta" \

# Rscript celesta_assign_cells.R \
#   --project_title "cervical_49411_raw_arcsinh" \
#   --results_dir "/gpfs/data/proteomics/home/yb2612/results/celesta" \

# ## >100k, <1M
# Rscript celesta_assign_cells.R \
#   --project_title "cervical_09002_raw_arcsinh" \
#   --results_dir "/gpfs/data/proteomics/home/yb2612/results/celesta" \

# Rscript celesta_assign_cells.R \
#   --project_title "cervical_08153_raw_arcsinh" \
#   --results_dir "/gpfs/data/proteomics/home/yb2612/results/celesta" \

# Rscript celesta_assign_cells.R \
#   --project_title "cervical_00438_raw_arcsinh" \
#   --results_dir "/gpfs/data/proteomics/home/yb2612/results/celesta" \

# Rscript celesta_assign_cells.R \
#   --project_title "cervical_07688_raw_arcsinh" \
#   --results_dir "/gpfs/data/proteomics/home/yb2612/results/celesta" \

# Rscript celesta_assign_cells.R \
#   --project_title "cervical_04738_raw_arcsinh" \
#   --results_dir "/gpfs/data/proteomics/home/yb2612/results/celesta" \

# ## >1M
# Rscript celesta_assign_cells.R \
#   --project_title "cervical_07611_raw_arcsinh" \
#   --results_dir "/gpfs/data/proteomics/home/yb2612/results/celesta" \

Rscript celesta_assign_cells.R \
  --project_title "cervical_00862_raw_arcsinh" \
  --results_dir "/gpfs/data/proteomics/home/yb2612/results/celesta" \

# Rscript celesta_assign_cells.R \
#   --project_title "cervical_10285_raw_arcsinh" \
#   --results_dir "/gpfs/data/proteomics/home/yb2612/results/celesta" \

# Rscript celesta_assign_cells.R \
#   --project_title "cervical_07291_raw_arcsinh" \
#   --results_dir "/gpfs/data/proteomics/home/yb2612/results/celesta" \

wait

echo "All jobs completed."