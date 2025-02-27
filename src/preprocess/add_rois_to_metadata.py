import os 
import numpy as np
import pandas as pd

def add_rois_to_metadata(metadata_path, roi_dir, tiles_dir, output_file):
    metadata = pd.read_csv(metadata_path, index_col=0)
    print('Original metadata shape:', metadata.shape)

    updated_metadata = []

    for sample in np.unique(metadata['slide_id'].values):
        print(f'Processing sample {sample}')
        sample_metadata = metadata[metadata['slide_id'] == sample].copy()

        sample_rois = pd.read_csv(os.path.join(roi_dir, sample, tiles_dir, 'positions_with_rois_256.csv'), index_col=0)

        # Merge ROI data with sample metadata based on matching tile_x to h and tile_y to w
        sample_metadata = sample_metadata.merge(
            sample_rois.rename(columns={'h': 'tile_x', 'w': 'tile_y'}),
            on=['tile_x', 'tile_y'],
            how='left'
        )

        column_order = ['cell_label', 'centroid_x', 'centroid_y', 'area', 'perimeter', 'axis_ratio', 'tile_x', 'tile_y', 'slide_id', 'roi_id', 'tissue_type']
        sample_metadata = sample_metadata[column_order]

        updated_metadata.append(sample_metadata)
    
    updated_metadata_df = pd.concat(updated_metadata)
    print('Updated metadata shape:', updated_metadata_df.shape)
    updated_metadata_df.to_csv(output_file)

save_path = '/gpfs/data/proteomics/projects/Endometrial_mIF/EC_codeximaging_results'
metadata_path = os.path.join(save_path, 'raw_segmentation_data/metadata.csv')
roi_dir = os.path.join(save_path, 'out_256/data')
tiles_dir = 'tiles_11_13'
output_file = os.path.join(save_path, 'raw_segmentation_data/metadata_with_rois.csv')

add_rois_to_metadata(metadata_path, roi_dir, tiles_dir, output_file)
