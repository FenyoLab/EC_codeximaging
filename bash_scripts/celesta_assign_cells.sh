#!/bin/bash
#SBATCH --partition=cpu_medium
#SBATCH --nodes=1
#SBATCH --job-name=med_assign_cells
#SBATCH --output=/gpfs/data/proteomics/home/yb2612/results/logs/%x_%j.out  # EDIT PATH TO LOGS DIR
#SBATCH --error=/gpfs/data/proteomics/home/yb2612/results/logs/%x_%j.err   # EDIT PATH TO LOGS DIR
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=20GB
#SBATCH --time=24:00:00

source set_up_conda.sh
conda activate celesta

# make sure you run this script from /path/to/bash_scripts
cd /gpfs/home/yb2612/yb2612_fenyo/CC_codeximaging/bash_scripts
cd ../src/celesta/

### ---------- SAMPLES TO RUN -------------
### add sample IDs to the array below

samples=(
  "08153"
  "09002"
  "02433"
  "07688"
  "00438"
  "04738"
)

### ---------- LOOP THROUGH SAMPLES -------------
### execute script for each sample chosen above
### edit arguments as needed

for sample in "${samples[@]}"; do
  echo "Running sample: $sample"
  Rscript celesta_assign_cells.R \
    --project_title "cervical_${sample}_raw_arcsinh" \
    --results_dir "/gpfs/data/proteomics/home/yb2612/results/celesta/detailed_cell_types" \
    --high_anchor 0.7 0.7 0.9 0.7 0.7 0.7 0.8 0.7 0.7 0.7 0.7 0.7 0.7 0.7 \
    --high_iter 0.5 0.5 0.8 0.5 0.5 0.5 0.7 0.5 0.5 0.5 0.5 0.5 0.5 0.5
done

wait

echo "All jobs completed."