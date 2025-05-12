import os
import omero2pandas 
import pdb  

def upload_omero_table(table_dir, omero_dict, table_name, server="omero.nyumc.org", port=4064):
    
    #check that kerberos and password is in env
    password = os.getenv('PASSWORD')
    kerberosid = os.getenv('USER')

    if password is None:
        raise ValueError('No password provided in environment variable PASSWORD')
    elif kerberosid is None:
        raise ValueError('No kerberos provided in environment variable USER')
    
    for sample in omero_dict.keys():
        #check if the table exists within the sample directory 
        if f'{table_name}.csv' not in os.listdir(os.path.join(table_dir, sample)):
            print(f'{table_name} not found in {sample}')
            continue

        print(f'Processing sample {sample}')
        table_path = os.path.join(table_dir, sample, f'{table_name}.csv')
        image_id = omero_dict.get(sample, {}).get('image_id')
        roi_value = omero_dict.get(sample, {}).get('cell_label_image_csv')
        ann_id = omero2pandas.upload_table(
            table_path, table_name, 
            links=[("Image", image_id), ("Roi", roi_value)], 
            server="omero.nyumc.org", port=4064, username=kerberosid, password=password)
        
        print(f'Omero table {table_name} uploaded for {sample}')