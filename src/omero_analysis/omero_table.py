import os
import sys
import pandas as pd

import omero
import omero2pandas
from omero.gateway import BlitzGateway
from omero.model import RoiAnnotationLinkI, RoiI, FileAnnotationI
from omero.sys import ParametersI
from getpass import getpass

from types import SimpleNamespace

sys.path.append('../..')
from utils import helper


'''this script must be run from datamover node with omero conda environment activated'''
'''first mount the research drive directly in terminal and then run the script (from sbatch)'''

def main():
    #load in config 
    config_yaml= '/gpfs/home/as18894/projects/as18894/FenyoLab/Endometrial/EC_codeximaging/config/config_cellsegmentation.yaml'
    run_config = helper.load_yaml_file(config_yaml)
    config = SimpleNamespace(**run_config)

    metadata_per_sample_path = os.path.join(config.out_dir, config.sample_metadata_dir)
    out_suffix = os.path.basename(config.out_dir)

    omero_table(metadata_dir = metadata_per_sample_path, base_dir = config.research_drive_dir, 
                    omero_info_dict = config.omero_image_info_dict, kerberosid = config.kerberosid) #, out_suffix = out_suffix)


def omero_table(metadata_dir, base_dir, omero_info_dict, kerberosid = None): #, out_suffix = None):
    
    #navigate to correct dir on research drive 
    research_drive_dir = f'/mnt/{kerberosid}/{base_dir}/label_images'
    os.chdir(research_drive_dir)
    #os.makedirs(out_suffix, exist_ok =True)
    #os.chdir(out_suffix)
    print(f"Current directory: {os.getcwd()}")
    
    #to save tables with date of run 
    date = "_".join(out_suffix.split("_")[1:])

    password = os.getenv('YOUR_PASSWORD')
    if password is None:
        raise ValueError('No password provided in environment variable YOUR_PASSWORD')
    print(password)

    sample_names = os.listdir(research_drive_dir) 
    for sample in sample_names:
        
        #for testing purposes
        if sample != '20231003-2630-3P_Scan1':
            continue
        
        print(f'Processing sample {sample}')

        os.makedirs(sample, exist_ok =True)
        os.chdir(sample)
        print(f"Current directory: {os.getcwd()}")

        table_path = os.path.join(research_drive_dir, sample, f'metatable_{date}.csv')
        print(table_path)
        if os.path.exists(table_path):
            print('Metatable already generated')

        else:
            roi_value = omero_info_dict.get(sample, {}).get('roi_id')
            create_omero_table(metadata_dir, table_path, sample, roi_value)
            print("omero table created")
        
        #breakpoint()
        image_id = omero_info_dict.get(sample, {}).get('image_id')
        table_name = f'table_{date}'
        ann_id = upload_omero_table(table_path, sample, table_name, image_id, kerberosid, password)
        print("omero table uploaded")
        print(ann_id)


        conn = connect(hostname='omero.nyumc.org', username= kerberosid, password = password)
        link_table_to_roi(conn, ann_id, roi_value)
        disconnect(conn)
    
        os.chdir('..')
    


def create_omero_table(metadata_dir, table_path, sample, roi_value):

    metadata = pd.read_csv(f'{metadata_dir}/{n_clusters}_clusters/{sample}/sample_metadata.csv', index_col = 0)
    print("Metadata shape:", metadata.shape)
    print(sample, roi_value)

    omero_df = pd.DataFrame({
        'object': metadata['label_image_cell_index'],
        'roi': roi_value,
        'kmeans_label': metadata['cluster_label'],
        #'cell_types': metadata['cell_types']
    })
    print("Omero_df shape:", omero_df.shape)
    #breakpoint()
    omero_df.to_csv(table_path, index = True)


def upload_omero_table(table_path, sample, table_name, image_id, kerberosid, password, server="omero.nyumc.org", port=4064):
    
    metatable = pd.read_csv(table_path, index_col = 0)
    print("Omero_df shape:", metatable.shape)
    
    ann_id = omero2pandas.upload_table(metatable, table_name, image_id, "Image",
			server="omero.nyumc.org", port=4064, username=kerberosid, password=password)

    return ann_id

def connect(hostname, username, password):
    """
    Connect to an OMERO server
    :param hostname: Host name
    :param username: User
    :param password: Password
    :return: Connected BlitzGateway
    """
    conn = BlitzGateway(username, password,
                        host=hostname, secure=True)
    conn.connect()
    conn.c.enableKeepAlive(60)
    return conn


def disconnect(conn):
    """
    Disconnect from an OMERO server
    :param conn: The BlitzGateway
    """
    conn.close()

def link_table_to_roi(gateway, table_id, roi_id):
    """
    Link an OMERO.table to a ROI object

    :param gateway: An instance of a BlitzGateway object
    :param table_id: The ID of the OMERO.table
    :param roi_ID: The ID of the ROI to link the table to
    """

    query = (
        "select ann from FileAnnotation ann "
        "join fetch ann.file as f "
        "where f.id=:id"
    )
    params = ParametersI()
    #breakpoint()
    params.addId(table_id)
    gateway.SERVICE_OPTS.setOmeroGroup("-1")
    file_ann = gateway.getQueryService().projection(query, params, gateway.SERVICE_OPTS)[0][0].val ##### ERROR LINE
    
    #THE ERROR IS HERE!!!
    #*** IndexError: list index out of range
    #its because fil_ann is empty, this query is not getting anything 

    link = RoiAnnotationLinkI()
    link.parent = RoiI(roi_id, False)
    link.child = FileAnnotationI(file_ann.id.val, False)
    ctx = {'omero.group': str(file_ann.getDetails().getGroup().getId().val)}
    gateway.getUpdateService().saveObject(link, ctx)
    #LOGGER.info(f"Linked table {table_id} to ROI {roi_id}.")

if __name__ == "__main__":
    main()
