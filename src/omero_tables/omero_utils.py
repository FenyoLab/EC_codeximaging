import omero2pandas 
import pandas as pd

def upload_omero_table(table_path, sample, table_name, image_id, roi_value, kerberosid, password, server="omero.nyumc.org", port=4064):

    ann_id = omero2pandas.upload_table(
        table_path, table_name, 
        links=[("Image", image_id), ("Roi", roi_value)], server="omero.nyumc.org", port=4064, username=kerberosid, password=password)
    
def create_omero_table(df, roi_value):
    omero_df = pd.DataFrame({
        'object': range(1, len(df) + 1),
        'roi': roi_value
    })
    omero_df = pd.concat([omero_df, df.reset_index(drop=True)], axis=1)
    
    return omero_df