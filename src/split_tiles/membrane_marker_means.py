import os
import sys
import torch
import numpy as np
from types import SimpleNamespace
import matplotlib.pyplot as plt

sys.path.append('../..')
from utils import helper

def get_top5_means_membrane_marker(data_path, tile_size, batch_size, tiles_dir, channel_names, mean_data_dir, membrane_marker_name = 'Ecadherin'):

    top5_mean_data_path=os.path.join(mean_data_dir, 'top5percent_means.npy')
    if os.path.exists(top5_mean_data_path):
        print('Means of top 5 percent of membrane marker tiles already exist, skipping')
        return

    os.makedirs(mean_data_dir, exist_ok=True)
    membrane_marker_index = channel_names.index(membrane_marker_name)
    print(f'{membrane_marker_name} index:', membrane_marker_index)
    #load dataset
    dataloader = load_dataset(data_path, tile_size, batch_size, tiles_dir)

    top5percent_means = []
    sample_names=[]
    tile_positions=[]
    
    for idx,batch in enumerate(dataloader):
        if idx % 100 == 0:
            print("Batch index:", idx)
        
        img, (labels, locations) = batch
        img_filtered = img[:, membrane_marker_index, :, :] 

        means = []
        for n in range(len(img_filtered)): #iterate through each batch
            tile = img_filtered[n,:,:]
            #print(tile.shape)
            top5_cutoff = np.percentile(tile,95)
            #print(top5_cutoff)
            top5_values = tile[tile >=top5_cutoff]
            #print(len(top5_values))
            mean_top5 = torch.mean(top5_values).item()
            #print(mean_top5)
            means.append(mean_top5)
        
        sample_names.append(labels)
        tile_positions.append(locations)
        top5percent_means.append(means)

    top5percent_means_tensors = [torch.tensor(batch) for batch in top5percent_means]
    stacked_tensor_top5_means = torch.cat(top5percent_means_tensors) #this creates one large array (not separated by batches
    top5_means_arr=stacked_tensor_top5_means.numpy()
    print(top5_means_arr.shape)

    #stack tile_positions and create array 
    stacked_tensor_tile_positions=torch.cat(tile_positions)
    tile_positions_arr=stacked_tensor_tile_positions.numpy()
    print(tile_positions_arr.shape)

    #stack sample_names and create array 
    sample_names_all = [item for sublist in sample_names for item in sublist] #this combines the list of IDs which all have different sizes because of the varying batch size into 1 list 
    sample_names_arr = np.array(sample_names_all)
    print(sample_names_arr.shape)
    
    np.save(top5_mean_data_path, top5_means_arr)
    np.save(os.path.join(mean_data_dir, 'sample_names.npy'), sample_names_arr)
    np.save(os.path.join(mean_data_dir, 'tile_positions.npy'), tile_positions_arr)

def load_dataset(data_path, tile_size, batch_size, tiles_dir, num_workers = 1):
    '''loads dataset into a dataloader'''
    input_size = 224
    from torchvision import transforms
    transform_codex = transforms.Compose([
            transforms.ToTensor(),
            transforms.Resize(input_size, interpolation = 2),
            ])
    
    #from src.data.imc_dataset import CANVASDatasetWithLocation, SlidesDataset
    from ..data.imc_dataset import CANVASDatasetWithLocation, SlidesDataset #check this works
    dataset = SlidesDataset(data_path, tile_size = tile_size, tiles_dir = tiles_dir, transform = None, dataset_class = CANVASDatasetWithLocation, use_normalization=False)

    dataloader= torch.utils.data.DataLoader(
        dataset, 
        batch_size=batch_size,
        num_workers=num_workers,
        drop_last=False,
    )
    return dataloader

if __name__ == "__main__":
    main()