import importlib
import os
#import torch
import numpy as np


def convert_to_float(image):
    if image.max() > 1:
        image = image / 255.
    return image

def convert_to_8bit(image):
    if image.max() > 1:
        image = image / image.max()
    image = (image * 255).astype(np.uint8) # Convert to 8-bit
    return image

def rescale_image(image, percentile=(2, 98)):
    from skimage.exposure import rescale_intensity
    scaled_image = rescale_intensity(image, out_range=(0, 1), 
                              in_range=tuple(np.percentile(image, percentile)))  
    return scaled_image

def convert_to_hed(image, enhance=[0, 1, 2], percentile=None):
    from skimage.color import rgb2hed, hed2rgb
    hed = rgb2hed(image[:, :, 0:3])
    #h = hed[:, :, 0]
    if enhance is not None:
        if percentile is None:
            percentile = (0, 100)
        scaled_channels = []
        for i in range(hed.shape[2]):
            channel = hed[:, :, i]
            if i in enhance:
                scaled_channel = rescale_image(channel, percentile=percentile)
            else:
                scaled_channel = channel
            scaled_channels.append(scaled_channel)
        scaled_hed = np.stack(scaled_channels, axis=-1)   
    return scaled_hed

def grid_idx(x=3, y=2):
    x_idx = [f'x{i}' for i in range(x)]
    y_idx = [f'y{i}' for i in range(y)]
    return [x+y for y in y_idx for x in x_idx]

def rgb2hed_transform(arr, conv_matrix, gpu=True):
        if gpu:
            import cupy as cp
            arr_cls = cp
        else:
            arr_cls = np
        #print(arr.shape)
        arr = arr.astype(arr_cls.float16)
        arr = arr_cls.multiply(arr, 1.0 / 255, dtype=arr_cls.float16)
        arr_cls.maximum(arr, 1e-6, out=arr)
        log_adjust = arr_cls.log(1e-6)
        arr = arr_cls.einsum('ijk,kl->ijl', (arr_cls.log(arr) / log_adjust), conv_matrix)
        arr_cls.maximum(arr, 0, out=arr)
        arr = arr_cls.multiply(arr, 255)
        arr = arr.astype(arr_cls.uint8)
        return arr

def customized_rgb2hed(rgb, chunk_size=1000):
    """
    Modified from skimage: 
    """
    from scipy import linalg
    import cupy as cp
    from tqdm import tqdm
    rgb_from_hed = np.array([[0.65, 0.70, 0.29], [0.07, 0.99, 0.11], [0.27, 0.57, 0.78]],dtype=np.float16)
    hed_from_rgb = linalg.inv(rgb_from_hed)
    
    conv_matrix = cp.asarray(hed_from_rgb)

    # Initialize an output array if you plan to store the entire processed image
    stains = np.empty_like(rgb)

    # Process the image in chunks
    for start in tqdm(range(0, rgb.shape[0], chunk_size), 
                      desc="Processing Image Chunks", ascii=' =',
                      bar_format='{l_bar}{bar:10}{r_bar}'):
        end = start + chunk_size
        chunk_cp = cp.asarray(rgb[start:end])
        chunk_cp = rgb2hed_transform(chunk_cp, conv_matrix, gpu=True)
        stains[start:end] = cp.asnumpy(chunk_cp)
        # Explicitly free GPU memory if desired
        del chunk_cp
        cp.get_default_memory_pool().free_all_blocks()
   
    return stains


