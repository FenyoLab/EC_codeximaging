import os
import sys

from sklearn.cluster import KMeans
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def lineage_marker_cluster_tables(sample_names_path, segmentation_data_dir, omero_table_path, omero_dict, table_name, channel_names, thresholding_channel_names, n_clusters):
    '''Create lineage marker cluster tables for omero
    This is the function called by the main script'''
    generate_omero_tables(process_lineage_marker_clusters, sample_names_path, omero_table_path, omero_dict, table_name, segmentation_data_dir=segmentation_data_dir,
                        channel_names=channel_names, thresholding_channel_names=thresholding_channel_names, n_clusters=n_clusters)

def process_lineage_marker_clusters(sample, segmentation_data_dir, channel_names, thresholding_channel_names, n_clusters):
    '''Process lineage marker cluster data for a single sample
    Calls KMeans clustering on each thresholding channel
    Returns a DataFrame with cluster labels for each channel'''

    matrix = np.load(os.path.join(segmentation_data_dir, 'matrix.npy'))
    cell_sample_names = np.load(os.path.join(segmentation_data_dir, 'cell_sample_names.npy'))
    sample_indices = np.where(cell_sample_names == sample)
    sample_matrix = matrix[sample_indices]

    kmeans_channel = []
    for channel in thresholding_channel_names:
        print(f'Channel: {channel}')
        channel_index = channel_names.index(channel)
        sample_channel_array = sample_matrix[:, channel_index]
        sample_channel_array = sample_channel_array.reshape(-1, 1)
        kmeans = KMeans(n_clusters=n_clusters, n_init = 'auto', random_state=0).fit(sample_channel_array)
        cluster_labels = kmeans.labels_
        kmeans_channel.append(cluster_labels)
        
    kmeans_channel_stacked = np.column_stack(kmeans_channel)
    marker_clusters_df = pd.DataFrame(kmeans_channel_stacked, columns = thresholding_channel_names)
    return marker_clusters_df


def celltype_cluster_tables(sample_names_path, cluster_path, omero_table_path, omero_dict, table_name, n_clusters):
   '''Create celltype cluster tables for omero
   This is the function called by the main script'''
   generate_omero_tables(process_celltype_clusters, sample_names_path, omero_table_path, omero_dict, table_name, cluster_path=cluster_path, n_clusters=n_clusters)

def process_celltype_clusters(sample, cluster_path, n_clusters):
    '''Process celltype cluster data for a single sample
    Extracts cell cluster labels from the metadata'''
    metadata = pd.read_csv(os.path.join(cluster_path, 'phenotype_clusters.csv'))
    sample_metadata = metadata[metadata["slide_id"] == sample]
    sample_cluster_labels = sample_metadata["cluster_label"]
    
    celltype_clusters_df = pd.DataFrame(sample_cluster_labels).rename(columns={"cluster_label": f'clusters_{n_clusters}'})
    return celltype_clusters_df


def celltype_tables(sample_names_path, cell_types_path, omero_table_path, omero_dict, table_name, n_clusters):
    '''Create celltype tables for omero
    This is the function called by the main script'''
    generate_omero_tables(process_celltypes, sample_names_path, omero_table_path, omero_dict, table_name, cell_types_path=cell_types_path, n_clusters=n_clusters)

def process_celltypes(sample, cell_types_path, n_clusters):
    '''Process celltype data for a single sample
    Extracts cell cluster and cell type labels from the metadata'''
    metadata = pd.read_csv(os.path.join(cell_types_path, 'cell_types.csv'))
    sample_metadata = metadata[metadata["slide_id"] == sample]
    sample_cluster_labels = sample_metadata["cluster_label"]
    sample_cell_types = sample_metadata["cell_type"]
    
    celltype_df = pd.DataFrame({
        f'clusters_{n_clusters}': sample_cluster_labels,
        'cell_type': sample_cell_types
    })
    return celltype_df


def biomarker_mean_tables(sample_names_path, segmentation_data_dir, omero_table_path, omero_dict, table_name, channel_names):
    '''Create biomarker mean tables for omero
    This is the function called by the main script
    NOT NEEDED WITH CSV INPUT FOR LABEL IMAGE'''
    generate_omero_tables(process_biomarker_means, sample_names_path, omero_table_path, omero_dict, table_name, segmentation_data_dir=segmentation_data_dir, channel_names=channel_names)

