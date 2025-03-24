import os
import time 
import pdb
from tqdm import tqdm
import numpy as np
import pandas as pd
import torch
from deepcell.applications import Mesmer

def get_cell_segmentations(data_path, tile_size, batch_size, tiles_dir, save_path, channel_names, num_biomarkers, membrane_marker = 'E-cadherin'):
    start_time = time.time()

    os.makedirs(save_path, exist_ok = True) # Create output directory

    matrix_path = os.path.join(save_path, 'matrix.npy') # If matrix already exists, skip
    if os.path.exists(matrix_path):
        print('Full matrix already exists, skipping')
        return

    dataloader = load_dataset(data_path, tile_size, batch_size, tiles_dir, tissue_type='membrane_marker_pos')
    extract_cell_data(dataloader, save_path, num_biomarkers, channel_names, membrane_marker, tile_size, tissue_type='membrane_marker_pos')
    
    dataloader = load_dataset(data_path, tile_size, batch_size, tiles_dir, tissue_type='membrane_marker_neg')
    extract_cell_data(dataloader, save_path, num_biomarkers, channel_names, membrane_marker, tile_size, tissue_type='membrane_marker_neg')

    combine_matrices(save_path, data_path, tiles_dir)

    end_time = time.time()  # Record the end time
    elapsed_time = end_time - start_time

    print("Cell segmentation complete")
    print(f"Time elapsed: {elapsed_time:.2f} seconds")

def load_dataset(data_path, tile_size, batch_size, tiles_dir = None, num_workers=1, tissue_type=''):
    '''loads dataset into a dataloader'''
    input_size = 224
    from torchvision import transforms
    transform_codex = transforms.Compose([
            transforms.ToTensor(),
            transforms.Resize(input_size, interpolation = 2),
            ])
    
    from src.data.imc_dataset_v2 import CANVASDatasetWithLocation, SlidesDataset
    dataset = SlidesDataset(data_path, tile_size = tile_size, tiles_dir = tiles_dir, tissue_type = tissue_type, transform = None, dataset_class = CANVASDatasetWithLocation, use_normalization=False)

    dataloader= torch.utils.data.DataLoader(
        dataset, 
        batch_size=batch_size,
        num_workers=num_workers,
        drop_last=False,
    )
    return dataloader

def load_model():
    ''' loads Mesmer model from deepcell for cell segmentation
        called and used in extract_cell_data function'''
    model = Mesmer(model=None)
    return model

def extract_cell_data(dataloader, output_path, num_biomarkers, channel_names, membrane_marker, tile_size, tissue_type=''): 
    ''''loops through the dataloader to extract:
            1. matrix with intensity values for each biomarker in each cell [shape: (num_cells, num_biomarkers)]
            2. metadata csv with additional cell information including polygons for label image generation in omero [shape: (num_cells, num_features)]
            3. tile_positions, tile_sample_names'''
    
    tissue_output_path = os.path.join(output_path, tissue_type)
    os.makedirs(tissue_output_path, exist_ok=True)
    if os.path.exists(os.path.join(tissue_output_path, f'matrix.npy')):
        print(f'{tissue_type} matrix already exists, skipping')
        return

    model = load_model() # Load segmentation model

    tile_sample_names = [] # On a tile level
    tile_positions = [] # On a tile level 
    metadata_list = []

    num_biomarkers = num_biomarkers
    cell_biomarker_matrix = np.zeros((0, num_biomarkers)) # Initialize matrix

    for idx, batch in enumerate(tqdm(dataloader)):
        img, (labels, locations) = batch
        tile_sample_names.extend(labels)
        tile_positions.extend([loc.numpy() for loc in locations]) 
        
        img_transposed = img.permute(0, 2, 3, 1).numpy()

        img_filtered = img_transposed[:, :, :, [channel_names.index('DAPI'), channel_names.index(membrane_marker)]] 
        img_filtered[:, :, :, 0] = img_filtered[:, :, :, 0] / np.max(img_filtered[:, :, :, 0])
        img_filtered[:, :, :, 1] = img_filtered[:, :, :, 1] / np.max(img_filtered[:, :, :, 1])

        if tissue_type == 'membrane_marker_pos':
            segmentation_prediction = model.predict(img_filtered, image_mpp=0.5)
        else:
            segmentation_prediction = model.predict(img_filtered, image_mpp=0.5, compartment='nuclear', 
                                                postprocess_kwargs_nuclear = {'pixel_expansion': 2})

        segmentation_prediction = np.squeeze(segmentation_prediction, axis=-1)
        
        batch_matrix = np.zeros((0, num_biomarkers)) # Initialize matrix for batch
            
        for i, tile in enumerate(img_transposed):
            slide_id = labels[i] # Cell level
            tile_h = locations[i][0].item() # Cell level
            tile_w = locations[i][1].item() # Cell level
                
            prediction = np.squeeze(segmentation_prediction[i])

            intensity_matrix, metadata = get_tile_intensity(tile, prediction, num_biomarkers,
                                                            slide_id, tile_h, tile_w, tile_size, tissue_type)
            
            batch_matrix = np.vstack((batch_matrix, intensity_matrix))
            metadata_list.extend(metadata)
        
        cell_biomarker_matrix = np.vstack((cell_biomarker_matrix, batch_matrix))
    
    print("cell_biomarker_matrix shape: ", cell_biomarker_matrix.shape)
    metadata_df = pd.DataFrame(metadata_list)
    print("metadata_df shape: ", metadata_df.shape)
    assert cell_biomarker_matrix.shape[0] == metadata_df.shape[0]

    cell_sample_names = metadata_df['slide_id'].values
    print("cell_sample_names length: ", len(cell_sample_names))

    metadata_df.to_csv(os.path.join(tissue_output_path, 'metadata.csv'), index = False)
    np.save(os.path.join(tissue_output_path, 'tile_positions.npy'), np.array(tile_positions))
    np.save(os.path.join(tissue_output_path, 'tile_sample_names.npy'), np.array(tile_sample_names))
    np.save(os.path.join(tissue_output_path, 'matrix.npy'), cell_biomarker_matrix)
    np.save(os.path.join(tissue_output_path, 'cell_sample_names.npy'), np.array(cell_sample_names, dtype=str))

