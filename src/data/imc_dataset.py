import os

import zarr
import numpy as np
import pandas as pd
import torch.utils.data as data
import pdb

from src.data.slide_dataset import SlideDataset
#??? If this is the first thing being imported, does that mean it is being called?? Or does it only get called once NPYDataset is called?

#when a class definition includes another class in parenthesis, it indicates the the class is inheriting all the attributes and methods from the class in parenthesis
#ex) CANVASDataset(ZarrDataset): CANVASDataset is inheriting ev

class NPYDataset(SlideDataset):

    def __init__(self, root_path = None, tile_size = None, transform = None, lazy = True):
        super().__init__(root_path, tile_size, transform) #SlideDataset
        self.slide = self.read_slide(root_path, lazy)
        self.read_counter = 0

    def read_slide(self, file_path, lazy):
        ''' Read numpy file on disk mapped to memory '''
        numpy_path = f'{file_path}/data/core.npy'
        if lazy:
            slide = np.load(numpy_path, mmap_mode = 'r', allow_pickle = True)
        else:
            slide = np.load(numpy_path, allow_pickle = True)
        return slide

    def read_region(self, pos_x, pos_y, width, height):
        ''' Read a numpy slide region '''
        #print(pos_x)
        #print(pos_y)
        #pdb.set_trace()
        region_np = self.slide[:, pos_x:pos_x+width, pos_y:pos_y+height].copy()
        #print("tile coordinates: ", pos_x,pos_y)
        #print("tile shape:",region_np.shape) #(53, 128, 128)
        # Swap channel to last dimension
        region_np = region_np.swapaxes(0, 1).swapaxes(1, 2)
        region = region_np.swapaxes(0, 1) # Change to numpy format
        self.read_counter += 1
        return region

    def get_slide_dimensions(self):
        print("get_slide_dimensions")
        ''' Get slide dimensions '''
        return self.slide.shape[0:2]

    # Generate thumbnail
    def generate_thumbnail(self, scaling_factor):
        tile_cache_size = 50 * scaling_factor
        cache = self.reduce_by_tile(self.slide, tile_cache_size, scaling_factor)
        thumbnail = cache.swapaxes(0, 1).astype(np.uint8)
        return thumbnail

    def reduce_by_tile(self, slide, tile_size, scaling_factor):
        from skimage.measure import block_reduce
        from tqdm import tqdm
        dims = self.get_slide_dimensions()
        print(dims)
        pdb.set_trace()
        cache = np.zeros((dims[0] // scaling_factor, dims[1] // scaling_factor, 4), dtype = np.uint8)
        for x in tqdm(range(0, dims[0], tile_size)):
            for y in range(0, dims[1], tile_size):
                tile = self.read_region(x, y, tile_size, tile_size).swapaxes(0, 1)
                reduced_tile = block_reduce(tile, block_size=(scaling_factor, scaling_factor, 1), func=np.mean)
                x_reduced = x // scaling_factor
                y_reduced = y // scaling_factor
                x_end = min(x_reduced + tile_size // scaling_factor, cache.shape[0])
                y_end = min(y_reduced + tile_size // scaling_factor, cache.shape[1])
                cache[x_reduced:x_end, y_reduced:y_end, :] = reduced_tile[:x_end - x_reduced, :y_end - y_reduced, :]
                self.slide = self.read_slide(self.root_path, lazy = True)
        return cache

    def save_thumbnail(self, scaling_factor = 32):
        from skimage.io import imsave
        ''' Save thumbnail of the slide '''
        #print("save_thumbnail")
        thumbnail = self.generate_thumbnail(scaling_factor)
        os.makedirs(f'{self.root_path}/thumbnails', exist_ok=True)
        imsave(f'{self.root_path}/thumbnails/npy_{scaling_factor}_bin.png', thumbnail)

class ZarrDataset(NPYDataset):

    def read_slide(self, file_path, lazy = True):
        ''' Read zarr file on disk '''
        zarr_path = f'{file_path}/data.zarr'
        slide = zarr.open(zarr_path, mode = 'r')
        return slide

#ZarrDataset is the superclass of CANVASDataset... it is being inherited by CANVASDataset
#Instances of CANVASDataset will have access to the attributes and methods defined in ZarrDataset
#CANVASDataset is a subclass of ZarrDataset
class CANVASDataset(ZarrDataset): #once we get to this function, the image has already been normalized! 
#also transform is set in SlidesDataset in main_pretrain.py 
    def __init__(self, root_path, tile_size, common_channel_names : [str], transform = None, lazy = True):
        super().__init__(root_path, tile_size, transform) #this is a call to the superclass constructor
        self.root_path = root_path
        self.slide = self.read_slide(root_path, lazy)
        self.read_counter = 0
        self.common_channel_names = common_channel_names
        self.channel_idx = self.get_channel_idx(common_channel_names)

    def __getitem__(self, index):
        image, label, x, y, img_id = super().__getitem__(index)
        #print('CANVASDataset')
        #print(image)
        # Move channel to first dimension
        if not self.channel_idx is None:
            image = image[self.channel_idx, :, :]
        dummy_label = self.root_path.split('/')[-1]
        return image, dummy_label

    def get_channel_idx(self, channel_names):
        ''' Get channel index from channel names '''
        channel_df = pd.read_csv(f'{self.root_path}/channels.csv')
        channel_dict = dict(zip(channel_df['marker'], channel_df['channel']))
        channel_idx = [channel_dict[channel_name] for channel_name in channel_names]
        return channel_idx

class CANVASDatasetWithLocation(CANVASDataset):

    def __getitem__(self, index):
        image, sample_label = super().__getitem__(index)
        #print('CANVASDatasetWithLocation')
        #print(image)
        #breakpoint()
        location = self.tile_pos[index]
        return image, (sample_label, location)

#this is where is starts!! It is called in main_pretrain.py
class SlidesDataset(data.Dataset): #this is inheriting data.Dataset from torch!!
    ''' Dataset for a list of slides '''

    def __init__(self, slides_root_path = None, tile_size = None, transform = None, dataset_class = None, use_normalization = True):
        self.slides_root_path = slides_root_path
        self.tile_size = tile_size
        self.transform = transform

        # Get id and path for all slides
        slide_ids = self.get_slide_paths(slides_root_path)
        self.common_channel_names = self.get_common_channel_names(self.slides_root_path)
        self.slides_dict, self.lengths = self.get_slides(slide_ids, dataset_class, self.common_channel_names)
        self.mean = None
        self.std = None
        self.use_normalization = use_normalization
        self.mean, self.std = self.get_normalization_stats()
        #print(self.mean)
        #print(self.std)

    def __getitem__(self, index):
        for slide_idx, (slide_id, slide) in enumerate(self.slides_dict.items()):
            #print("we are in getitem of SlidesDataset")
            #print(slide_idx,slide_id) #ex)0 AMP_1154
            if index < self.lengths[slide_idx]:
                image, label = slide[index]
                #print("Image pre mean normalization")
                #print(image.shape)
                #print(torch.min(image))
                #print(torch.max(image))
                
                # Check if already initialized
                if not self.use_normalization:
                    #print(image)
                    return image, label
                if not self.mean is None: #if self.mean is not NONE... it's only generated if the image is getting normalized!!!
                    #print("image is being mean normalized")
                    image = (image - self.mean) / self.std #this is where the mean normalization occurs
                #print("SlidesDataset")
                #print(image)
                #print("Image post mean normalization")
                #print(image.shape)
                #print(torch.min(image))
                #print(torch.max(image))
                #breakpoint()
                return image, label
            else:
                index -= self.lengths[slide_idx]

    def __len__(self):
        return sum(self.lengths)

    def get_common_channel_names(self, root_path):
        with open(f'{root_path}/common_channels.txt', 'r') as f:
            channel_names = f.read().splitlines()
        return channel_names

    def get_normalization_stats(self):
        ''' Get normalization stats across samples '''
        from tqdm import tqdm
        mean = 0
        std = 0
        stats_path = f'{self.slides_root_path}/../stats_blank'
        # Load mean and std if exists
        if os.path.exists(f'{stats_path}/mean.npy') and os.path.exists(f'{stats_path}/std.npy'):
            print("using previously generated mean and std numpy files")
            mean = np.load(f'{stats_path}/mean.npy')
            std = np.load(f'{stats_path}/std.npy')
        else:
            print("generating new stats files")
            # Generate random samples with seed
            rand_state = np.random.RandomState(42)
            rand_idices = rand_state.randint(0, len(self), size = 10000) #MH: change size from 1000 --> 10000
            #print(len(rand_idices))
            
            n_samples = 0
            for i in tqdm(rand_idices):
                image, label  = self.__getitem__(i) #this gets the random tile and its corresponding label 
                mean += image.mean(axis = (1, 2)) #this calculates the mean and std of that specific tile and accumulates the values over all of random tiles
                std += image.std(axis = (1, 2))
                n_samples += 1
            mean /= n_samples #divides the total mean across all samples by the number of samples to get average mean 
            std /= n_samples
            mean = mean[:, np.newaxis, np.newaxis] #This is done to make sure that mean and std have the same shape as the images, making it easier to use them for normalization.
            std = std[:, np.newaxis, np.newaxis]
            # Save stats
            os.makedirs(stats_path, exist_ok = True)
            print("saving stats")
            np.save(f'{stats_path}/mean.npy', mean)
            np.save(f'{stats_path}/std.npy', std)
        return mean, std

    def get_slide_paths(self, slides_root_path):
        ''' Get slides from a directory '''
        slide_ids = []
        slide_channels = []
        slide_channel_dicts = []
        for slide_id in os.listdir(slides_root_path):
            if os.path.isdir(os.path.join(slides_root_path, slide_id)) and not slide_id.startswith('.') and 'V' not in slide_id:
                mat = zarr.open(f'{slides_root_path}/{slide_id}/data.zarr', mode = 'r')
                #print("slideshape: ",mat.shape) #(54, 7488, 20032)->for one of the kidney slides 
                channel_df = pd.read_csv(f'{slides_root_path}/{slide_id}/channels.csv')
                channel_dict = dict(zip(channel_df['channel'], channel_df['marker']))
                slide_channels.append(mat.shape[0])
                slide_channel_dicts.append(channel_dict)
                slide_ids.append(slide_id)
        # Check if all slides have the same channels
        print(f'Found {len(slide_ids)} slides with {slide_channels} channels')

        common_channels_path = f'{slides_root_path}/common_channels.txt'
        if not os.path.exists(common_channels_path):
            common_channels = self.get_common_channels(slide_channel_dicts)
            # Save common channels as txt file
            with open(common_channels_path, 'w') as f:
                for channel in common_channels:
                    f.write(f'{channel}\n')
            if len(set(slide_channels)) > 1 or len(set([tuple(channel_dict.values()) for channel_dict in slide_channel_dicts])) > 1:
                raise Exception(f'All slides must have the same channels, common channel file is written to {common_channels_path}, PLEASE REVIEW')
            else:
                raise Exception(f'All slides DO have the same channels, common channel file is written to {common_channels_path}, PLEASE REVIEW and remove unnecessary channels')
        #print(slide_ids)
        return slide_ids

    def get_common_channels(self, slide_channel_dicts):
        ''' Get common channels for a list of slides '''
        common_markers = [] # Channel dict: channel -> marker
        for channel_dict in slide_channel_dicts:
            common_markers.append(set(channel_dict.values()))
        common_markers = set.intersection(*common_markers)
        #print(common_markers)
        return common_markers

    def get_slides(self, slide_ids, dataset_class, common_channel_names):
        ''' Get slides from a list of slide ids '''
        from tqdm import tqdm
        slides_dict = {}
        lengths = []
        print('Loading slides...')
        for slide_id in tqdm(slide_ids):
            #print("we are in get_slides")
            #print(slide_id)
            slide_path = os.path.join(self.slides_root_path, slide_id)
            slide = dataset_class(slide_path, self.tile_size, common_channel_names, self.transform) #dataset_class is CANVASDataset! This is where we go to that function
            #self.transform refers to transform_codex in main_pretrain.py!
            slides_dict[slide_id] = slide
            lengths.append(len(slide))
        return slides_dict, lengths
