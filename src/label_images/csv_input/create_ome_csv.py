import os
import numpy as np
import pandas as pd

def create_ome_csv(sample, seg_data_path, save_path, channel_names):
    '''Function to create a csv file with polygons and marker intensities for a given sample
    Function is called in omero_label_image function in upload_label_image.py
    Inputs: sample - str, name of the sample
            seg_data_path - str, path to the segmentation data - contains matrix with intensities and metadata with polygons
            save_path - str, path to save the csv file (in research drive)
            channel_names - list of str, names of the channels
    Outputs: table_filename - str, name of the csv file created'''

    metadata = pd.read_csv(os.path.join(seg_data_path, 'metadata.csv'), index_col = 0)
    matrix = np.load(os.path.join(seg_data_path, 'matrix.npy'))

    assert metadata.shape[0] == matrix.shape[0], 'Number of rows in metadata and matrix do not match'

    sample_metadata = metadata[metadata['slide_id'] == sample].copy()
    sample_metadata['object'] = np.arange(1, len(sample_metadata) + 1)
    sample_matrix = matrix[sample_metadata.index]

    assert sample_metadata.shape[0] == sample_matrix.shape[0], 'Number of rows in sample_metadata and sample_matrix do not match'

    #want only certain metadata columns
    sample_metadata = sample_metadata[['object', 'polygon', 'tile_polygon']].reset_index(drop=True)
    polygon_and_markers_df = add_markers(sample_metadata, sample_matrix, channel_names)

    table_filename = 'polygons_and_markers.csv'
    polygon_and_markers_df.to_csv(os.path.join(save_path, table_filename), index=False)

    return table_filename

def add_markers(polygon_df, matrix, channel_names):

    matrix_df = pd.DataFrame(matrix, columns=channel_names)
    print('polygon_df.shape:', polygon_df.shape)
    print('matrix_df.shape:', matrix_df.shape)
    assert matrix_df.shape[0] == polygon_df.shape[0], 'Number of rows in matrix_df and polygon_df do not match'

    # Concatenate along columns (axis=1)
    polygon_and_marker_df = pd.concat([polygon_df, matrix_df], axis=1)
    print('polygon_and_marker_df.shape:', polygon_and_marker_df.shape)
    print(polygon_and_marker_df.head())

    return polygon_and_marker_df
