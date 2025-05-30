cat("Loading required libraries...\n")
library(Seurat)
library(ggplot2)
library(plyr)  # for revalue()

cat("Setting random seed for reproducibility...\n")
set.seed(9)

cat("Loading immune subset...\n")
obj <- readRDS("/gpfs/home/yb2612/yb2612_fenyo/data/seurat_objects/immune/Cervical_srtv5_merged_obj_umap_immune_PCA_integratedHarmony_join_UMAP.rds")

cat("Joining layers...\n")
obj <- JoinLayers(obj)

# kmeans clutering on CD45RO expression
cat("Running K-means clustering on CD45RO expression...\n")

# Extract CD45RO expression from "data" layer safely
cd45ro_expr <- GetAssayData(obj, layer = "data")["CD45RO", ]

# Identify cells with CD45RO expression > 0
positive_cells <- cd45ro_expr > 0

# Run k-means on positive expression values
CD45RO_clu <- kmeans(as.numeric(cd45ro_expr[positive_cells]), centers = 3)

# Initialize full cluster vector with 0 for zero-expression cells
CD45RO_cluster <- rep(0, length(cd45ro_expr))
names(CD45RO_cluster) <- names(cd45ro_expr)

# Assign clusters for positive-expression cells
CD45RO_cluster[positive_cells] <- CD45RO_clu$cluster

# Add cluster metadata to Seurat object
obj <- AddMetaData(obj, metadata = CD45RO_cluster, col.name = "CD45RO_cluster")

# Map numeric cluster labels to descriptive names, ordering by cluster centers
cluster_order <- order(CD45RO_clu$centers)
cluster_map <- setNames(
  c("No_activation", "Low_activation", "Moderate_activation", "High_activation"),
  c(0, cluster_order)
)

obj$CD45RO_cluster <- plyr::revalue(as.character(obj$CD45RO_cluster), cluster_map)

saveRDS(obj, file = "/gpfs/home/yb2612/yb2612_fenyo/data/seurat_objects/immune/Cervical_srtv5_merged_obj_umap_immune_PCA_integratedHarmony_join_UMAP_CD45RO_cluster.rds")

# Set default assay to RNA
DefaultAssay(obj) <- "RNA"

clusters <- sort(unique(obj$CD45RO_cluster))
cat("Found", length(clusters), "clusters.\n")

Idents(obj) <- "CD45RO_cluster"

cat("Plotting violins for each cluster...\n")
VlnPlot(obj, features = "CD45RO", pt.size=0)
ggsave("/gpfs/home/yb2612/yb2612_fenyo/data/seurat_objects/plots/immune/immune_integratedHarmony_CD45RO_cluster_violin.png", width = 8, height = 6)

cat("Plotting UMAP colored by K-means clusters...\n")
umap_plot <- DimPlot(obj, reduction = "umap.harmony", group.by = "CD45RO_cluster", alpha = 0.5) +
  labs(title = "UMAP Plot colored by CD45RO cluster")
ggsave("/gpfs/home/yb2612/yb2612_fenyo/data/seurat_objects/plots/immune/immune_integratedHarmony_umap_by_CD45RO_cluster.png", plot=umap_plot, width = 8, height = 6)

cat("Plotting PCA colored by K-means clusters...\n")
pca_plot <- DimPlot(obj, reduction = "harmony", group.by = "CD45RO_cluster", alpha = 0.5) +
  labs(title = "PCA Plot colored by CD45RO cluster")
ggsave("/gpfs/home/yb2612/yb2612_fenyo/data/seurat_objects/plots/immune/immune_integratedHarmony_pca_by_CD45RO_cluster.png", plot=pca_plot, width = 8, height = 6)