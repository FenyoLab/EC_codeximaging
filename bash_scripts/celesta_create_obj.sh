#!/bin/bash
#SBATCH --partition=fn_medium
#SBATCH --nodes=1
#SBATCH --job-name=celesta_create_obj
#SBATCH --output=/gpfs/data/proteomics/home/yb2612/results/logs/%x_%j.out  # EDIT PATH TO LOGS DIR
#SBATCH --error=/gpfs/data/proteomics/home/yb2612/results/logs/%x_%j.err   # EDIT PATH TO LOGS DIR
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=20GB
#SBATCH --time=48:00:00

source set_up_conda.sh
conda activate celesta

# make sure you run this script from /path/to/bash_scripts
cd ../src/celesta/

# EDIT ARGUMENTS

## first 4 samples
Rscript celesta_create_obj.R \
  --project_title "cervical_10103_raw_arcsinh" \
  --prior_marker_info "/gpfs/data/proteomics/home/yb2612/data/celesta/cervical/prior_marker_info_cervical.csv" \
  --imaging_data "/gpfs/data/proteomics/home/yb2612/data/celesta/cervical/imaging_data_10103_raw.csv" \
  --results_dir "/gpfs/data/proteomics/home/yb2612/results/celesta" \
  --transform_type 1 \

Rscript celesta_create_obj.R \
  --project_title "cervical_34933_raw_arcsinh" \
  --prior_marker_info "/gpfs/data/proteomics/home/yb2612/data/celesta/cervical/prior_marker_info_cervical.csv" \
  --imaging_data "/gpfs/data/proteomics/home/yb2612/data/celesta/cervical/imaging_data_34933_raw.csv" \
  --results_dir "/gpfs/data/proteomics/home/yb2612/results/celesta" \
  --transform_type 1 \

Rscript celesta_create_obj.R \
  --project_title "cervical_28873_raw_arcsinh" \
  --prior_marker_info "/gpfs/data/proteomics/home/yb2612/data/celesta/cervical/prior_marker_info_cervical.csv" \
  --imaging_data "/gpfs/data/proteomics/home/yb2612/data/celesta/cervical/imaging_data_28873_raw.csv" \
  --results_dir "/gpfs/data/proteomics/home/yb2612/results/celesta" \
  --transform_type 1 \

Rscript celesta_create_obj.R \
  --project_title "cervical_02433_raw_arcsinh" \
  --prior_marker_info "/gpfs/data/proteomics/home/yb2612/data/celesta/cervical/prior_marker_info_cervical.csv" \
  --imaging_data "/gpfs/data/proteomics/home/yb2612/data/celesta/cervical/imaging_data_02433_raw.csv" \
  --results_dir "/gpfs/data/proteomics/home/yb2612/results/celesta" \
  --transform_type 1 \

## <100k
Rscript celesta_create_obj.R \
  --project_title "cervical_39367_raw_arcsinh" \
  --prior_marker_info "/gpfs/data/proteomics/home/yb2612/data/celesta/cervical/prior_marker_info_cervical.csv" \
  --imaging_data "/gpfs/data/proteomics/home/yb2612/data/celesta/cervical/imaging_data_39367_raw.csv" \
  --results_dir "/gpfs/data/proteomics/home/yb2612/results/celesta" \
  --transform_type 1 \

Rscript celesta_create_obj.R \
  --project_title "cervical_49411_raw_arcsinh" \
  --prior_marker_info "/gpfs/data/proteomics/home/yb2612/data/celesta/cervical/prior_marker_info_cervical.csv" \
  --imaging_data "/gpfs/data/proteomics/home/yb2612/data/celesta/cervical/imaging_data_49411_raw.csv" \
  --results_dir "/gpfs/data/proteomics/home/yb2612/results/celesta" \
  --transform_type 1 \

## >100k, <1M
Rscript celesta_create_obj.R \
  --project_title "cervical_09002_raw_arcsinh" \
  --prior_marker_info "/gpfs/data/proteomics/home/yb2612/data/celesta/cervical/prior_marker_info_cervical.csv" \
  --imaging_data "/gpfs/data/proteomics/home/yb2612/data/celesta/cervical/imaging_data_09002_raw.csv" \
  --results_dir "/gpfs/data/proteomics/home/yb2612/results/celesta" \
  --transform_type 1 \

