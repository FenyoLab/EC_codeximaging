#!/bin/bash
#SBATCH --partition=cpu_medium
#SBATCH --nodes=1
#SBATCH --job-name=celesta_assign_cells
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

# EDIT ARGUMENTS
# ## first 4 samples
# Rscript celesta_assign_cells.R \
#   --project_title "cervical_10103_raw_arcsinh" \
#   --results_dir "/gpfs/data/proteomics/home/yb2612/results/celesta/detailed_cell_types" \

# Rscript celesta_assign_cells.R \
#   --project_title "cervical_34933_raw_arcsinh" \
#   --results_dir "/gpfs/data/proteomics/home/yb2612/results/celesta/detailed_cell_types" \

# Rscript celesta_assign_cells.R \
#   --project_title "cervical_28873_raw_arcsinh" \
#   --results_dir "/gpfs/data/proteomics/home/yb2612/results/celesta/detailed_cell_types" \

# Rscript celesta_assign_cells.R \
#   --project_title "cervical_02433_raw_arcsinh" \
#   --results_dir "/gpfs/data/proteomics/home/yb2612/results/celesta/detailed_cell_types" \

## <100k
# Rscript celesta_assign_cells.R \
#   --project_title "cervical_39367_raw_arcsinh" \
#   --results_dir "/gpfs/data/proteomics/home/yb2612/results/celesta/detailed_cell_types" \

# Rscript celesta_assign_cells.R \
#   --project_title "cervical_49411_raw_arcsinh" \
#   --results_dir "/gpfs/data/proteomics/home/yb2612/results/celesta/detailed_cell_types" \

# ## >100k, <1M
# Rscript celesta_assign_cells.R \
#   --project_title "cervical_09002_raw_arcsinh" \
#   --results_dir "/gpfs/data/proteomics/home/yb2612/results/celesta/detailed_cell_types" \

# Rscript celesta_assign_cells.R \
#   --project_title "cervical_08153_raw_arcsinh" \
#   --results_dir "/gpfs/data/proteomics/home/yb2612/results/celesta/detailed_cell_types" \

# Rscript celesta_assign_cells.R \
#   --project_title "cervical_00438_raw_arcsinh" \
#   --results_dir "/gpfs/data/proteomics/home/yb2612/results/celesta/detailed_cell_types" \

# Rscript celesta_assign_cells.R \
#   --project_title "cervical_07688_raw_arcsinh" \
#   --results_dir "/gpfs/data/proteomics/home/yb2612/results/celesta/detailed_cell_types" \

# Rscript celesta_assign_cells.R \
#   --project_title "cervical_04738_raw_arcsinh" \
#   --results_dir "/gpfs/data/proteomics/home/yb2612/results/celesta/detailed_cell_types" \

# ## >1M

# Rscript celesta_assign_cells.R \
#   --project_title "cervical_00862_raw_arcsinh" \
#   --results_dir "/gpfs/data/proteomics/home/yb2612/results/celesta/detailed_cell_types" \

Rscript celesta_assign_cells.R \
  --project_title "cervical_10285_raw_arcsinh" \
  --results_dir "/gpfs/data/proteomics/home/yb2612/results/celesta/detailed_cell_types" \

# Rscript celesta_assign_cells.R \
#   --project_title "cervical_07291_raw_arcsinh" \
#   --results_dir "/gpfs/data/proteomics/home/yb2612/results/celesta/detailed_cell_types" \

wait

echo "All jobs completed."