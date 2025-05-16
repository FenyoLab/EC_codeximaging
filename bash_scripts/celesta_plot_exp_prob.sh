#!/bin/bash
#SBATCH --partition=cpu_short
#SBATCH --nodes=1
#SBATCH --job-name=celesta_plot_exp_prob
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
python -u celesta_plot_exp_prob.py \
  --project_title "endometrial_1T_raw_noarcsinh" \
  --results_dir "/gpfs/data/proteomics/home/yb2612/results/celesta" \

wait

echo "All jobs completed."