def process_biomarker_means(sample, segmentation_data_dir, channel_names):
    '''Process biomarker mean data for a single sample
    Extracts biomarker means from the matrix
    NOT NEEDED WITH CSV INPUT FOR LABEL IMAGE'''
    matrix = np.load(os.path.join(segmentation_data_dir, 'matrix.npy'))
    cell_sample_names = np.load(os.path.join(segmentation_data_dir, 'cell_sample_names.npy'))

    sample_indices = np.where(cell_sample_names == sample)
    sample_matrix = matrix[sample_indices]
        
    biomarker_means_df = pd.DataFrame(sample_matrix, columns = channel_names)
    return biomarker_means_df


def cell_feature_tables(sample_names_path, segmentation_data_dir, omero_table_path, omero_dict, table_name):
    '''Create cell feature tables for omero
    This is the function called by the main script'''
    generate_omero_tables(process_cell_features, sample_names_path, omero_table_path, omero_dict, table_name, segmentation_data_dir=segmentation_data_dir)

def process_cell_features(sample, segmentation_data_dir):
    '''Process cell feature data for a single sample
    Extracts cell features - area, perimeter, and axis_ratio from the metadata'''
    metadata = pd.read_csv(os.path.join(segmentation_data_dir, 'metadata.csv'))
    sample_metadata = metadata[metadata["slide_id"] == sample]
    sample_area = sample_metadata["area"]
    sample_perimeter = sample_metadata["perimeter"]
    sample_axis_ratio = sample_metadata["axis_ratio"]
    
    cell_features_df = pd.DataFrame({
        'area': sample_area,
        'perimeter': sample_perimeter,
        'axis_ratio': sample_axis_ratio
    })
    return cell_features_df


def neutrophil_percentage_table(sample_names_path, neutrophil_percentage_df_path, omero_tables_path, omero_dict, table_name):
    '''Create neutrophil percentage tables for omero
    This is the function called by the main script'''
    generate_omero_tables(process_neutrophil_percentage, omero_tables_path, omero_dict, table_name, neutrophil_percentage_df_path=neutrophil_percentage_df_path)

def process_neutrophil_percentage(sample, neutrophil_percentage_df_path):
    '''Process neutrophil percentage data for a single sample'''
    neutrophil_percentage_df = pd.read_csv(os.path.join(neutrophil_percentage_df_path, sample, 'neutrophil_percentage.csv'), index_col = 0)
    return neutrophil_percentage_df


def generate_omero_tables(process_func, sample_names_path, omero_table_path, omero_dict, table_name, samples_to_remove = None, **kwargs):
    '''General function called by table functions to loop through samples
    Calls the specific process_function to generate the table content
    Calls create_omero_table to format the table for omero
    Saves the table to the omero_table_path
    '''
    sample_names = np.load(sample_names_path)
    for sample in np.unique(sample_names):
        if samples_to_remove is not None and sample in samples_to_remove:
            print(f"Skipping sample: {sample}")
            continue

        os.makedirs(os.path.join(omero_table_path, sample), exist_ok = True)
        table_path = os.path.join(omero_table_path, sample, f'{table_name}.csv')
        if os.path.exists(table_path):
            print(f'{table_name}.csv already saved for sample {sample}')
            continue
        
        print(f"Processing sample: {sample}")    

        table_data = process_func(sample, **kwargs)
        if process_func == process_neutrophil_percentage:
            roi_value = omero_dict.get(sample, {}).get('tile_roi_id')
        else:
            roi_value = omero_dict.get(sample, {}).get('roi_id')

        omero_df = create_omero_table(table_data, roi_value)
        print(omero_df.head())
        omero_df.to_csv(table_path, index = False)
        print(f'{table_name}.csv saved for sample {sample}')

def create_omero_table(df, roi_value):
    '''Formats the table content for omero
    format: object, roi, table_content...'''
    omero_df = pd.DataFrame({
        'object': range(1, len(df) + 1),
        'roi': roi_value
    })
    omero_df = pd.concat([omero_df, df.reset_index(drop=True)], axis=1)
    
    return omero_df