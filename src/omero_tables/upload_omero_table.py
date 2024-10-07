import os
import omero2pandas 

def upload_omero_table(table_dir, omero_dict, table_name, server="omero.nyumc.org", port=4064):
    
    #check that kerberos and password is in env
    password = os.getenv('PASSWORD')
    kerberosid = os.getenv('KERBEROSID')

    if password is None:
        raise ValueError('No password provided in environment variable PASSWORD')
    elif kerberosid is None:
        raise ValueError('No kerberos provided in environment variable KERBEROSID')
    
    for sample in os.listdir(table_dir):
        print(f'Processing sample {sample}')
        table_path = os.path.join(table_dir, sample, f'{table_name}.csv')
        image_id = omero_dict.get(sample, {}).get('image_id')
        roi_value = omero_dict.get(sample, {}).get('roi_id')

        ann_id = omero2pandas.upload_table(
            table_path, table_name, 
            links=[("Image", image_id), ("Roi", roi_value)], 
            server="omero.nyumc.org", port=4064, username=kerberosid, password=password)
        
        print(f'Omero table {table_name} uploaded for {sample}')