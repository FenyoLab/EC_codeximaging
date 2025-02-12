import os
from tqdm import tqdm
import utils.helper as utils
import pdb
from types import SimpleNamespace

def run_preprocess(config_yaml):
    
    # Load the configuration
    run_config = utils.load_yaml_file(config_yaml)
    config = SimpleNamespace(**run_config)

    data_path = f'{config.output_path}/data'
    qc_path = f'{config.output_path}/qc'

    # Step 1: Convert tiff to zarr and QC
    zarr_conversion(config.common_channel_file, config.input_path, config.input_ext, config.output_path, data_path, qc_path)

    # Step 2: Generate tiles
    tiling(config.input_path, config.input_ext, data_path, config.tiles_dir, config.ref_channel, config.ROI_path, config.output_path, config.inference_window_um, config.input_pixel_per_um, config.selected_region, config.ROI_rm)

def tiling(input_path, input_ext, data_path, tiles_dir, ref_channel, ROI_path, output_path, inference_window_um, input_pixel_per_um, selected_region, ROI_rm):
    from preprocess.tile import gen_tiles
    file_names = utils.get_file_name_list(input_path, input_ext)
    print("ROI_path: ", ROI_path)
    print(file_names)
    training_window_um = inference_window_um * 2
    training_window_pixel = training_window_um * input_pixel_per_um
    inference_window_pixel = inference_window_um * input_pixel_per_um
    for file_name in tqdm(file_names):
        print(file_name)
        gen_tiles(data_path, file_name, tiles_dir, ref_channel, ROI_path, training_window_pixel, selected_region, ROI_rm)
        gen_tiles(data_path, file_name, tiles_dir, ref_channel, ROI_path, inference_window_pixel, selected_region, ROI_rm)

def zarr_conversion(common_channel_file, input_path, input_ext, output_path, data_path, qc_path):
    from preprocess import io 
    from preprocess import qc
    # Start preprocessing
    common_channels = utils.read_channel_file(common_channel_file)
    file_names = utils.get_file_name_list(input_path, input_ext)
    print("files names: ", file_names)
    print('Converting tiff to zarr')
    for file_name in tqdm(file_names):
        print(file_name)
        io.tiff_to_zarr(input_path, data_path, file_name, input_ext, common_channels)
    # Plot global QC histogram
    #print('Generating global QC histogram')
    #qc.global_hist(data_path, file_names, qc_path)


