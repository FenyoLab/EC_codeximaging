import os
import sys
import pandas as pd
import geojson

import omero
from omero.gateway import BlitzGateway
from omero.model import RoiAnnotationLinkI, RoiI, FileAnnotationI
from omero.sys import ParametersI
from omero.rtypes import rdouble, rint, rstring

from types import SimpleNamespace
sys.path.append('../..')
from utils import helper

def main():
    #import config
    config_yaml= '../../config/config_cellsegmentation.yaml'
    run_config = helper.load_yaml_file(config_yaml)
    config = SimpleNamespace(**run_config)

    annotations_dir = '/gpfs/data/proteomics/projects/Endometrial_mIF/EC_codeximaging_results/preprocessing/registration/annotations'
    omero_dict = config.omero_image_dict

    for sample in os.listdir(annotations_dir):
        print(f'Processing sample {sample}')
        sample_dir = os.path.join(annotations_dir, sample)
        os.chdir(sample_dir)
        print(f"Current directory: {os.getcwd()}")
        
        upload_rois_to_omero(sample, omero_dict)
        print('rois uploaded to omero')


def upload_rois_to_omero(sample, omero_dict):   
    
    password = os.getenv('PASSWORD')
    kerberosid = os.getenv('KERBEROSID')

    if password is None:
        raise ValueError('No password provided in environment variable PASSWORD')
    elif kerberosid is None:
        raise ValueError('No kerberos provided in environment variable KERBEROSID')

    #omero login
    conn = BlitzGateway(kerberosid, password, host="omero.nyumc.org", port=4064)
    conn.connect()
    updateService = conn.getUpdateService()

    image_id = omero_dict.get(sample, {}).get('image_id')
    image = conn.getObject("Image", image_id)
    print(image, image_id)

    geojson_file = f'{sample}_rois.geojson'
    print(geojson_file)
    with open(geojson_file) as f:
        data = geojson.load(f)
        
    for feature in data['features']:
        # Extract the coordinates for each feature
        coordinates = feature['geometry']['coordinates'][0]  # Assuming the first set of coordinates is used
    
        # Flatten and format points to the correct format
        points = " ".join([f"{x},{y}" for x, y in coordinates])
    
        # Create an ROI with a single polygon
        polygon = omero.model.PolygonI()
        polygon.points = rstring(points)
        polygon.textValue = rstring(feature['properties']['Name'])  # Use the feature name for the ROI text value

        # Create the ROI in OMERO
        create_roi(image, [polygon], updateService)
    
    conn.close()


def create_roi(img, shapes, updateService):
    # create an ROI, link it to Image
    roi = omero.model.RoiI()
    # use the omero.model.ImageI that underlies the 'image' wrapper
    roi.setImage(img._obj)
    for shape in shapes:
        roi.addShape(shape)
    # Save the ROI (saves any linked shapes too)
    return updateService.saveAndReturnObject(roi)

if __name__ == '__main__':
    main()