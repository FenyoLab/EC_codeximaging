#!/bin/bash
#SBATCH --partition=fn_medium
#SBATCH --nodes=1
#SBATCH --job-name=celesta_full_pipeline
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
Rscript celesta_full_pipeline.R \
  --project_title "endometrial_1T_raw_noarcsinh_full" \
  --prior_marker_info "/gpfs/data/proteomics/home/yb2612/data/celesta/endometrial_test/prior_marker_info_endometrial_noDAPI.csv" \
  --imaging_data "/gpfs/data/proteomics/home/yb2612/data/celesta/endometrial_test/imaging_data_1T_raw_noDAPI.csv" \
  --results_dir "/gpfs/data/proteomics/home/yb2612/results/celesta" \
  --transform_type 0 \
  # --high_anchor 1 0.8 0.9 0.7 0.7 0.7 0.7 0.5 0.5 0.8 \
  # --high_iter 1 0.7 0.8 0.6 0.6 0.6 0.6 0.5 0.5 0.7 \
  # --low_anchor 1 1 1 1 1 1 1 1 1 1 \
  # --low_iter 1 1 1 1 1 1 1 1 1 1

wait

echo "All jobs completed."