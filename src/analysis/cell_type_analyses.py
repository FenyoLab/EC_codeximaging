import pandas as pd 
import pdb
from statistics import mean
import scipy.stats as stats
import numpy as np
from types import SimpleNamespace
from utils import helper
import matplotlib.pyplot as plt
from scipy.stats import pearsonr, spearmanr
import os
import seaborn as sns
from sklearn.neighbors import NearestNeighbors
from scipy.spatial.distance import cdist 

def cell_type_analysis(matrix_path, metadata_path, channels, clinical_dat, cell_types, out_file):
    #load files 
    clinicaldata = pd.read_csv(clinical_dat)
    metadata = pd.read_csv(metadata_path)
    matrix = np.load(matrix_path, mmap_mode='r')

    metadata_celltypes = pd.read_csv(cell_types)
    slides = clinicaldata['Key']

    Pair_Correlation(matrix, metadata, metadata_celltypes, clinicaldata, channels, slides)
    #pdb.set_trace()
    #recur_vs_nonrecur_allbiomarkers(matrix, metadata, clinicaldata, channels, slides)

    pdb.set_trace()
   
    #create an df with a few key clinical variables
    summary_df = clinicaldata.loc[:, ['Key', 'Stage (1*:I-II, 2*:I-II, 3*:III-IV, 4*:III-IV)', 'Grade', 'Recurred', 'IO response', 'Smoking Hx']]
    summary_df.rename(columns={'Stage (1*:I-II, 2*:I-II, 3*:III-IV, 4*:III-IV)': 'Stage'}, inplace=True)
    summary_df = summary_df.set_index('Key')
    cell_types = metadata_celltypes['cell_type'].unique()
    print(cell_types)
    if not os.path.exists(out_file):
        for slide in slides: 
            print(slide)
            metadata_slide = metadata_celltypes[metadata_celltypes['slide_id']==slide]
            #count_immune_cells(slide, metadata, metadata_slide,clinicaldata, summary_df)
        summary_df.to_csv(out_file)
    else:
        summary_df = pd.read_csv(out_file)

    print(summary_df)
    #calc_stats(summary_df)

