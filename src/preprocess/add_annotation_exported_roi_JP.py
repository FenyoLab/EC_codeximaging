import pandas as pd
import os


def delete_apple_nonsense(data_dir):
    file_list = os.listdir(data_dir)
    real_files = []
    for filly in file_list:
        if not ("._"  in filly and ".DS" in filly):
            real_files.append(filly)
    return real_files


# sample_name = '02433_A1_1043528'
def main():
    data_dir = '/gpfs/data/proteomics/data/Cervical_mIF/registration_ROIs_downloaded'
    default_annot='tumor'
    for file_name in delete_apple_nonsense(data_dir):
        df_annot = pd.read_csv(data_dir + "/" + file_name)
        # if unannotated in "Text" field
        if any(pd.isna(df_annot["Text"])):
            df_annot["Text"]=df_annot["Text"].astype(str)
            for x in range(0,len(df_annot)):
                if df_annot.loc[x,"Text"] == 'nan':
                    print("NaN at row " + str(x) +", replacing with "+ default_annot)
                    df_annot.loc[x,"Text"]=default_annot
    
        new_file_name = file_name.split(" ")[0]+ "_" + file_name.split(" ")[1].split(".")[0] + "_rois.csv"
        df_annot.to_csv(data_dir+"/" + new_file_name)
        os.remove(data_dir + "/" + file_name)


# Run main() when this analysis.py is run 
if __name__ == "__main__":
    main()


    

        

