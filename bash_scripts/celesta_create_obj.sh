#!/bin/bash
#SBATCH --partition=cpu_short
#SBATCH --nodes=1
#SBATCH --job-name=celesta_create_obj
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
Rscript celesta_create_obj.R \
  --project_title "cervical_10103_raw_arcsinh" \
  --prior_marker_info "/gpfs/data/proteomics/home/yb2612/data/celesta/cervical/prior_marker_info_cervical.csv" \
  --imaging_data "/gpfs/data/proteomics/home/yb2612/data/celesta/cervical/imaging_data_10103_raw.csv" \
  --results_dir "/gpfs/data/proteomics/home/yb2612/results/celesta" \
  --transform_type 1 \

Rscript celesta_create_obj.R \
  --project_title "cervical_28873_raw_arcsinh" \
  --prior_marker_info "/gpfs/data/proteomics/home/yb2612/data/celesta/cervical/prior_marker_info_cervical.csv" \
  --imaging_data "/gpfs/data/proteomics/home/yb2612/data/celesta/cervical/imaging_data_28873_raw.csv" \
  --results_dir "/gpfs/data/proteomics/home/yb2612/results/celesta" \
  --transform_type 1 \

Rscript celesta_create_obj.R \
  --project_title "cervical_34933_raw_arcsinh" \
  --prior_marker_info "/gpfs/data/proteomics/home/yb2612/data/celesta/cervical/prior_marker_info_cervical.csv" \
  --imaging_data "/gpfs/data/proteomics/home/yb2612/data/celesta/cervical/imaging_data_34933_raw.csv" \
  --results_dir "/gpfs/data/proteomics/home/yb2612/results/celesta" \
  --transform_type 1 \

Rscript celesta_create_obj.R \
  --project_title "cervical_02433_raw_arcsinh" \
  --prior_marker_info "/gpfs/data/proteomics/home/yb2612/data/celesta/cervical/prior_marker_info_cervical.csv" \
  --imaging_data "/gpfs/data/proteomics/home/yb2612/data/celesta/cervical/imaging_data_02433_raw.csv" \
  --results_dir "/gpfs/data/proteomics/home/yb2612/results/celesta" \
  --transform_type 1 \

wait

echo "All jobs completed."