import os
import time 
import pdb
from tqdm import tqdm

import numpy as np
import pandas as pd
import torch
from deepcell.applications import Mesmer

def get_cell_segmentations(data_path, tile_size, batch_size, save_path, num_biomarkers, output_suffix = 'cell_marker_matrix'):
    start_time = time.time()

    output_path = f'{save_path}/{output_suffix}' #create output directory 
    os.makedirs(output_path, exist_ok = True)

    matrix_path = os.path.join(output_path, 'matrix.npy') #if matrix already exists, skip
    if os.path.exists(matrix_path):
        print('Matrix already exists, skipping')
        return

    dataloader = load_dataset(data_path, tile_size, batch_size)
    get_matrix(dataloader, output_path, num_biomarkers)

    end_time = time.time()  # Record the end time
    elapsed_time = end_time - start_time

    print("Cell segmentation complete")
    print(f"Time elapsed: {elapsed_time:.2f} seconds")

def load_dataset(data_path, tile_size, batch_size, num_workers = 8):
    '''loads dataset into a dataloader'''
    input_size = 224
    from torchvision import transforms
    transform_codex = transforms.Compose([
            transforms.ToTensor(),
            transforms.Resize(input_size, interpolation = 2),
            ])
    
    #from ..data.imc_dataset import CANVASDatasetWithLocation, SlidesDataset
    from src.data.imc_dataset import CANVASDatasetWithLocation, SlidesDataset
    dataset = SlidesDataset(data_path, tile_size = tile_size, transform = None, dataset_class = CANVASDatasetWithLocation, use_normalization=False)

    dataloader= torch.utils.data.DataLoader(
        dataset, 
        batch_size=batch_size,
        num_workers=num_workers,
        drop_last=False,
    )
    return dataloader

def load_model():
    ''' loads Mesmer model from deepcell for cell segmentation
        called and used in get_matrix function'''
    model = Mesmer(model=None)
    return model

def get_matrix(dataloader, output_path, num_biomarkers, output_suffix = 'cell_marker_matrix'): 
    ''''loops through the dataloader to extract:
            1. matrix with intensity values for each biomarker in each cell [shape: (num_cells, num_biomarkers)]
            2. metadata csv with additional cell information [shape: (num_cells, num_features)]
            3. tile_positions, tile_sample_names, segmentation_masks to be used in omero downstream analysis'''

    model = load_model() #load segmentation model

    tile_sample_names = [] #on a tile level
    tile_positions = [] # on a tile level 
    segmentation_masks = [] # on a tile level 
    metadata_list = []  # am i doing list? 

    num_biomarkers = num_biomarkers #num_biomarkers = 36
    cell_biomarker_matrix = np.zeros((0, num_biomarkers)) #initialize matrix

    for idx, batch in enumerate(tqdm(dataloader)):
        #if idx > 2: #for testing purposes
        #    break
        #print("Batch number: ", idx)
        img, (labels, locations) = batch
        tile_sample_names.extend(labels)
        tile_positions.extend([loc.numpy() for loc in locations]) 
        
        img_transposed = img.permute(0, 2, 3, 1).numpy()
        img_filtered = img_transposed[:, :, :, [0, 3]] 
        segmentation_prediction = model.predict(img_filtered, image_mpp=0.5)  
        #print("segmentation_prediction shape: ", segmentation_prediction.shape)

        segmentation_prediction = np.squeeze(segmentation_prediction, axis=-1)
        #print("segmentation_prediction squeezed shape: ", segmentation_prediction.shape)
        
        segmentation_masks.extend(segmentation_prediction)

        batch_matrix = np.zeros((0, num_biomarkers)) #initialize matrix for batch
            
        for i, tile in enumerate(img_transposed):
            slide_id = labels[i] #cell level
            tile_x = locations[i][0].item() #cell level
            tile_y = locations[i][1].item() #cell level
                
            prediction = np.squeeze(segmentation_prediction[i])

            intensity_matrix, metadata = get_tile_intensity(tile, prediction, num_biomarkers,
                                                            slide_id, tile_x, tile_y)
            
            #print("intensity_matrix shape: ", intensity_matrix.shape)
            #print("metadata length: ", len(metadata))
            
            batch_matrix = np.vstack((batch_matrix, intensity_matrix))
            metadata_list.extend(metadata)
        
        cell_biomarker_matrix = np.vstack((cell_biomarker_matrix, batch_matrix))
    
    print("cell_biomarker_matrix shape: ", cell_biomarker_matrix.shape)
    metadata_df = pd.DataFrame(metadata_list)
    print("metadata_df shape: ", metadata_df.shape)
    assert cell_biomarker_matrix.shape[0] == metadata_df.shape[0]

    cell_sample_names = metadata_df['slide_id'].values
    print("cell_sample_names length: ", len(cell_sample_names))

    metadata_df.to_csv(os.path.join(output_path, 'metadata.csv'), index=False)
    np.save(os.path.join(output_path, 'tile_positions.npy'), np.array(tile_positions))
    np.save(os.path.join(output_path, 'tile_sample_names.npy'), np.array(tile_sample_names))
    np.save(os.path.join(output_path, 'segmentation_masks.npy'), np.array(segmentation_masks))
    np.save(os.path.join(output_path, 'matrix.npy'), cell_biomarker_matrix)
    np.save(os.path.join(output_path, 'cell_sample_names.npy'), np.array(cell_sample_names, dtype=str))


def get_tile_intensity(image, prediction, num_biomarkers, slide_id, tile_x, tile_y):
    '''gets information needed on a cell level for each tile
    returns this information for the mean intensity matrix + metadata'''
    from skimage.measure import regionprops
    regions = regionprops(intensity_image = image, label_image = prediction)
    num_cells = len(np.unique(prediction)) - 1
    intensity_matrix = np.zeros((num_cells, num_biomarkers))
    metadata = []

    for region in regions:
        cell_label = region.label
        cell_mask = prediction == cell_label
        
        for channel in range(num_biomarkers):
            channel_intensity = image[..., channel]
            mean_intensity = np.mean(channel_intensity[cell_mask])
            intensity_matrix[cell_label - 1, channel] = mean_intensity
        
        axis_minor_length = region.axis_minor_length
        epsilon = 1e-10  # Small number to avoid division by zero
        axis_ratio = region.axis_major_length / (axis_minor_length if axis_minor_length > epsilon else epsilon)
        
        cell_metadata = {
            "cell_label": cell_label,
            "centroid_x": region.centroid[1],  # x coordinate of the centroid
            "centroid_y": region.centroid[0],  # y coordinate of the centroid
            "area": region.area,
            "perimeter": region.perimeter,
            "axis_ratio": axis_ratio,
            "tile_x": int(tile_x),
            "tile_y": int(tile_y),
            "slide_id": slide_id
        }

        metadata.append(cell_metadata)
    
    return intensity_matrix, metadata

if __name__ == '__main__':
    get_cell_segmentations(
        data_path='/media/ssd02/mh6486/Endometrial/CANVAS_v2/canvas/out_256/data',
        save_path='/media/ssd02/mh6486/Endometrial/as18894/cell_segmentation/out',
        tile_size=256,
        batch_size=64
    )