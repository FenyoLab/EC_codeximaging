import os
import zarr
import numpy as np
from skimage.measure import block_reduce
from skimage.transform import resize
from skimage.io import imsave
import pandas as pd
from skimage.draw import polygon
from PIL import Image
import pdb
import cv2
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon


def run_rois():

    data_path = '/gpfs/data/proteomics/projects/Endometrial_mIF/EC_codeximaging_results/out_256/data'
    slide_id = '20231003-2630-3P_Scan1'
    tiles_dir = 'tiles_11_13' 
    ROI_path = '/gpfs/data/proteomics/projects/Endometrial_mIF/EC_codeximaging_results/preprocessing/qptiff_annotations'
    selected_region = ['tumor', 'TUMOR', 'tumor involving adenomyosis']

    get_rois_for_positions(data_path, slide_id, tiles_dir, ROI_path, tile_size=256, selected_region=selected_region)


def get_rois_for_positions(data_path: str, slide_id: str, tiles_dir: None, ROI_path: str, tile_size: int = 256, selected_region: str = None):
    '''Get the ROIs for corresponding tiles for a given slide'''
    
    print("slideID: ", slide_id)

    output_path = os.path.join(f'{data_path}/{slide_id}/{tiles_dir}')
    os.makedirs(output_path, exist_ok=True)

    if os.path.exists(os.path.join(output_path, f'positions_with_rois_{tile_size}.csv')):
        print(f"{slide_id} positions exists.. moving on to next slide")
        return None 

    print('Reading slide...')
    slide_path = f'{data_path}/{slide_id}/data.zarr'
    slide = zarr.open(slide_path, mode='r')
    
    _, slide_height, slide_width = slide.shape
    print(f'Slide_shape: {slide.shape}')

    print('Reading positions...')
    positions_file = os.path.join(output_path, f'positions_{tile_size}.csv')
    positions = pd.read_csv(positions_file, index_col=0)
    print(f'Positions shape: {positions.shape}')

    all_files = os.listdir(ROI_path)
    ROIfile_name = [f for f in all_files if slide_id in f]
    print("ROI file name: ", ROIfile_name)
    ROIs_path = os.path.join(ROI_path, ROIfile_name[0])
    ROIdata = pd.read_csv(ROIs_path)
    
    if selected_region is not None: 
        data_subset = ROIdata.loc[ROIdata.Text.isin(selected_region)]
        data_subset_coords = data_subset['all_points']
        data_subset_coords_list = data_subset_coords.str.split(' ', expand=False)
        data_subset_roi_ids = data_subset['Id']
        print("data_subset_roi_ids: ", data_subset_roi_ids)

        if len(data_subset_roi_ids) == 1:
            #add a new column to positions with the roi_id
            positions['roi_id'] = data_subset_roi_ids.iloc[0]
            print("positions with roi id shape: ", positions.shape)
            print("positions with roi id: ", positions.head())
            positions_with_rois_file = os.path.join(output_path, f'positions_with_rois_{tile_size}.csv')
            positions.to_csv(positions_with_rois_file)
            return None
        
        else:
            roi_positions = []  # Initialize once, outside the loop
            for roi_id, ROI in zip(data_subset_roi_ids, data_subset_coords_list):
                if roi_id == 1230022:
                    continue
                # Convert the list of strings to a NumPy array of floats (if it's in the format 'x,y')
                data_subset_coords_array = np.array([list(map(float, coord.split(','))) for coord in ROI])
                # Create a Polygon from the coordinates
                roi_polygon = Polygon(data_subset_coords_array)
            
                # For each position, check if the top-left coordinates of the tile fall within the ROI
                for _, row in positions.iterrows():
                    top_left_x, top_left_y = row['w'], row['h']  # Assuming the CSV has 'h' and 'w' columns for positions
                    tile_polygon = Polygon([
                        (top_left_x, top_left_y),
                        (top_left_x + tile_size, top_left_y),
                        (top_left_x + tile_size, top_left_y + tile_size),
                        (top_left_x, top_left_y + tile_size)
                    ])
                    #breakpoint()
        
                    if roi_polygon.intersects(tile_polygon):
                        #print(f'Tile at position ({top_left_x}, {top_left_y}) intersects with ROI {roi_id}')
                        roi_positions.append([top_left_y, top_left_x, roi_id])

            # At this point, roi_for_positions contains all the roi_ids
            roi_positions_df = pd.DataFrame(roi_positions, columns=['top_left_y', 'top_left_x', 'roi_id'])
            #rename top_left_x to w and top_left_y to h
            roi_positions_df.rename(columns={'top_left_y': 'h', 'top_left_x': 'w'}, inplace=True)
            roi_positions_df = roi_positions_df.sort_values(by=['h', 'w'], ascending=[True, True]).reset_index(drop=True)
            print("roi_positions_df shape: ", roi_positions_df.shape)
            print("positions shape: ", positions.shape)
            positions_with_roi_check = positions[['h', 'w']].isin(roi_positions_df[['h', 'w']].to_dict(orient='list')).all(axis=1)
            not_in_roi_positions = positions[~positions_with_roi_check]
            print("# of coord pairs not in both positions files:", len(not_in_roi_positions))
            print(positions.head()) 
            print(roi_positions_df.head())
            #breakpoint()

            if roi_positions_df.shape[0] == positions.shape[0]:
                positions_with_rois_file = os.path.join(output_path, f'positions_with_rois_{tile_size}.csv')
                roi_positions_df.to_csv(positions_with_rois_file)
            
            else:
                # Check if there are any duplicates in the positions
                duplicates = roi_positions_df.duplicated(subset=['h', 'w'], keep=False)
                if duplicates.any():
                    print(roi_positions_df[duplicates])
                    #breakpoint()
                else:
                    print("No duplicates found")
                    #breakpoint()
                
                # Check if there are any missing positions
                positions_set = set(zip(positions['h'], positions['w']))
                roi_positions_set = set(zip(roi_positions_df['h'], roi_positions_df['w']))
                missing_positions_set = positions_set - roi_positions_set
                print("# of missing positions: ", len(missing_positions_set), missing_positions_set)

                missing_positions_df = pd.DataFrame(list(missing_positions_set), columns=['h', 'w'])
                positions.columns.values[0] = 'original_index'
                missing_positions_indices = positions.merge(missing_positions_df, on=['h', 'w'], how='inner')['original_index'].tolist()
                print("Indices of missing positions:", missing_positions_indices)
                breakpoint()

                positions_with_rois_file = os.path.join(output_path, f'positions_with_rois_{tile_size}.csv')
                roi_positions_df.to_csv(positions_with_rois_file)

run_rois()