Rscript celesta_create_obj.R \
  --project_title "cervical_08153_raw_arcsinh" \
  --prior_marker_info "/gpfs/data/proteomics/home/yb2612/data/celesta/cervical/prior_marker_info_cervical.csv" \
  --imaging_data "/gpfs/data/proteomics/home/yb2612/data/celesta/cervical/imaging_data_08153_raw.csv" \
  --results_dir "/gpfs/data/proteomics/home/yb2612/results/celesta" \
  --transform_type 1 \

Rscript celesta_create_obj.R \
  --project_title "cervical_00438_raw_arcsinh" \
  --prior_marker_info "/gpfs/data/proteomics/home/yb2612/data/celesta/cervical/prior_marker_info_cervical.csv" \
  --imaging_data "/gpfs/data/proteomics/home/yb2612/data/celesta/cervical/imaging_data_00438_raw.csv" \
  --results_dir "/gpfs/data/proteomics/home/yb2612/results/celesta" \
  --transform_type 1 \

Rscript celesta_create_obj.R \
  --project_title "cervical_07688_raw_arcsinh" \
  --prior_marker_info "/gpfs/data/proteomics/home/yb2612/data/celesta/cervical/prior_marker_info_cervical.csv" \
  --imaging_data "/gpfs/data/proteomics/home/yb2612/data/celesta/cervical/imaging_data_07688_raw.csv" \
  --results_dir "/gpfs/data/proteomics/home/yb2612/results/celesta" \
  --transform_type 1 \

Rscript celesta_create_obj.R \
  --project_title "cervical_04738_raw_arcsinh" \
  --prior_marker_info "/gpfs/data/proteomics/home/yb2612/data/celesta/cervical/prior_marker_info_cervical.csv" \
  --imaging_data "/gpfs/data/proteomics/home/yb2612/data/celesta/cervical/imaging_data_04738_raw.csv" \
  --results_dir "/gpfs/data/proteomics/home/yb2612/results/celesta" \
  --transform_type 1 \

## >1M
Rscript celesta_create_obj.R \
  --project_title "cervical_07611_raw_arcsinh" \
  --prior_marker_info "/gpfs/data/proteomics/home/yb2612/data/celesta/cervical/prior_marker_info_cervical.csv" \
  --imaging_data "/gpfs/data/proteomics/home/yb2612/data/celesta/cervical/imaging_data_07611_raw.csv" \
  --results_dir "/gpfs/data/proteomics/home/yb2612/results/celesta" \
  --transform_type 1 \

Rscript celesta_create_obj.R \
  --project_title "cervical_00862_raw_arcsinh" \
  --prior_marker_info "/gpfs/data/proteomics/home/yb2612/data/celesta/cervical/prior_marker_info_cervical.csv" \
  --imaging_data "/gpfs/data/proteomics/home/yb2612/data/celesta/cervical/imaging_data_00862_raw.csv" \
  --results_dir "/gpfs/data/proteomics/home/yb2612/results/celesta" \
  --transform_type 1 \

Rscript celesta_create_obj.R \
  --project_title "cervical_10285_raw_arcsinh" \
  --prior_marker_info "/gpfs/data/proteomics/home/yb2612/data/celesta/cervical/prior_marker_info_cervical.csv" \
  --imaging_data "/gpfs/data/proteomics/home/yb2612/data/celesta/cervical/imaging_data_10285_raw.csv" \
  --results_dir "/gpfs/data/proteomics/home/yb2612/results/celesta" \
  --transform_type 1 \

Rscript celesta_create_obj.R \
  --project_title "cervical_07291_raw_arcsinh" \
  --prior_marker_info "/gpfs/data/proteomics/home/yb2612/data/celesta/cervical/prior_marker_info_cervical.csv" \
  --imaging_data "/gpfs/data/proteomics/home/yb2612/data/celesta/cervical/imaging_data_07291_raw.csv" \
  --results_dir "/gpfs/data/proteomics/home/yb2612/results/celesta" \
  --transform_type 1 \

wait

echo "All jobs completed."