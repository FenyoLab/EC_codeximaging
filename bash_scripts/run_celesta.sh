#!/bin/bash
#SBATCH --partition=gpu8_short                  # Node
#SBATCH --nodes=1                             # 1 node
#SBATCH --job-name=run_celesta         # Job name
#SBATCH --output=/gpfs/home/yb2612/yb2612_fenyo/results/logs/%x_%j.out  # Redirect stdout log to logs directory
#SBATCH --error=/gpfs/home/yb2612/yb2612_fenyo/results/logs/%x_%j.err   # Redirect stderr log to logs directory
#SBATCH --cpus-per-task=1                     # Run on a single CPU
#SBATCH --mem-per-cpu=50GB                     # Memory limit
#SBATCH --time=12:00:00                       # Max time for short


# edit this to activate the correct conda environment
source /gpfs/data/hammelllab/yumi/lib/yumi_miniconda/etc/profile.d/conda.sh
conda activate celesta
echo "conda activated"

# edit path to folder containing celesta script
cd /gpfs/home/yb2612/yb2612_fenyo/scripts/R

# edit arguments
Rscript celesta_phenotyping.R \
  --project_title "endometrial_1T_raw_noDAPI_adjusted" \
  --prior_marker_info "/gpfs/home/yb2612/yb2612_fenyo/data/celesta/endometrial_test/prior_marker_info_endometrial_noDAPI.csv" \
  --imaging_data "/gpfs/home/yb2612/yb2612_fenyo/data/celesta/endometrial_test/imaging_data_1T_raw_noDAPI.csv" \
  --output_dir "/gpfs/home/yb2612/yb2612_fenyo/results/celesta" \
  --transform_type 1 \
  --high_anchor 1 0.7 0.9 0.7 0.5 0.7 0.7 0.8 0.5 0.8 \
  --high_iter 1 0.6 0.8 0.6 0.5 0.6 0.6 0.7 0.5 0.7 \
  --low_anchor 1 1 1 1 1 1 1 1 1 1 \
  --low_iter 1 1 1 1 1 1 1 1 1 1

wait

echo "All jobs completed."