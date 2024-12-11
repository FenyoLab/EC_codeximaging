import numpy as np
from rdfpy import rdf
import pandas as pd
import pdb
import matplotlib.pyplot as plt

def cell_type_analysis(matrix_path, metadata_path, channels, clinical_dat, cell_types, out_file):
    #load files 
    clinicaldata = pd.read_csv(clinical_dat)
    metadata = pd.read_csv(metadata_path)
    matrix = np.load(matrix_path, mmap_mode='r')

    metadata_celltypes = pd.read_csv(cell_types)
    slides = clinicaldata['Key']
    Pair_Correlation(matrix, metadata, metadata_celltypes, clinicaldata, channels, slides)

def Pair_Correlation(matrix, metadata, metadata_celltypes, clinicaldata, channels, slides): #must use the raw unfiltered RAW metadata here!!!
    plt.figure(figsize=(10, 8)) 
    for slide in slides:
        print(slide)
        #get the indices of the T cells per slide
        Tcells_indices = metadata_celltypes.index[(metadata_celltypes['slide_id'] == slide) & (metadata_celltypes['cell_type'].isin(["cytotoxic_Tcell", "helper_Tcell"]))].to_list()
        #get the indices of the Tumor cells per slide 
        Tumorcells_indices = metadata_celltypes.index[(metadata_celltypes['slide_id'] == slide) & (metadata_celltypes['cell_type'].isin(["tumor", "tumor_cell"]))].to_list()

        metadata['centroid_x_slide'] = metadata.centroid_x + metadata.tile_w
        metadata['centroid_y_slide'] = metadata.centroid_y + metadata.tile_h

        Tcells_x = metadata['centroid_x_slide'].loc[Tcells_indices]
        Tcells_y = metadata['centroid_y_slide'].loc[Tcells_indices]

        Tumorcells_x = metadata['centroid_x_slide'].loc[Tumorcells_indices]
        Tumorcells_y = metadata['centroid_y_slide'].loc[Tumorcells_indices]

        #convert the centroids to be within slide locations rather than just within tile
        #pdb.set_trace()

        # Combine T cell and Tumor cell centroids into a 2D array
        Tcells_centroids = np.column_stack((Tcells_x, Tcells_y))
        Tumorcells_centroids = np.column_stack((Tumorcells_x, Tumorcells_y))
        #pdb.set_trace()
        # compute radial distribution function with step size = 0.1
        g_r_Tcells, radii_Tcells = rdf(Tcells_centroids, dr=2000)
        g_r_Tumorcells, radii_Tumorcells = rdf(Tumorcells_centroids, dr=3000)
        
        # metadata_indices = metadata.index[metadata['slide_id'] == slide].tolist()
        # matrix_slide_chan = matrix[metadata_indices,chan]

        recurrence_status = clinicaldata.loc[clinicaldata.Key == slide, 'Recurred'].values

        if len(recurrence_status) > 0:  # Check if recurrence status exists for the slide
            if recurrence_status[0] == 1:
                color = 'blue'
                label = f'{slide} Recurrent'
                print('label', label)
            elif recurrence_status[0] == 0:
                color = 'orange'
                label = f'{slide} NonRecurrent'
                print('label', label)

        
        # Plot the RDF for T cells
        # plt.plot(radii_Tcells, g_r_Tcells, marker='o', color=color, label=label)
        # plt.xlabel('Distance (r)')
        # plt.ylabel('g(r)')
        # plt.title(f'Radial Distribution Function Tcells')
        # plt.legend()

        # plt.plot(radii_Tumorcells, g_r_Tumorcells, marker='o')
        # plt.xlabel('Distance (r)')
        # plt.ylabel('g(r)')
        # plt.title(f'Radial Distribution Function Tumorcells')
        # plt.legend()
        # Plot the RDF for T cells
        plt.plot(radii_Tcells, g_r_Tcells, marker='o', linestyle='-', color=color, label=f'T cells {label}')
        
        # Plot the RDF for Tumor cells
        plt.plot(radii_Tumorcells, g_r_Tumorcells, marker='x', linestyle='--', color=color, label=f'Tumor cells {label}')
    
    # Add labels, title, and legend once after the loop
    plt.xlabel('Distance (r)')
    plt.ylabel('g(r)')
    plt.title('Radial Distribution Function for T cells and Tumor cells')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')  # Adjust the legend location to prevent overlap
    plt.tight_layout()

    plt.savefig(f'rdf_allslides_Tcells_Tumorcells.png')
    plt.close()
        

    # g_r_Tumorcells, radii_Tumorcells = rdf(Tumorcells_centroids, dr=1000)

        # plt.plot(radii_Tumorcells, g_r_Tumorcells, marker='o')
        # plt.xlabel('Distance (r)')
        # plt.ylabel('g(r)')
        # plt.title(f'Radial Distribution Function Tumor cells {slide}')
    # plt.savefig(f'rdf_{slide}_Tumorcells.png')
    # plt.close()