def Pair_Correlation(matrix, metadata, metadata_celltypes, clinicaldata, channels, slides): #must use the raw unfiltered RAW metadata here!!!
    distances_all = []
    for slide in slides:
        print(slide)
        #get the indices of the T cells per slide
        Tcells_indices = metadata_celltypes.index[(metadata_celltypes['slide_id'] == slide) & (metadata_celltypes['cell_type'].isin(["cytotoxic_Tcell", "helper_Tcell"]))].to_list()
        #get the indices of the Tumor cells per slide 
        Tumorcells_indices = metadata_celltypes.index[(metadata_celltypes['slide_id'] == slide) & (metadata_celltypes['cell_type'].isin(["tumor", "tumor_cell"]))].to_list()

        Tcells_x = metadata['centroid_x'].loc[Tcells_indices]
        Tcells_y = metadata['centroid_y'].loc[Tcells_indices]

        Tumorcells_x = metadata['centroid_x'].loc[Tumorcells_indices]
        Tumorcells_y = metadata['centroid_y'].loc[Tumorcells_indices]

        #convert the centroids to be within slide locations rather than just within tile
        pdb.set_trace()

        # Combine T cell and Tumor cell centroids into a 2D array
        Tcells_centroids = np.column_stack((Tcells_x, Tcells_y))
        Tumorcells_centroids = np.column_stack((Tumorcells_x, Tumorcells_y))



        # # Define the region to filter (X between 100 and 200, Y between 20 and 30)
        # x_min, x_max = 100, 200
        # y_min, y_max = 200, 300
        # #filter centroids to only include a smaller region
        # Tcells_centroids_filtered = filter_coordinates(Tcells_centroids, x_min, x_max, y_min, y_max)
        # Tumorcells_centroids_filtered = filter_coordinates(Tumorcells_centroids, x_min, x_max, y_min, y_max)

        # r, rdf = calculate_rdf_between_types(Tcells_centroids_filtered, Tumorcells_centroids_filtered)
        # r_T, rdf_T = calc_rdf(Tcells_centroids, max_distance = 50, num_bins = 20)
        # r_Tumor, rdf_Tumor = calc_rdf(Tumorcells_centroids, max_distance = 50, num_bins = 20)

    
        #plot the results
        # Plotting the results
        # plt.figure(figsize=(10, 5))
        # plt.plot(r_T, rdf_T, label='T Cells', marker='o')
        # plt.plot(r_Tumor, rdf_Tumor, label='Tumor Cells', marker='o')
        # plt.plot(r,rdf, label='T Cells vs Tumor Cells', marker='o')
        # plt.xlabel('Distance (µm)')
        # plt.ylabel('Radial Distribution Function')
        # plt.title('Radial Distribution Function of T Cells and Tumor Cells')
        # plt.legend()
        # plt.grid()
        # plt.savefig(f"RDF_Tcells_vs_Tumorcells_{slide}")

        #pdb.set_trace()

        #distances = calculate_nearest_distances(Tcells_centroids, Tumorcells_centroids)
        #distances_all.append(distances)
    pdb.set_trace()
    #calculate the mean distance per sample 
    mean_distances = [mean(sample) for sample in distances_all]

    samples_rec_idx = clinicaldata.index[clinicaldata.Recurred == 1]
    samples_nonrec_idx = clinicaldata.index[clinicaldata.Recurred == 0]

    mean_distances_recur = [mean_distances[i] for i in samples_rec_idx]
    mean_distances_nonrecur = [mean_distances[i] for i in samples_nonrec_idx]
    t_stat, p_value = stats.ttest_ind(mean_distances_recur, mean_distances_nonrecur)
    pdb.set_trace()

    distances_recur = [distances_all[i] for i in samples_rec_idx]
    distances_nonrecur = [distances_all[i] for i in samples_nonrec_idx]
    pdb.set_trace()
    t_stat, p_value = stats.ttest_ind(np.concatenate(distances_recur), np.concatenate(distances_nonrecur))


    #Make boxplots for each patient's distances!!
    # Boxplot of distances across patients
    plt.figure(figsize=(10, 6))
    plt.boxplot(distances_all, labels=slides)
    plt.title("Distribution of Tumor to T cell Distances Across Patients")
    plt.ylabel("Distance")
    plt.xlabel("Patients")
    plt.xticks(rotation=45,ha='right')
    plt.tight_layout()
    plt.savefig(f"Tcell_Tumor_distances_boxplot.png")
    plt.close()

    # Boxplot of distances across patients
    plt.figure(figsize=(10, 6))
    plt.boxplot(distances_recur, labels=slides[samples_rec_idx])
    plt.title("Distribution of Tumor to T cell Distances Across Recurrent Patients")
    plt.ylabel("Distance")
    plt.xlabel("Patients")
    plt.xticks(rotation=45,ha='right')
    plt.tight_layout()
    plt.savefig(f"Tcell_Tumor_distances_boxplot_recur.png")
    plt.close()

    # Boxplot of distances across patients
    plt.figure(figsize=(10, 6))
    plt.boxplot(distances_nonrecur, labels=slides[samples_nonrec_idx])
    plt.title("Distribution of Tumor to T cell Distances Across NonRecurrent Patients")
    plt.ylabel("Distance")
    plt.xlabel("Patients")
    plt.xticks(rotation=45,ha='right')
    plt.tight_layout()
    plt.savefig(f"Tcell_Tumor_distances_boxplot_nonrecur.png")
    plt.close()

    pdb.set_trace()

# Function to filter coordinates based on region
def filter_coordinates(coords, x_min, x_max, y_min, y_max):
    return coords[
        (coords[:, 0] >= x_min) & (coords[:, 0] <= x_max) &  # X range
        (coords[:, 1] >= y_min) & (coords[:, 1] <= y_max)    # Y range
    ]

def calculate_rdf_between_types(t_cells, tumor_cells, max_distance=50, num_bins=20):
    # Calculate pairwise distances between T cells and tumor cells
    distances = cdist(t_cells, tumor_cells)
    
    # Flatten the distance matrix into a single array
    distances = distances.flatten()
    
    # Create bins for the distances
    bins = np.linspace(0, max_distance, num_bins + 1)
    hist, _ = np.histogram(distances, bins=bins)
    
    # Calculate the radial distribution function
    r = 0.5 * (bins[1:] + bins[:-1])  # Midpoints of bins
    volume_elements = 4/3 * np.pi * ((bins[1:]**3) - (bins[:-1]**3))  # Volume of spherical shells
    rdf = hist / volume_elements  # Density function
    
    # Normalize RDF
    rdf /= np.sum(rdf)

    return r, rdf


