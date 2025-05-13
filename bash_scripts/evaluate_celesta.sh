#!/bin/bash
#SBATCH --partition=gpu8_short                  # Node
#SBATCH --nodes=1                             # 1 node
#SBATCH --job-name=run_celesta         # Job name
#SBATCH --output=/gpfs/home/yb2612/yb2612_fenyo/results/logs/%x_%j.out  # Redirect stdout log to logs directory
#SBATCH --error=/gpfs/home/yb2612/yb2612_fenyo/results/logs/%x_%j.err   # Redirect stderr log to logs directory
#SBATCH --cpus-per-task=1                     # Run on a single CPU
#SBATCH --mem-per-cpu=50GB                     # Memory limit
#SBATCH --time=12:00:00                       # Max time for short

source set_up_conda.sh
conda activate celesta

cd ../

# edit arguments
Rscript evaluate_celesta.R \
  --project_title "endometrial_1T_raw_arcsinh_initial" \
  --celesta_results "/gpfs/home/yb2612/yb2612_fenyo/results/celesta/endometrial_1T_raw_arcsinh_initial/endometrial_1T_raw_arcsinh_initial_final_cell_type_assignment.csv" \
  --metadata "/gpfs/home/yb2612/yb2612_fenyo/data/celesta/endometrial_test/metadata_1T.csv" \
  --output_dir "/gpfs/home/yb2612/yb2612_fenyo/results/evaluate_celesta" \

wait

echo "All jobs completed."