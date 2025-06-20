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

### ---------- SAMPLES TO RUN -------------
### add sample IDs to the array below

samples=(
  "10103"
  "28873"
)

### ---------- LOOP THROUGH SAMPLES -------------
### execute script for each sample chosen above
### edit arguments as needed

for sample in "${samples[@]}"; do
  echo "Running sample: $sample"
  python -u celesta_plot_exp_prob.py \
    --project_title "cervical_${sample}_raw_arcsinh" \
    --results_dir "/gpfs/data/proteomics/home/yb2612/results/celesta/detailed_cell_types"
done

wait
echo "All jobs completed."