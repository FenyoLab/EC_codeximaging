#!/bin/bash
#SBATCH --partition=cpu_short
#SBATCH --nodes=1
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=5GB
#SBATCH --time=12:00:00

sample=$1

source set_up_conda.sh
conda activate celesta

cd ../src/celesta/

echo "Running sample: $sample"

# edit arguments
python -u celesta_plot_interactive_assignments.py \
  --project_title "cervical_${sample}_raw_arcsinh" \
  --results_dir "/gpfs/data/proteomics/home/yb2612/results/celesta/detailed_cell_types"