def get_tile_intensity(image, prediction, num_biomarkers, slide_id, tile_h, tile_w, tile_size, tissue_type):
    '''gets information needed on a cell level for each tile
    returns this information for the mean intensity matrix + metadata'''
    from skimage.measure import regionprops, find_contours
    from shapely.geometry import Polygon
    regions = regionprops(intensity_image = image, label_image = prediction)
    num_cells = len(np.unique(prediction)) - 1
    intensity_matrix = np.zeros((num_cells, num_biomarkers))
    metadata = []

    tile_polygon = Polygon([
        (tile_w, tile_h),
        (tile_w + tile_size, tile_h),
        (tile_w + tile_size, tile_h + tile_size),
        (tile_w, tile_h + tile_size),
        (tile_w, tile_h)
    ]).wkt

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

        #extract contour and convert to global coordinates
        contours = find_contours(cell_mask, level=0.5)
        cell_polygon = None

        if contours:
            contour = max(contours, key=len)  # Pick the most detailed contour
            global_coords = [(tile_w + x, tile_h + y) for x, y in contour]
            cell_polygon = Polygon(global_coords).wkt  # Convert to Well-Known Text format
        
        cell_metadata = {
            "cell_label": cell_label,
            "centroid_x": region.centroid[1],  # x coordinate of the centroid
            "centroid_y": region.centroid[0],  # y coordinate of the centroid
            "area": region.area,
            "perimeter": region.perimeter,
            "axis_ratio": axis_ratio,
            "tile_h": int(tile_h),           
            "tile_w": int(tile_w),
            "slide_id": slide_id,
            "tissue_type": tissue_type,
            "polygon": cell_polygon,
            'tile_polygon': tile_polygon
        }

        metadata.append(cell_metadata)
    
    return intensity_matrix, metadata

def load_data(prefix, output_path):
    """Load data for a given prefix (e.g., 'membrane_marker_pos', 'membrane_marker_neg')."""
    base_path = os.path.join(output_path, prefix)
    return {
        'matrix': np.load(os.path.join(base_path, 'matrix.npy')),
        'metadata': pd.read_csv(os.path.join(base_path, 'metadata.csv')),
        'cell_sample_names': np.load(os.path.join(base_path, 'cell_sample_names.npy')),
        'tile_positions': np.load(os.path.join(base_path, 'tile_positions.npy')),
        'tile_sample_names': np.load(os.path.join(base_path, 'tile_sample_names.npy')),
    }

