#!/bin/bash
#SBATCH --job-name=create_label_images
#SBATCH --mail-type=FAIL # Mail events (NONE, BEGIN, END, FAIL, ALL)
#SBATCH --ntasks=1
#SBATCH --output=../logs/main_label_images_%j.txt
#SBATCH --error=../logs/main_label_images_err_%j.txt
#SBATCH --mem=50G
#SBATCH --time=4:00:00
#SBATCH --cpus-per-task=1
#SBATCH --partition=cpu_short

cd /gpfs/home/as18894/projects/as18894/FenyoLab/Endometrial/EC_codeximaging
source ~/.bashrc

conda activate omero 
python main_label_images.py