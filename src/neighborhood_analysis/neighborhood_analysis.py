import os 
import sys
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns
import skimage
import pickle
from sklearn.cluster import MiniBatchKMeans

from knn_graph_neighborhood import Neighborhoods
from general import *

cells_df_path = 'path/to/cells_df'
cells_df = pd.read_csv(cells_df_path)

cells_df = cells_df[['slide_id','X','Y','cell_types']] 
#cells = cells[['Exp','X','Y','Cluster name2','100']] #what is 100!
cells_df.head()

ks = [10,20,30]
cluster_col = 'cell_types'
sum_cols = list(cells[cluster_col].unique())
cluster_cols = sum_cols  #[col for col in sum_cols]
keep_cols = ['slide_id', 'X', 'Y', cluster_col]
X = 'X'
Y = 'Y'
clusters = [10, 15, 20]

#exclude_cols = ['col_name']
#cluster_cols = [a for a in sum_cols if a not in exclude_cols]


neighborhood = Neighborhoods(cells_df, ks = ks, cluster_col = cluster_col,
                      sum_cols=sum_cols, keep_cols=keep_cols, X = X, Y= Y,
                      add_dummies=True)
cluster_windows = neighborhood.k_windows()

BASE = cells_df[keep_cols]

for k in ks:
    for n_cluster in clusters:

        #extract data for clustering 
        X_ = cluster_windows[k][cluster_cols].values
        #normalize data - now contains proportions, not raw counts 
        X = X_/X_.sum(1,keepdims = True)
        #replace NaNs with 0 
        X[np.isnan(X)] = 0

        #status messsage 
        print ('clustering - ws:{} n_clusters: {}'.format(k,n_clusters))
        #assign column name to new cluster column for df and confirms that its a new column 
        col_name = 'cluster_col{}_ws{}_clusts{}_noECM'.format(cluster_col,k,n_clusters)
        assert col_name not in BASE.columns
        
        #performs clustering based on proportions of cell types in cell neighborhood
        #and adds the resulting cluster labels to a new column to BASE df 
        BASE[col_name] = MiniBatchKMeans(random_state = 5,n_clusters=n_clusters).fit(X).labels_

catplot(BASE, hue = 'clustering_col', #column name of interest in BASE
        palette = {i:colors[i] for i in range(len(colors))}, figsize = 15, size = 4) #savefig