def order_data(matrix, metadata, cell_sample_names, tiles_dir, data_path):
    print("Original data shapes:")
    print(f"Matrix: {matrix.shape}, Metadata: {metadata.shape}, Cell sample names: {cell_sample_names.shape}")

    # Initialize empty containers for reordered data
    reordered_matrix_list = []
    reordered_metadata_list = []
    reordered_cell_sample_names_list = []

    for sample in np.unique(cell_sample_names):
        print(f'Processing sample: {sample}')
        
        # Get sample-specific data
        sample_metadata = metadata[metadata['slide_id'] == sample].copy()
        sample_matrix = matrix[sample_metadata.index.to_numpy()]
        sample_cell_sample_names = cell_sample_names[sample_metadata.index.to_numpy()]

        # Ensure matching shapes after filtering
        assert sample_matrix.shape[0] == sample_metadata.shape[0], \
            f"Mismatch in rows for sample {sample}: {sample_matrix.shape[0]} vs {sample_metadata.shape[0]}"
        
        sample_metadata = sample_metadata.reset_index(drop=True)

        # Load tile positions for that sample
        tile_positions_path = os.path.join(data_path, sample, tiles_dir, 'positions_256.csv')
        sample_tile_positions = pd.read_csv(tile_positions_path)
        
        print('First row of metadata (before reordering):', sample_metadata[['tile_h', 'tile_w']].head(1))
        print('First 5 rows of tile positions file:', sample_tile_positions[['h', 'w']].head())

        # Create tuples for (tile_h, tile_w) and (h, w) for ordering
        sample_metadata['tile_hw'] = list(zip(sample_metadata['tile_h'], sample_metadata['tile_w']))
        sample_tile_positions['hw'] = list(zip(sample_tile_positions['h'], sample_tile_positions['w']))

        # Ensure all tile positions in metadata are found in the tile_positions file
        assert set(sample_metadata['tile_hw']).issubset(set(sample_tile_positions['hw'])), \
            f"Tile positions mismatch for sample {sample}"

        # Use Categorical to align metadata ordering with tile_positions
        sample_metadata['tile_hw'] = pd.Categorical(
            sample_metadata['tile_hw'],
            categories=sample_tile_positions['hw'],
            ordered=True
        )

        # Sort metadata and reorder the matrix accordingly
        ordered_metadata = sample_metadata.sort_values(['tile_hw', 'cell_label'])
        ordered_matrix = sample_matrix[ordered_metadata.index.to_numpy()]

        # Verify that the matrix and metadata are still aligned
        assert ordered_matrix.shape[0] == ordered_metadata.shape[0], \
            f"Mismatch after reordering for sample {sample}"

        print('First row of reordered metadata:', ordered_metadata[['tile_h', 'tile_w']].head(1))

        # Append the reordered data to the containers
        reordered_matrix_list.append(ordered_matrix)
        reordered_metadata_list.append(ordered_metadata)
        reordered_cell_sample_names_list.append(sample_cell_sample_names)
    
    # Concatenate all reordered data at once for better performance
    reordered_matrix = np.vstack(reordered_matrix_list)
    reordered_metadata = pd.concat(reordered_metadata_list, ignore_index=True).drop(columns=['tile_hw'])
    reordered_cell_sample_names = np.hstack(reordered_cell_sample_names_list)

    # Ensure final shapes match expected dimensions
    assert reordered_matrix.shape[0] == reordered_metadata.shape[0] == reordered_cell_sample_names.shape[0], \
        "Final shape mismatch between matrix, metadata, and cell sample names"

    print("Reordered data shapes:")
    print(f"Matrix: {reordered_matrix.shape}, Metadata: {reordered_metadata.shape}, Cell sample names: {reordered_cell_sample_names.shape}")

    return reordered_matrix, reordered_metadata, reordered_cell_sample_names

def save_data(output_path, matrix, metadata, cell_sample_names, tile_positions, tile_sample_names):
    """Save combined data to output path."""
    np.save(os.path.join(output_path, 'matrix.npy'), matrix)
    metadata.to_csv(os.path.join(output_path, 'metadata.csv'), index=True)
    np.save(os.path.join(output_path, 'cell_sample_names.npy'), cell_sample_names)
    np.save(os.path.join(output_path, 'tile_positions.npy'), tile_positions)
    np.save(os.path.join(output_path, 'tile_sample_names.npy'), tile_sample_names)

def combine_matrices(output_path, data_path, tiles_dir):
    # Load data
    membrane_marker_pos = load_data('membrane_marker_pos', output_path)
    membrane_marker_neg = load_data('membrane_marker_pos', output_path)

    # Combine matrices and metadata
    matrix = np.vstack([membrane_marker_pos['matrix'], membrane_marker_neg['matrix']])
    metadata = pd.concat([membrane_marker_pos['metadata'], membrane_marker_neg['metadata']], ignore_index=True)
    cell_sample_names = np.concatenate([membrane_marker_pos['cell_sample_names'], membrane_marker_neg['cell_sample_names']])
    tile_positions = np.concatenate([membrane_marker_pos['tile_positions'], membrane_marker_neg['tile_positions']])
    tile_sample_names = np.concatenate([membrane_marker_pos['tile_sample_names'], membrane_marker_neg['tile_sample_names']])

    reordered_matrix, reordered_metadata, reordered_cell_sample_names = order_data(matrix, metadata, cell_sample_names, tiles_dir, data_path)

    # Save combined data
    save_data(output_path, reordered_matrix, reordered_metadata, reordered_cell_sample_names, tile_positions, tile_sample_names)
