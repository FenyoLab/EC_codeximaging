library(Seurat)

immune <- readRDS('/gpfs/home/yb2612/yb2612_fenyo/data/seurat_objects/immune/Cervical_srtv5_merged_obj_umap_immune_PCA_integratedHarmony_join_UMAP_CD45RO_cluster.rds')
metadata <- immune@meta.data

write.table(metadata, '/gpfs/home/yb2612/yb2612_fenyo/data/seurat_objects/immune/Cervical_srtv5_merged_obj_umap_immune_PCA_integratedHarmony_join_UMAP_CD45RO_cluster_metadata.csv', quote=FALSE, sep=",")
