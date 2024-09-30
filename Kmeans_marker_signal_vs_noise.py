import os
import numpy as np
from types import SimpleNamespace
from utils import helper
import matplotlib.pyplot as plt

#import config
config_yaml_cellseg= '/gpfs/data/proteomics/projects/mh6486/FenyoLab/Endometrial/EC_codeximaging/config/config_cellsegmentation_test.yaml'
run_config_cellseg = helper.load_yaml_file(config_yaml_cellseg)
config_cellseg = SimpleNamespace(**run_config_cellseg)

config_yaml_cellphen = '/gpfs/data/proteomics/projects/mh6486/FenyoLab/Endometrial/EC_codeximaging/config/config_cellphenotyping.yaml'
run_config_cellphen = helper.load_yaml_file(config_yaml_cellphen)
config_cellphen = SimpleNamespace(**run_config_cellphen)

import pandas as pd
import numpy as np 
from sklearn.cluster import KMeans
import pdb

metadata = pd.read_csv('/gpfs/data/proteomics/projects/Endometrial_mIF/EC_codeximaging_results/raw_segmentation_data/metadata.csv')
matrix = np.load('/gpfs/data/proteomics/projects/Endometrial_mIF/EC_codeximaging_results/raw_segmentation_data/matrix.npy', mmap_mode='r')

samples = os.listdir(config_cellseg.data_dir)
channels_all = config_cellseg.channel_names
channels_lineage = ['MPO', 'CD163', 'CD4', 'CD68', 'CD8', 'CD20', 'CD31', 'CD3e']
for sample in samples:
    print(sample)
    if sample == 'common_channels.txt':
        continue
    kmeans_perchannel = []
    for channel in channels_lineage:
        print(channel)
        marker_idx = channels_all.index(channel) #this is the index in the full matrix of markers so can use to extract channel info from matrix 
        # Extract marker data from the cell by marker matrix 
        matrix_channel = matrix[:, marker_idx] 
        # Filter by sample in the metadata
        metadata_sample = metadata['slide_id'] == sample #this tells me where in the metadata is my sample
        matrix_channel_sample_specific = matrix_channel[metadata_sample.values] #this is just getting the cell means of the sample of interest
        # Run KMeans on the sample data
        matrix_channel_sample_specific_2d = matrix_channel_sample_specific.reshape(-1, 1)  # Reshape to 2D
        kmeans = KMeans(n_clusters=2, random_state=0).fit(matrix_channel_sample_specific_2d)
        # Get the cluster labels and centers
        labels = kmeans.labels_
        centers = kmeans.cluster_centers_
        kmeans_perchannel.append(labels)
        # Create the scatter plot
        # plt.scatter(sample_data, np.zeros_like(sample_data), c=labels, cmap='viridis', marker='o')
        # plt.title(f'K-means Clustering Results for {sample} and {channel}')
        # plt.xlabel('Marker Value')
        # plt.yticks([])  # Hide y-axis ticks

        # # Save the figure as a PNG file
        # plt.savefig(f'/gpfs/data/proteomics/projects/mh6486/FenyoLab/Endometrial/CellPhenotypingAnalysis/out/3kmeans_{sample}_{channel}.png', bbox_inches='tight')  # Adjust the filename as needed
        # plt.close()  # Close the plot to free up memory

        #run kmeans on other channels to distinguish low, medium, high groups 

    # Stack the arrays as columns
    kmeans_perchannel_stacked = np.column_stack(kmeans_perchannel)
    df_kmeans = pd.DataFrame(kmeans_perchannel_stacked, columns = channels_lineage)
    os.makedirs("/gpfs/data/proteomics/projects/mh6486/FenyoLab/Endometrial/CellPhenotypingAnalysis/kmeans2_labels", exist_ok=True)
    df_kmeans.to_csv(f"/gpfs/data/proteomics/projects/mh6486/FenyoLab/Endometrial/CellPhenotypingAnalysis/kmeans2_labels/lineagemarkers_2clusters_{sample}.csv")

   


