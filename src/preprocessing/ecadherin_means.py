import os
import sys
import torch
import numpy as np
from types import SimpleNamespace

sys.path.append('..')
from src.cell_segmentation import load_dataset
sys.path.append('../..')
from utils import helper

def main():
    config_yaml= '/gpfs/home/as18894/projects/as18894/FenyoLab/Endometrial/EC_codeximaging/config/configb.yaml'
    run_config = helper.load_yaml_file(config_yaml)
    config = SimpleNamespace(**run_config)

    save_path = os.path.join(config.segementation_data_dir, config.preprocessing)

    get_top5_means_ecadherin(data_path = config.data_dir, tile_size = config.tile_size, batch_size = config.batch_size,
                            channel_names = config.channel_names, save_path = save_path)


def get_top5_means_ecadherin(data_path, tile_size, batch_size, channel_names, mean_data_dir):

    top5_mean_data_path=os.path.join(save_path, 'top5percent_means.npy')
    if os.path.exists(top5_mean_data_path):
        print('Means of top 5 percent of ecadherin tiles already exist, skipping')
        return

    os.makedirs(save_path, exist_ok=True)
    ecadherin_index = channel_names.index('Ecadherin')
    #load dataset
    dataloader = load_dataset(data_path, tile_size, batch_size)

    top5percent_means = []
    sample_names=[]
    tile_positions=[]
    
    for idx,batch in enumerate(dataloader):
        if idx % 1000 == 0:
            print("Batch index:", idx)
            
        img, (labels, locations) = batch
        img_filtered = img[:, ecadherin_index, :, :] 

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
    np.save(os.path.join(save_path, 'sample_names.npy'), sample_names_arr)
    np.save(os.path.join(save_path, 'tile_positions.npy'), tile_positions_arr)

if __name__ == "__main__":
    main()