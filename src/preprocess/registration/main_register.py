import os
import geojson
import pandas as pd
import json
#from valis import registration
import geojson
import pdb

#pdb.set_trace()
import csv_to_geojson, geojson_to_csv #, registration

image_dir = '/gpfs/data/proteomics/projects/Endometrial_mIF/EC_codeximaging_results/registration/images'
annotations_dir = '/gpfs/data/proteomics/projects/Endometrial_mIF/EC_codeximaging_results/registration/annotations'

#sample = sample_qptiff name 
#pdb.set_trace()
for sample in os.listdir(image_dir):
    if sample == '20231003-2630-3P_Scan1' or sample == "20230720-4309-4G-1_Scan1":
        continue
    print (sample)
    sample_path = os.path.join(image_dir, sample)
    for file in os.listdir(sample_path):
        
        # Get the file name without the extension
        file_name, ext = os.path.splitext(file)
            
        if ext == '.qptiff':
            sample_qptiff_name = file_name  # Without .qptiff
        elif ext == '.svs':
            sample_svs_name = file_name  # Without .svs
    
    #pdb.set_trace()
    # Convert the CSV file to GeoJSON
    csv_file = os.path.join(annotations_dir, sample, f'{sample_svs_name}_rois.csv')
    geojson_file = os.path.join(annotations_dir, sample, f'{sample_svs_name}_rois.geojson')
    csv_to_geojson.csv_to_geojson(csv_file, geojson_file)

    # # Perform registration and transfer annotations
    # registration.convert_rois_with_registration(sample, sample_svs_name, sample_qptiff_name)

    # # Convert the GeoJSON file back to CSV
    # geojson_file = os.path.join(annotations_dir, sample, f'{sample_qptiff_name}_rois.geojson')
    # csv_file = os.path.join(annotations_dir, sample, f'{sample_qptiff_name}_rois.csv')
    # geojson_to_csv.geojson_to_csv(geojson_file, csv_file)

