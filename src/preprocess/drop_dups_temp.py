import pandas as pd
import numpy as np
import os
import glob

parent_dir = "/gpfs/data/proteomics/data/Cervical_mIF/output/data/"

# List only directories (folders) in the path
folder_list = [f for f in os.listdir(parent_dir) if os.path.isdir(os.path.join(parent_dir, f))]

# Loop over each folder
for folder in folder_list:
    folder_path = os.path.join(parent_dir, folder)
    print(f"Processing folder: {folder_path}")
    csv_files = glob.glob(f"{folder_path}/tiles/*.csv")
    print(csv_files)
    for filly in csv_files:
        csv_temp = pd.read_csv(filly)
        csv_temp_cleaned = csv_temp.drop_duplicates()
        old_file_name = os.path.splitext(filly)[0] + "_with_duplicates.csv" 
        print(f"Saving: {old_file_name}")
        csv_temp.to_csv(old_file_name)
        print(f"Saving: {filly}")
        csv_temp_cleaned.to_csv(filly)

for folder in folder_list:
    folder_path = os.path.join(parent_dir, folder)
    print(f"Processing folder: {folder_path}")
    csv_files = glob.glob(f"{folder_path}/tiles/*.csv")
    filtered_files = [f for f in csv_files if "_duplicates" not in f]
    print(filtered_files)
    for filly in filtered_files:
        csv_temp = pd.read_csv(filly, index_col=0)
        csv_temp = csv_temp.loc[:,["h","w"]]
        csv_temp_cleaned = csv_temp.drop_duplicates()
        old_file_name = os.path.splitext(filly)[0] + "_with_duplicates.csv" 
        print(f"Saving: {old_file_name}")
        csv_temp.to_csv(old_file_name)
        print(f"Saving: {filly}")
        csv_temp_cleaned.to_csv(filly)





