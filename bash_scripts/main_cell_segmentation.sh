#!/bin/bash
#SBATCH --job-name=cell_segmentation
#SBATCH --ntasks=1
#SBATCH --output=../logs/cell_segmentation_%j.txt
#SBATCH --partition gpu4_short,gpu8_short,gpu4_dev,gpu8_dev,gpu4_medium,gpu8_medium,gpu4_long,gpu8_long
#SBATCH --nodes=1
#SBATCH --cpus-per-task=1
#SBATCH --ntasks-per-node=1
#SBATCH --mem=300GB
#SBATCH --time=4:00:00
#SBATCH --gres=gpu:4

source .env
source set_up_conda.sh
module load condaenvs/new/deepcell

cp -r /gpfs/data/proteomics/data/Cervical_mIF/output/data/20250225-Jharna-08153-A1_Scan1.er /gpfs/data/proteomics/data/Cervical_mIF/output/data_new/20250225-Jharna-08153-A1_Scan1.er

cd ..
python main_cell_segmentation.py

rm -r /gpfs/data/proteomics/data/Cervical_mIF/output/data_new/20250225-Jharna-08153-A1_Scan1.er