def calc_rdf(coordinates, max_distance=50, num_bins=20):
    # Define the region bounds
    x_min, x_max = 100, 120 
    y_min, y_max = 20, 30

    # Apply filtering
    filtered_coords = coordinates[
        (coordinates[:, 0] >= x_min) & (coordinates[:, 0] <= x_max) &  # X in range
        (coordinates[:, 1] >= y_min) & (coordinates[:, 1] <= y_max)    # Y in range
    ]

    
    #test on a small section of pixels!! 
    # Calculate pairwise distances
    distances = np.linalg.norm(filtered_coords[:, np.newaxis] - filtered_coords, axis=2)

    # Exclude self-distances (distance of 0)
    distances = distances[distances > 0]
    
    # Create bins for the distances
    bins = np.linspace(0, max_distance, num_bins + 1)
    hist, _ = np.histogram(distances, bins=bins)

    # Calculate the radial distribution function
    r = 0.5 * (bins[1:] + bins[:-1])  # Midpoints of bins
    volume_elements = 4/3 * np.pi * ((bins[1:]**3) - (bins[:-1]**3))  # Volume of spherical shells
    rdf = hist / volume_elements  # Density function

    # Normalize RDF
    rdf /= np.sum(rdf)

    return r, rdf

def calculate_nearest_distances(tumor_centroids, tcell_centroids):
    # Fit NearestNeighbors on the T cell centroids
    neigh = NearestNeighbors(n_neighbors=1)  # Find the nearest T cell for each Tumor cell
    neigh.fit(tcell_centroids)

    # Find the nearest T cell for each Tumor cell... there are x number of tumor cells... we are finding the closest distance each T cell is to each tumor cell 
    distances, _ = neigh.kneighbors(tumor_centroids) #The kneighbors method will return the Euclidean distance between each Tumor cell and its nearest T cell.

    return distances.flatten()  # Return the distances as a 1D array


