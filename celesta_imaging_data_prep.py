import pandas as pd
import os

markers = ["CD31", "E-cadherin", "CD68", "CD163", "MPO", "CD20", "CD3e", "CD8", "Granzyme B", "TOX", "CD4", "FOXP3", "TIM3", "CD45RO"]
metadata_dir = "/gpfs/data/proteomics/home/yb2612/data/cervical_samples"
imaging_data_dir = "/gpfs/data/proteomics/home/yb2612/data/celesta/cervical"

def prep_imaging_data(raw_means_csv, metadata_csv, markers, sample_name):
    # load raw biomarker means, filter to markers of interest
    raw_means = pd.read_csv(raw_means_csv)
    print(" > No of cells:", raw_means.shape[0])
    raw_means_filtered = raw_means[markers]

    # load metadata, filter to abs x, y
    metadata = pd.read_csv(metadata_csv)
    metadata.drop(columns=["absolute_x","absolute_y"], inplace=True)
    metadata["absolute_x"] = metadata["centroid_y"] + metadata["tile_w"]  # FIXED COORDS
    metadata["absolute_y"] = metadata["centroid_x"] + metadata["tile_h"]  # FIXED COORDS
    
    # join xy, raw means
    metadata_xy = metadata[["absolute_x", "absolute_y"]].copy()
    imaging_data = metadata_xy.join(raw_means_filtered)
    imaging_data = imaging_data.rename(columns={"absolute_x": "X", "absolute_y": "Y"})

    return metadata, imaging_data
  
os.chdir(metadata_dir)

for folder in os.listdir():
    folder_path = os.path.join(metadata_dir, folder)
    if os.path.isdir(folder_path):
        # folder name is like 20250225-Jharna-02433-A1_Scan1.er
        try:
            sample_id = folder.split("-")[2]  # get string after 2nd split
            print(f"Sample ID: {sample_id}")
            
            raw_means_csv = os.path.join(folder_path, "raw_biomarker_means.csv")
            metadata_csv = os.path.join(folder_path, f"{folder}_metadata.csv")

            # check if files exist
            if os.path.exists(raw_means_csv):
                print(f" > Found: {raw_means_csv}")
            else:
                print(f" > Missing: {raw_means_csv}")
            
            if os.path.exists(metadata_csv):
                print(f" > Found: {metadata_csv}")
            else:
                print(f" > Missing: {metadata_csv}")
                
        except IndexError:
            print(f"! Could not extract sample ID from folder name: {folder}")

        try:
            metadata_xy, imaging_data = prep_imaging_data(raw_means_csv, metadata_csv, markers, f"{sample_id}_raw")
            
            # save
            metadata_xy_path = os.path.join(folder_path, f"{folder}_metadata_fixed.csv")
            imaging_data_path = f"{imaging_data_dir}/imaging_data_{sample_id}.csv"

            metadata_xy.to_csv(metadata_xy_path, index=False)
            imaging_data.to_csv(imaging_data_path, index=False)

            print(" > Saved metadata and imaging_data csv")
            
        except Exception as e:
            print(" !", e)