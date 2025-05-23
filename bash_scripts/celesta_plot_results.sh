#!/bin/bash
#SBATCH --partition=cpu_short
#SBATCH --nodes=1
#SBATCH --job-name=celesta_plot_results
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

### first 4 samples
# python -u celesta_plot_results.py \
#   --project_title "cervical_10103_raw_arcsinh" \
#   --results_dir "/gpfs/data/proteomics/home/yb2612/results/celesta" \

# python -u celesta_plot_results.py \
#   --project_title "cervical_34933_raw_arcsinh" \
#   --results_dir "/gpfs/data/proteomics/home/yb2612/results/celesta" \

# python -u celesta_plot_results.py \
#   --project_title "cervical_28873_raw_arcsinh" \
#   --results_dir "/gpfs/data/proteomics/home/yb2612/results/celesta" \

# python -u celesta_plot_results.py \
#   --project_title "cervical_02433_raw_arcsinh" \
#   --results_dir "/gpfs/data/proteomics/home/yb2612/results/celesta" \

# ### <100k
# python -u celesta_plot_results.py \
#   --project_title "cervical_39367_raw_arcsinh" \
#   --results_dir "/gpfs/data/proteomics/home/yb2612/results/celesta" \

# python -u celesta_plot_results.py \
#   --project_title "cervical_49411_raw_arcsinh" \
#   --results_dir "/gpfs/data/proteomics/home/yb2612/results/celesta" \

# ### >100k, <1M
# python -u celesta_plot_results.py \
#   --project_title "cervical_09002_raw_arcsinh" \
#   --results_dir "/gpfs/data/proteomics/home/yb2612/results/celesta" \

# python -u celesta_plot_results.py \
#   --project_title "cervical_08153_raw_arcsinh" \
#   --results_dir "/gpfs/data/proteomics/home/yb2612/results/celesta" \

# python -u celesta_plot_results.py \
#   --project_title "cervical_00438_raw_arcsinh" \
#   --results_dir "/gpfs/data/proteomics/home/yb2612/results/celesta" \

# python -u celesta_plot_results.py \
#   --project_title "cervical_07688_raw_arcsinh" \
#   --results_dir "/gpfs/data/proteomics/home/yb2612/results/celesta" \

# python -u celesta_plot_results.py \
#   --project_title "cervical_04738_raw_arcsinh" \
#   --results_dir "/gpfs/data/proteomics/home/yb2612/results/celesta" \

# # ### >1M
# python -u celesta_plot_results.py \
#   --project_title "cervical_00862_raw_arcsinh" \
#   --results_dir "/gpfs/data/proteomics/home/yb2612/results/celesta" \

python -u celesta_plot_results.py \
  --project_title "cervical_10285_raw_arcsinh" \
  --results_dir "/gpfs/data/proteomics/home/yb2612/results/celesta" \

# python -u celesta_plot_results.py \
#   --project_title "cervical_07291_raw_arcsinh" \
#   --results_dir "/gpfs/data/proteomics/home/yb2612/results/celesta" \

wait

echo "All jobs completed."