def recur_vs_nonrecur_allbiomarkers(matrix, metadata, clinicaldata, channels, slides):
    recurrent_slides = clinicaldata['Key'].loc[clinicaldata.Recurred == 1]
    nonrecurrent_slides = clinicaldata['Key'].loc[clinicaldata.Recurred == 0]
   
    recurrent_slides_idx = slides[slides.isin(recurrent_slides)].index.tolist()
    nonrecurrent_slides_idx = slides[slides.isin(nonrecurrent_slides)].index.tolist()

    for chan in range(1,len(channels)): 
        #print(chan)
        chan_mean_all = []
        #if channels[chan] == "CD47" or channels[chan] == "GAL3" or channels[chan] == "TIM3":
        for slide in slides:
            #print(slide)

        #get the indeces of the recurrent and nonrecurrent cells 
        # metadata_rec_indices = metadata.index[metadata['slide_id'].isin(recurrent_slides)].tolist()
        # metadata_nonrec_indices = metadata.index[metadata['slide_id'].isin(nonrecurrent_slides)].tolist()
            metadata_indices = metadata.index[metadata['slide_id'] == slide].tolist()
       
        # matrix_rec = matrix[metadata_rec_indices,:]
        # matrix_nonrec = matrix[metadata_nonrec_indices,:]
            matrix_slide_chan = matrix[metadata_indices,chan]

        #Calculate the correlation of the biomarkers in the recurrent samples vs nonrecurrent samples... see if the same markers correlate
        #correlation_matrix_rec = np.corrcoef(matrix_rec, rowvar=False)  # Set rowvar=False to correlate columns
        #correlation_matrix_nonrec = np.corrcoef(matrix_nonrec, rowvar=False)  # Set rowvar=False to correlate columns

        # Visualize the correlation matrix
        # plt.figure(figsize=(22, 20))
        # sns.heatmap(correlation_matrix_rec, annot=True, fmt=".2f", cmap='coolwarm', square=True,
        #             xticklabels=[f'{channels[idx]}' for idx in range(correlation_matrix_rec.shape[1])],
        #             yticklabels=[f'{channels[idx]}' for idx in range(correlation_matrix_rec.shape[1])])
        # plt.title('Correlation Matrix of Biomarker Intensities in Recurrent Patients')
        # # Adjust layout to minimize whitespace
        # plt.tight_layout()  # Automatically adjust the padding
        # plt.savefig(f"Correlation_norm_filt_rec.png")
        # plt.close()

        # plt.figure(figsize=(22, 20))
        # sns.heatmap(correlation_matrix_nonrec, annot=True, fmt=".2f", cmap='coolwarm', square=True,
        #             xticklabels=[f'{channels[idx]}' for idx in range(correlation_matrix_nonrec.shape[1])],
        #             yticklabels=[f'{channels[idx]}' for idx in range(correlation_matrix_nonrec.shape[1])])
        # plt.title('Correlation Matrix of Biomarker Intensities in NonRecurrent Patients')
        # # Adjust layout to minimize whitespace
        # plt.tight_layout()  # Automatically adjust the padding
        # plt.savefig(f"Correlation_norm_filtnonrec.png")
        # plt.close()


            #extract the intensities for the biomarker of interest 
            # matrix_rec = matrix[metadata_rec_indices,chan]
            # matrix_nonrec = matrix[metadata_nonrec_indices,chan]

            # M ake a KDE plot of this data
            # Create KDE plot
                #sns.kdeplot(np.log(matrix_slide_chan + 1e-10), bw_adjust=0.5, label=f'{slide}')  # bw_adjust controls the smoothness of the curve
                # Check if the slide is recurrent or non-recurrent
         
            if clinicaldata['Recurred'][clinicaldata.Key == slide].any() == 1:
                sns.kdeplot(np.log1p(matrix_slide_chan + 1e-10), bw_adjust=0.5, color='blue', fill=True, label=f'{slide} Recurrent:')
            elif clinicaldata['Recurred'][clinicaldata.Key == slide].any() == 0:
                sns.kdeplot(np.log1p(matrix_slide_chan + 1e-10), bw_adjust=0.5, color='orange', fill=True, label=f'{slide} NonRecurrent')

                
            #sns.kdeplot(np.log(matrix_slide_chan + 1e-10), bw_adjust=0.5, label=clinicaldata['Recurred'][clinicaldata.Key == slide]) 
            plt.title('KDE Plot of Your Data')
            plt.xlabel('Log Intensity Value')
            plt.ylabel('Density')
            plt.legend(title="Recurrence", bbox_to_anchor=(1.05, 1), loc='upper left')  # Add legend
            plt.tight_layout()
            plt.savefig(f"KDE_{channels[chan]}_allslides")
                
            mean_channel_perslide = np.mean(matrix_slide_chan)
            chan_mean_all.append(mean_channel_perslide)

            # plt.figure(figsize=(8, 6))

            # plt.boxplot([matrix_rec, matrix_nonrec], labels=['Recurrent', 'Non-Recurrent'])

            # # Overlay dots (using scatter) - takes too long 
            # # plt.scatter(np.ones(len(matrix_rec)), matrix_rec, color='blue', alpha=0.6, label='recurrence')
            # # plt.scatter(2 * np.ones(len(matrix_nonrec)), matrix_nonrec, color='orange', alpha=0.6, label='nonrecurrence')
            # plt.title(f'Boxplot for {channels[chan]}')
            # plt.ylabel('Intensity')
            # plt.savefig(f"{channels[chan]}_boxplot_raw.png")
            # plt.close()

            #calculate a pvalue to see if there are any notable differences between the 2 groups 
            # t_stat, p_value = stats.ttest_ind(list(matrix_rec), list(matrix_nonrec))
            # print(f"ttest pval: {channels[chan]}: ", p_value)

            # Perform the Kolmogorov-Smirnov test to compare distributions
            # ks_statistic, ks_p_value = stats.ks_2samp(matrix_rec, matrix_nonrec)
            # print(f"ks pval: {channels[chan]}: ", ks_p_value)

            #use mannwhitney when your 2 groups of data is not normally distributed to compare differences in the 2 groups 
            # stat, p_value = stats.mannwhitneyu(matrix_rec, matrix_nonrec)
            # print(f"Mann-Whitney pval: {channels[chan]}: ", p_value)

            #Logistic Regression
        plt.close()  # Close the figure to avoid overlaying plots
            
        chan_mean_rec = [chan_mean_all[idx] for idx in recurrent_slides_idx]
        chan_mean_nonrec = [chan_mean_all[idx] for idx in nonrecurrent_slides_idx]
        t_stat, p_value = stats.ttest_ind(chan_mean_rec, chan_mean_nonrec)
        print("recurrent means: ", chan_mean_rec)
        print("nonrecurrent means: ", chan_mean_nonrec)
        print(channels[chan],p_value)
        
