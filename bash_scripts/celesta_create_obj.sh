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
  Rscript celesta_create_obj.R \
    --project_title "cervical_${sample}_raw_arcsinh" \
    --prior_marker_info "/gpfs/data/proteomics/home/yb2612/data/celesta/cervical/prior_marker_info_cervical_full.csv" \
    --imaging_data "/gpfs/data/proteomics/home/yb2612/data/celesta/cervical/imaging_data_${sample}_raw.csv" \
    --results_dir "/gpfs/data/proteomics/home/yb2612/results/celesta/detailed_cell_types" \
    --transform_type 1 
done

wait
echo "All jobs completed."