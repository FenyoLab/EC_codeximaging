import os

from src.analysis import color_by_sample, color_by_marker, color_by_cluster, sample_per_cluster, expression_per_cluster

def clustering_analysis(save_path, n_clusters, channel_names, filtered_channel_names, out_suffix = 'analysis_figures'):

    output_path = f'{save_path}/{out_suffix}'
    output_path_bycluster = f'{save_path}/{out_suffix}/{n_clusters}_clusters'
    os.makedirs(output_path, exist_ok = True)
    os.makedirs(output_path_bycluster, exist_ok = True)

    umap_coord_path = os.path.join(save_path, 'umap/coord.npy')
    sample_names_path = os.path.join(save_path, 'normalized_matrix/cell_sample_names_filtered.npy')
    normal_matrix_path = os.path.join(save_path, 'normalized_matrix/matrix_normal.npy')
    kmeans_labels_path = os.path.join(save_path, f'clustering/{n_clusters}_clusters/kmeans_labels.npy')
    cluster_centroids_df_path = os.path.join(output_path_bycluster, 'cluster_centroids_df.csv')

    color_by_sample.umap_by_sample(umap_coord_path, sample_names_path, output_path, n_clusters)
    color_by_marker.umap_by_marker(umap_coord_path, normal_matrix_path, output_path, channel_names)
    color_by_cluster.umap_by_cluster(umap_coord_path, kmeans_labels_path, output_path_bycluster, n_clusters)
    expression_per_cluster.gen_cluster_centroid_matrix(normal_matrix_path, kmeans_labels_path, output_path_bycluster, n_clusters, channel_names)
    expression_per_cluster.plot_cluster_matrix_as_heatmap(cluster_centroids_df_path, output_path_bycluster, n_clusters, filtered_channel_names)
    sample_per_cluster.proportion_per_cluster(sample_names_path, kmeans_labels_path, output_path_bycluster, n_clusters)
