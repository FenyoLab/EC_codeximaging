import os
import geojson
import pandas as pd
import json
from valis import registration
import pdb
#import geojson

import csv_to_geojson, geojson_to_csv
import registration

image_dir = '../data/images'
annotations_dir = '../data/annotations'

#sample = sample_qptiff name 

for sample in os.listdir(image_dir):
    if sample != '20231019-4475-1E_Scan2': # HAVE TO RUN THIS ONE SAMPLE AT A TIME
        continue

    print(f'Processing sample {sample}')
    sample_path = os.path.join(image_dir, sample)
    for file in os.listdir(sample_path):
        # Get the file name without the extension
        file_name, ext = os.path.splitext(file)
        
        if ext == '.qptiff':
            sample_qptiff_name = file_name  # Without .qptiff
            print("sample qptiff name:", sample_qptiff_name)
        elif ext == '.svs':
            sample_svs_name = file_name  # Without .svs
            print("sample svs name:", sample_svs_name)

    transformed_geojson_file = os.path.join(annotations_dir, sample, f'{sample_qptiff_name}_rois.geojson')
    if os.path.exists(transformed_geojson_file):
        print(f"Transformed rois geojson already exists, skipping sample {sample}")
        continue

    # Convert the CSV file to GeoJSON
    original_csv_file = os.path.join(annotations_dir, sample, f'{sample_svs_name}_rois.csv')
    original_geojson_file = os.path.join(annotations_dir, sample, f'{sample_svs_name}_rois.geojson')
    csv_to_geojson.csv_to_geojson(original_csv_file, original_geojson_file)

    # Perform registration and transfer annotations
    registration.convert_rois_with_registration(sample, sample_svs_name, sample_qptiff_name)

    # Convert the GeoJSON file back to CSV
    #transformed_csv_file = os.path.join(annotations_dir, sample, f'{sample_qptiff_name}_rois.csv')
    #geojson_to_csv.geojson_to_csv(transformed_geojson_file, transformed_csv_file)

