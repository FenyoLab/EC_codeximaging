# Description: Helper functions for project
import os
import zarr
import pandas as pd
import numpy as np  
import pdb

def load_zarr_w_channel(root_path, sample_name):
    sample_zarr_path = f'{root_path}/{sample_name}/data.zarr'
    channel_path = f'{root_path}/{sample_name}/channels.csv'
    data = zarr.open(sample_zarr_path, mode='r')
    channels = pd.read_csv(channel_path)
    return data, channels

def load_tile_info(root_path, sample_name, tile_size):
    tiles = pd.read_csv(f'{root_path}/{sample_name}/tiles/positions_{tile_size}.csv', index_col = 0)
    return tiles

def read_channel_file(channel_file):
    if channel_file:
        with open(channel_file, 'r') as f:
            channels = f.read().splitlines()
    else:
        channels = None
    return channels

def get_file_name_list(root_path, file_ext):
    file_names = []
    for file_name in os.listdir(root_path):
        if file_name.endswith(file_ext):
            file_names.append(file_name[:-len(file_ext)-1])
    return file_names

def load_yaml_file(yaml_file):
    import yaml
    with open(yaml_file, 'r') as f:
        yaml_dict = yaml.safe_load(f)
    return yaml_dict

def load_channel_yaml_file(color_file):
    color_dict = load_yaml_file(color_file)
    for channel, color in color_dict.items():
        print(f'{channel}: {color}')
    return color_dict

def visualize_color_yaml_file(color_file, save_path):
    color_save_path = f'{save_path}/marker_color.png'
    import numpy as np
    from canvas.visualization.core import subplots
    color_dict = load_channel_yaml_file(color_file)
    fig, ax = subplots(1, 1)
    for channel, color in color_dict.items():
        color = np.array(color) / 255
        ax.scatter(0, 0, color=color, label=channel)
    ax.scatter(0, 0, color=[0, 0, 0], s = 50)
    # Use white text for legend
    ax.legend(loc='center', bbox_to_anchor=(2, 0), title='Channels', title_fontsize='large', shadow=True, fancybox=True)
    for text in ax.get_legend().get_texts():
        text.set_color('white')
    # Hide scatter plot
    ax.axis('off')
    # Dark background for entire figure
    fig.patch.set_facecolor('black')
    fig.savefig(color_save_path, bbox_inches='tight')

def vis_multiplex(data, channels, color_dict, strength_dict = None):
    pdb.set_trace()
    # Initialize black image
    image = np.zeros((data.shape[1], data.shape[2], 3))
    data = np.array(data).astype(np.float32) / 255
    for channel, color in color_dict.items():
        channel_index = np.where(np.array(channels) == channel)[0][0]
        if strength_dict:
            strength = strength_dict[channel]
        else:
            strength = 1
        # From 0-255 to 0-1
        color = np.array(color) / 255
        for channel_i in range(3):
            image[:, :, channel_i] = np.maximum(image[:, :, channel_i], image[channel_i] * color[channel_i] * strength)
    image = (image * 255).clip(0, 255).astype(np.uint8)
    return image