def parallel_rgb2hed(rgb, num_processes=4, num_chunks=32):
    """
    With cpu acceleration
    """
    from scipy import linalg
    from multiprocessing import Pool
    from tqdm import tqdm

    rgb_from_hed = np.array([[0.65, 0.70, 0.29], [0.07, 0.99, 0.11], [0.27, 0.57, 0.78]],dtype=np.float16)
    hed_from_rgb = linalg.inv(rgb_from_hed)
    conv_matrix = np.asarray(hed_from_rgb)

    chunks = np.array_split(rgb, num_chunks, axis=0)
    with Pool(num_processes) as pool:
        # Prepare arguments for each process
        # Map process_chunk to the chunks
        args = [(chunk, conv_matrix, False) for chunk in chunks]
        result_list = list(tqdm(pool.starmap(rgb2hed_transform, args), desc="Processing Image Chunks", ascii=' =',
                      bar_format='{l_bar}{bar:10}{r_bar}'))
    
    return np.concatenate(result_list, axis=0)


def data_split(df,
               id='beaker_id',
               stratify='label',
               split_ratio=(0.8, 0.1, 0.1),
               return_df=True,
               seed=42):

    print('Using {} as id column.'.format(str(id)))
    print('Split ratio: ' + str(split_ratio))
    levels = df[stratify].unique()
    levels.sort()
    trn = []
    val = []
    tst = []
    trn_sizes = []
    val_sizes = []
    tst_sizes = []
    np.random.seed(seed)
    seeds = np.random.randint(low=0, high=1000000, size=len(levels))

    for i, level in enumerate(levels):    # stratified splits
        ids = df.loc[df[stratify] == level][id].unique()
        print('{} unique ids in class {}'.format(str(len(ids)), str(level)))
        
        val_size = round(len(ids)*split_ratio[1])    # math.floor(len(ids)*split_ratio[1])
        tst_size = round(len(ids)*split_ratio[2])    # math.floor(len(ids)*split_ratio[2])
        trn_size = len(ids) - (val_size + tst_size)

        trn_sizes.append(trn_size)
        val_sizes.append(val_size)
        tst_sizes.append(tst_size)

        np.random.seed(seeds[i])    
        np.random.shuffle(ids)
        
        trn.append(ids[:trn_size])
        val.append(ids[trn_size: (trn_size + val_size)])
        tst.append(ids[(trn_size + val_size):])
        
    print('Training samples: ' + str(trn_sizes))
    print('Validation samples: ' + str(val_sizes))
    print('Testing samples: ' + str(tst_sizes))


    print('Collapsing ids in each split.')
    trn = np.concatenate(trn)
    val = np.concatenate(val)
    tst = np.concatenate(tst)

    if return_df:
        df['split'] = 'trn'
        df.loc[df[id].isin(val), 'split'] = 'val'
        df.loc[df[id].isin(tst), 'split'] = 'tst'
        
        return df
    else:
        return trn, val, tst
    

def import_with_str(module_name, object_name):
    module = importlib.import_module(module_name)
    obj = getattr(module, object_name)
    return obj


def get_img_in_dir(root_dir):
    imgs = []
    for beaker_id in os.listdir(root_dir):
        samples = os.listdir(os.path.join(root_dir, beaker_id))
        for sample in samples:
            slide_path = os.path.join(root_dir, beaker_id, sample)
            if os.path.isdir(os.path.join(slide_path, 'zarr')):
                segs = os.listdir(os.path.join(slide_path, 'zarr'))
                for seg in segs:
                    img_id = '-'.join((beaker_id, sample, seg.split('.')[0]))
                    imgs.append(img_id)
    return imgs


def split_id(id_str):
    code, number, sample, seg = id_str.split('-')
    beaker_id = '-'.join((code, str(number)))
    return beaker_id, sample, seg


# def threshold_by_max(tensor, threshold=32):
#     num_dims = tensor.dim()
#     pix_max = torch.amax(tensor, dim=tuple(range(1, num_dims)))
#     label = (pix_max >= threshold).int().float()
#     return pix_max, label

# def threshold_by_top(tensor, threshold=32):
#     flattened_tensor = tensor.view(tensor.shape[0], -1)
#     pix = torch.quantile(flattened_tensor, 0.9999,dim=1, interpolation='nearest')
#     label = (pix >= threshold).int().float()
#     return pix, label
    


    

