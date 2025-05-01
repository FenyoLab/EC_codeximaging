#!/bin/bash
#SBATCH --partition=gpu8_short                  # Node
#SBATCH --nodes=1                             # 1 node
#SBATCH --job-name=run_celesta         # Job name
#SBATCH --output=/gpfs/home/yb2612/yb2612_fenyo/results/logs/%x_%j.out  # Redirect stdout log to logs directory
#SBATCH --error=/gpfs/home/yb2612/yb2612_fenyo/results/logs/%x_%j.err   # Redirect stderr log to logs directory
#SBATCH --cpus-per-task=1                     # Run on a single CPU
#SBATCH --mem-per-cpu=50GB                     # Memory limit
#SBATCH --time=12:00:00                       # Max time for short


cd /gpfs/home/yb2612/yb2612_fenyo/scripts/R
# Rscript celesta_phenotyping.R endometrial_1T_raw_noDAPI /gpfs/home/yb2612/yb2612_fenyo/data/celesta/endometrial_test/prior_marker_info_endometrial_noDAPI.csv /gpfs/home/yb2612/yb2612_fenyo/data/celesta/endometrial_test/imaging_data_1T_raw_noDAPI.csv 1
Rscript celesta_phenotyping.R endometrial_3P_raw_noDAPI /gpfs/home/yb2612/yb2612_fenyo/data/celesta/endometrial_test/prior_marker_info_endometrial_noDAPI.csv /gpfs/home/yb2612/yb2612_fenyo/data/celesta/endometrial_test/imaging_data_3P_raw_noDAPI.csv 1