import pandas as pd
import os
import glob
import yaml

with open("../../config/config_celesta_to_omero_prep.yaml", "r") as f:
    config = yaml.safe_load(f)

phenotype_clusters_path = config["paths"]["phenotype_clusters"]
celesta_results_dir = config["paths"]["celesta_results_dir"]
output_dir = config["paths"]["output_dir"]
thresholds_dict = config["thresholds_dict"]

print("All results saved to:", output_dir)

phenotype_clusters = pd.read_csv(phenotype_clusters_path, index_col=0)
# extract short_id from long sample name, e.g., "02433" from "20250225-Jharna-02433-A1_Scan1.er"
phenotype_clusters["short_id"] = phenotype_clusters["slide_id"].apply(lambda x: x.split("-")[2])
phenotype_clusters["short_id"].value_counts()
# remove all rows where short id is 07611
phenotype_clusters = phenotype_clusters[phenotype_clusters["short_id"] != "07611"]

for table_name, threshold in thresholds_dict.items():
    print(f"\nProcessing table: {table_name} with threshold: {threshold}")

    pc_copy = phenotype_clusters.copy()  # create copy of phenotype_clusters
    # init col for cell types
    pc_copy["cell_type"] = None
    
    # process each sample
    for short_id in pc_copy["short_id"].unique():
        folder_name = f"cervical_{short_id}_raw_arcsinh"
        folder_path = os.path.join(celesta_results_dir, folder_name)
    
        if not os.path.isdir(folder_path):
            print(f" ! Folder not found for short_id: {short_id}")
            continue
    
        # find celesta final assignment file
        file_pattern = os.path.join(folder_path, f"*{threshold}_final_cell_type_assignment.csv")
        matches = glob.glob(file_pattern)
    
        if len(matches) != 1:
            print(f" ! Expected 1 assignment file, found {len(matches)} for {short_id}")
            continue
    
        # read celesta final cell type assignments
        celesta_df = pd.read_csv(matches[0])
        final_cell_types = celesta_df["Final cell type"].values
    
        # get phenotype_clusters rows for this short_id
        mask = pc_copy["short_id"] == short_id
        n_rows = mask.sum()
    
        if len(final_cell_types) != n_rows:
            print(f" ! Row mismatch for {short_id}: phenotype_clusters has {n_rows}, celesta has {len(final_cell_types)}")
            continue
    
        # assign cell types, preserving order
        pc_copy.loc[mask, "cell_type"] = final_cell_types

        print(f" > {short_id}")
    
    # save
    print(" > Saving OMERO table...")
    output_path = os.path.join(output_dir, f"celesta_{table_name}.csv")
    valid_pc_copy = pc_copy[pc_copy["cell_type"].notna()].copy()
    valid_pc_copy.to_csv(output_path, index=False)
    # pc_copy.to_csv(output_path, index=False)
    print(" > Saved!")