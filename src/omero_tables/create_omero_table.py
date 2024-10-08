import pandas as pd
    
def create_omero_table(df, roi_value):
    omero_df = pd.DataFrame({
        'object': range(1, len(df) + 1),
        'roi': roi_value
    })
    omero_df = pd.concat([omero_df, df.reset_index(drop=True)], axis=1)
    
    return omero_df