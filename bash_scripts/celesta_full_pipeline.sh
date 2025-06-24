#!/bin/bash
#SBATCH --partition=fn_medium
#SBATCH --nodes=1
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=30GB
#SBATCH --time=48:00:00

sample=$1

source set_up_conda.sh
conda activate celesta

cd ../src/celesta/

echo "Running sample: $sample"

# edit arguments
Rscript celesta_full_pipeline.R \
    --project_title "cervical_${sample}_raw_arcsinh" \
    --prior_marker_info "/gpfs/data/proteomics/home/yb2612/data/celesta/cervical/prior_marker_info_cervical_full.csv" \
    --imaging_data "/gpfs/data/proteomics/home/yb2612/data/celesta/cervical/imaging_data_${sample}_raw.csv" \
    --results_dir "/gpfs/data/proteomics/home/yb2612/results/celesta/detailed_cell_types" \
    --transform_type 1 