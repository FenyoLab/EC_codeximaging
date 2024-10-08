import os
import time 
import pdb
from tqdm import tqdm

import numpy as np
import pandas as pd
import torch
from deepcell.applications import Mesmer

os.environ.update({"DEEPCELL_ACCESS_TOKEN": "<token-from-users.deepcell.org>"})

def get_cell_segmentations(data_path, tile_size, batch_size, save_path, num_biomarkers):
    start_time = time.time()

    os.makedirs(save_path, exist_ok = True) #create output directory

    matrix_path = os.path.join(save_path, 'matrix.npy') #if matrix already exists, skip
    if os.path.exists(matrix_path):
        print('Full matrix already exists, skipping')
        return

    dataloader = load_dataset(data_path, tile_size, batch_size, tissue_type='ecad+_')
    get_matrix(dataloader, save_path, num_biomarkers, tissue_type='ecad+_')
    
    dataloader = load_dataset(data_path, tile_size, batch_size, tissue_type='ecad-_')
    get_matrix(dataloader, save_path, num_biomarkers, tissue_type='ecad-_')

    combine_matrices(save_path)

    end_time = time.time()  # Record the end time
    elapsed_time = end_time - start_time

    print("Cell segmentation complete")
    print(f"Time elapsed: {elapsed_time:.2f} seconds")

def load_dataset(data_path, tile_size, batch_size, num_workers = 1, tissue_type=''):
    '''loads dataset into a dataloader'''
    input_size = 224
    from torchvision import transforms
    transform_codex = transforms.Compose([
            transforms.ToTensor(),
            transforms.Resize(input_size, interpolation = 2),
            ])
    
    #from ..data.imc_dataset import CANVASDatasetWithLocation, SlidesDataset
    from src.data.imc_dataset_v2 import CANVASDatasetWithLocation, SlidesDataset
    dataset = SlidesDataset(data_path, tile_size = tile_size, tissue_type = tissue_type, transform = None, dataset_class = CANVASDatasetWithLocation, use_normalization=False)

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

def get_matrix(dataloader, output_path, num_biomarkers, tissue_type=''): 
    ''''loops through the dataloader to extract:
            1. matrix with intensity values for each biomarker in each cell [shape: (num_cells, num_biomarkers)]
            2. metadata csv with additional cell information [shape: (num_cells, num_features)]
            3. tile_positions, tile_sample_names, segmentation_masks to be used in omero downstream analysis'''
    
    tissue_output_path = os.path.join(output_path, tissue_type)
    os.makedirs(tissue_output_path, exist_ok=True)
    if os.path.exists(os.path.join(tissue_output_path, f'matrix.npy')):
        print(f'{tissue_type} matrix already exists, skipping')
        return

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
        #if labels[0] != '20231019-0413-3D_Scan1':
        #    continue
        tile_sample_names.extend(labels)
        tile_positions.extend([loc.numpy() for loc in locations]) 
        
        img_transposed = img.permute(0, 2, 3, 1).numpy()
        img_filtered = img_transposed[:, :, :, [0, 3]] 
        
        if tissue_type == 'ecad+_':
            segmentation_prediction = model.predict(img_filtered, image_mpp=0.5)
        else:
            segmentation_prediction = model.predict(img_filtered, image_mpp=0.5, compartment='nuclear', 
                                                postprocess_kwargs_nuclear = {'pixel_expansion': 2})


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
                                                            slide_id, tile_x, tile_y, tissue_type)
            #add tissue type 
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

    metadata_df.to_csv(os.path.join(tissue_output_path, 'metadata.csv'), index=True)
    np.save(os.path.join(tissue_output_path, 'tile_positions.npy'), np.array(tile_positions))
    np.save(os.path.join(tissue_output_path, 'tile_sample_names.npy'), np.array(tile_sample_names))
    np.save(os.path.join(tissue_output_path, 'segmentation_masks.npy'), np.array(segmentation_masks))
    np.save(os.path.join(tissue_output_path, 'matrix.npy'), cell_biomarker_matrix)
    np.save(os.path.join(tissue_output_path, 'cell_sample_names.npy'), np.array(cell_sample_names, dtype=str))


def get_tile_intensity(image, prediction, num_biomarkers, slide_id, tile_x, tile_y, tissue_type):
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
            "slide_id": slide_id,
            "tissue_type": tissue_type
        }

        metadata.append(cell_metadata)
    
    return intensity_matrix, metadata

def combine_matrices(output_path):

    #load endo data
    ecad_pos_matrix=np.load(os.path.join(output_path, 'ecad+_', 'matrix.npy'))
    ecad_pos_metadata=pd.read_csv(os.path.join(output_path, 'ecad+_', 'metadata.csv'))
    ecad_pos_cell_sample_names=np.load(os.path.join(output_path, 'ecad+_', 'cell_sample_names.npy'))
    ecad_pos_tile_positions=np.load(os.path.join(output_path, 'ecad+_', 'tile_positions.npy'))
    ecad_pos_tile_sample_names=np.load(os.path.join(output_path, 'ecad+_', 'tile_sample_names.npy'))
    ecad_pos_segmentation_masks=np.load(os.path.join(output_path, 'ecad+_', 'segmentation_masks.npy'))

    #load myo data
    ecad_neg_matrix=np.load(os.path.join(output_path, 'ecad-_', 'matrix.npy'))
    ecad_neg_metadata=pd.read_csv(os.path.join(output_path, 'ecad-_', 'metadata.csv'))
    ecad_neg_cell_sample_names=np.load(os.path.join(output_path, 'ecad-_', 'cell_sample_names.npy'))
    ecad_neg_tile_positions=np.load(os.path.join(output_path, 'ecad-_', 'tile_positions.npy'))
    ecad_neg_tile_sample_names=np.load(os.path.join(output_path, 'ecad-_', 'tile_sample_names.npy'))
    ecad_neg_segmentation_masks=np.load(os.path.join(output_path, 'ecad-_', 'segmentation_masks.npy'))

    #combine data
    matrix=np.vstack((ecad_pos_matrix, ecad_neg_matrix))
    metadata=pd.concat([ecad_pos_metadata, ecad_neg_metadata], ignore_index=True)
    cell_sample_names=np.concatenate((ecad_pos_cell_sample_names, ecad_neg_cell_sample_names))
    tile_positions=np.concatenate((ecad_pos_tile_positions, ecad_neg_tile_positions))
    tile_sample_names=np.concatenate((ecad_pos_tile_sample_names, ecad_neg_tile_sample_names))
    segmentation_masks=np.concatenate((ecad_pos_segmentation_masks, ecad_neg_segmentation_masks))

    np.save(os.path.join(output_path, 'matrix.npy'), matrix)
    metadata.to_csv(os.path.join(output_path, 'metadata.csv'), index=True)
    np.save(os.path.join(output_path, 'cell_sample_names.npy'), cell_sample_names)
    np.save(os.path.join(output_path, 'tile_positions.npy'), tile_positions)
    np.save(os.path.join(output_path, 'tile_sample_names.npy'), tile_sample_names)
    np.save(os.path.join(output_path, 'segmentation_masks.npy'), segmentation_masks)