def count_immune_cells(slide, metadata, metadata_slide,clinicaldata, summary_df):
    n_Tcells = len(metadata_slide.loc[(metadata_slide.cell_type == 'helper_Tcell') | (metadata_slide.cell_type == 'cytotoxic_Tcell')])
    n_Bcells = len(metadata_slide.loc[metadata_slide.cell_type == 'Bcell'])
    n_CD8 = len(metadata_slide.loc[metadata_slide.cell_type == 'cytotoxic_Tcell'])  
    n_CD4 = len(metadata_slide.loc[(metadata_slide.cell_type == 'helper_Tcell')])
    n_lymphocytes = n_Tcells + n_Bcells
    n_neutrophils = len(metadata_slide.loc[(metadata_slide.cell_type == 'neutrophil')])

    n_Tumorcells = len(metadata_slide.loc[(metadata_slide.cell_type == 'tumor') | (metadata_slide.cell_type == 'tumor_cell')])
    Tcell_Tumor_ratio = n_Tcells/(n_Tumorcells + n_Tcells)
    Bcell_Tumor_ratio = n_Bcells/(n_Tumorcells + n_Bcells)
    #Tcell_Tumor_ratio = n_Tcells/n_Tumorcells
    #Bcell_Tumor_ratio = n_Bcells/n_Tumorcells
    T_B_ratio = n_Tcells/n_Bcells
    
    Neutrophil_Tumor_ratio = n_neutrophils/(n_neutrophils + n_Tumorcells)
    Lymphocytes_Tumor_ratio = n_lymphocytes/ (n_lymphocytes + n_Tumorcells)

    #Neutrophil : Lymphocyte Ratio
    NLR = n_neutrophils/n_lymphocytes

    summary_df.loc[slide, 'n_Tcells'] = n_Tcells
    summary_df.loc[slide, 'n_Bcells'] = n_Bcells
    summary_df.loc[slide, 'n_CD8_cytTcells'] = n_CD8
    summary_df.loc[slide, 'n_CD4_T_helpercells'] = n_CD4
    summary_df.loc[slide, 'n_neutrophils'] = n_neutrophils
    summary_df.loc[slide, 'n_lymphocytes'] = n_lymphocytes
    summary_df.loc[slide, 'T_B_ratio'] = T_B_ratio
    summary_df.loc[slide, 'Tcell_Tumor_ratio'] = Tcell_Tumor_ratio
    summary_df.loc[slide, 'Bcell_Tumor_ratio'] = Bcell_Tumor_ratio
    summary_df.loc[slide, 'Neutrophil_Tumor_ratio'] = Neutrophil_Tumor_ratio
    summary_df.loc[slide, 'Lymphocytes_Tumor_ratio'] = Lymphocytes_Tumor_ratio
    summary_df.loc[slide, 'NLR'] = NLR

    #Tim3 abundance 

    #T cell with PD1
    #pdb.set_trace()


