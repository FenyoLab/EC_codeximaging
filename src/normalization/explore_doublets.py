import numpy as np
import pandas as pd

#load in metadata 
metadata_path = '/media/ssd02/mh6486/Endometrial/as18894/cell_segmentation/out_test/metadata.csv'
metadata_df = pd.read_csv(metadata_path, index_col = 'cell_id')
print("metadata_df shape: ", metadata_df.shape)

#print column names 
print("metadata_df columns: ", metadata_df.columns)