def calc_stats(summary_df):
    recurrant_Tcell_tumor_ratio = summary_df.loc[summary_df['Recurred'] == 1, 'Tcell_Tumor_ratio']
    nonrecurrant_Tcell_tumor_ratio = summary_df.loc[summary_df['Recurred'] == 0, 'Tcell_Tumor_ratio']
    t_stat, p_value = stats.ttest_ind(list(recurrant_Tcell_tumor_ratio), list(nonrecurrant_Tcell_tumor_ratio))
    print("pval: Tcell_Tumor_ratio: ", p_value)

    gen_boxplot(recurrant_Tcell_tumor_ratio, nonrecurrant_Tcell_tumor_ratio, g1_name = 'recurrant_Tcell_tumor_ratio', g2_name = 'nonrecurrant_Tcell_tumor_ratio', pval = p_value)

    recurrant_Bcell_tumor_ratio = summary_df.loc[summary_df['Recurred'] == 1, 'Bcell_Tumor_ratio']
    nonrecurrant_Bcell_tumor_ratio = summary_df.loc[summary_df['Recurred'] == 0, 'Bcell_Tumor_ratio']
    t_stat, p_value = stats.ttest_ind(list(recurrant_Bcell_tumor_ratio), list(nonrecurrant_Bcell_tumor_ratio))
    print("pval: Bcell_Tumor_ratio: ",p_value)

    #Calculate the correlation between Lymphocytes and Neutrophils
    # Calculate Pearson correlation
    pearson_corr, pearson_pvalue  = pearsonr(summary_df['Lymphocytes_Tumor_ratio'], summary_df['Neutrophil_Tumor_ratio'])
    print(f"Pearson correlation: {pearson_corr:.3f}")

    # Calculate Spearman correlation
    spearman_corr, spearman_pvalue= spearmanr(summary_df['Lymphocytes_Tumor_ratio'], summary_df['Neutrophil_Tumor_ratio'])
    print(f"Spearman correlation: {spearman_corr:.3f}")

    #See if NLR correlates with any patient outcome
    recurrant_NLR = summary_df.loc[summary_df['Recurred'] == 1, 'NLR']
    nonrecurrant_NLR = summary_df.loc[summary_df['Recurred'] == 0, 'NLR']
    t_stat, p_value = stats.ttest_ind(list(recurrant_NLR), list(nonrecurrant_NLR))

    EarlyStage_NLR = summary_df.loc[summary_df['Stage'] == 'I-II', 'NLR']
    LateStage_NLR = summary_df.loc[summary_df['Stage'] == 'III-IV', 'NLR']
    t_stat, p_value = stats.ttest_ind(list(EarlyStage_NLR), list(LateStage_NLR))

    Grade1_NLR = summary_df.loc[summary_df['Grade'] == 1, 'NLR']
    Grade2_NLR = summary_df.loc[summary_df['Grade'] == 2, 'NLR']
    t_stat, p_value = stats.ttest_ind(list(Grade1_NLR), list(Grade2_NLR))

    IO_1_NLR = summary_df.loc[summary_df['IO response'] == 1, 'NLR']
    IO_0_NLR = summary_df.loc[summary_df['IO response'] == 0, 'NLR']
    t_stat, p_value = stats.ttest_ind(list(IO_1_NLR), list(IO_0_NLR))

    print("pval: NLR: ",p_value)

def gen_boxplot(group1, group2, g1_name, g2_name, pval):
    # Create a boxplot with both groups on the same plot
    plt.boxplot([group1, group2], labels=[g1_name, g2_name])
    # Overlay dots (using scatter)
    plt.scatter(np.ones(len(group1)), group1, color='blue', alpha=0.6, label='Group 1')
    plt.scatter(2 * np.ones(len(group2)), group2, color='orange', alpha=0.6, label='Group 2')

    # Add a title and axis labels
    plt.title('Comparison of Group 1 and Group 2')
    plt.ylabel('Values')    

    # Set y-limits to ensure the annotation is visible
    max_y = max(max(group1), max(group2))
    plt.ylim(bottom=min(min(group1), min(group2)) - .01, top=max_y + .01)

    # Add statistical significance annotation
    if pval < 0.05:
        significance = "***" if pval < 0.001 else "**" if pval < 0.01 else "*"
        # Position the text above the highest box
        plt.text(1.5, max_y + 0.2, f'p = {pval:.3f} {significance}',
                 horizontalalignment='center', fontsize=12, color='red')

    # Show legend
    #plt.legend(loc='upper right')

    # Show the plot
    plt.savefig(f"{g1_name}_{g2_name}.png")

    plt.close()

if __name__ == '__main__':
    cell_type_analysis()