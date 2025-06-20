cat("Loading required libraries...\n")
library(Seurat)
library(harmony)
library(ggplot2)

cat("Setting random seed for reproducibility...\n")
set.seed(9)

load 
cat("Loading full object...\n")
obj <- readRDS("/gpfs/home/yb2612/yb2612_fenyo/data/seurat_objects/Cervical_srtv5_merged_obj_umap.rds")

# subset to immune cells
cat("Subsetting to immune cells...\n")
obj <- subset(obj, subset = Final.cell.type %in% c("Macrophage_CD163neg", 
                                                   "Macrophage_CD163pos", 
                                                   "Neutrophil", 
                                                   "B", 
                                                   "T", 
                                                   "CD8_T", 
                                                   "CD4_T", 
                                                   "Cytotoxic_NK", 
                                                   "Exhausted_CD8", 
                                                   "Treg", 
                                                   "Th1"))

cat("Saving subsetted object...\n")
saveRDS(obj, file = "/gpfs/home/yb2612/yb2612_fenyo/data/seurat_objects/immune/Cervical_srtv5_merged_obj_umap_immune.rds")

# join layers
cat("Joining layers...\n")
obj = JoinLayers(obj)

# split by orig.ident
cat("Splitting by sample...\n")
obj[["RNA"]] = split(obj[["RNA"]], f = obj$orig.ident)

cat("Setting variable features to all genes...\n")
# set var features to all
VariableFeatures(obj) <- rownames(obj)
all.genes = rownames(obj)

# scale
cat("Scaling data...\n")
obj = ScaleData(obj, features = all.genes)

# run PCA
cat("Running PCA...\n")
obj = RunPCA(obj, npcs=30)

cat("Saving PCA results...\n")
saveRDS(obj, file = "/gpfs/home/yb2612/yb2612_fenyo/data/seurat_objects/immune/Cervical_srtv5_merged_obj_umap_immune_PCA.rds")

# integrate with harmony
cat("Integrating with Harmony...\n")
obj <- IntegrateLayers(object = obj, method = HarmonyIntegration, orig.reduction = "pca",
  new.reduction = 'harmony', verbose = TRUE)

cat("Saving integrated Harmony results...\n")
saveRDS(obj, file = "/gpfs/home/yb2612/yb2612_fenyo/data/seurat_objects/immune/Cervical_srtv5_merged_obj_umap_immune_PCA_integratedHarmony.rds")

cat("Joining layers...\n")
obj = JoinLayers(obj)

cat("Saving joined layers...\n")
saveRDS(obj, file = "/gpfs/home/yb2612/yb2612_fenyo/data/seurat_objects/immune/Cervical_srtv5_merged_obj_umap_immune_PCA_integratedHarmony_join.rds")

# plot PCA
cat("Plotting PCA...\n")
pca_plot <- DimPlot(obj, reduction = "harmony", group.by = "orig.ident", alpha = 0.5) +
  labs(title = "PCA Plot colored by Sample")

ggsave("/gpfs/home/yb2612/yb2612_fenyo/data/seurat_objects/plots/immune/immune_integratedHarmony_pca_by_sample.png", plot = pca_plot, width = 8, height = 6)

pca_plot <- DimPlot(obj, reduction = "harmony", group.by = "Final.cell.type", alpha = 0.5) +
  labs(title = "PCA Plot colored by Cell Type")

ggsave("/gpfs/home/yb2612/yb2612_fenyo/data/seurat_objects/plots/immune/immune_integratedHarmony_pca_by_celltype.png", plot = pca_plot, width = 8, height = 6)

pca_plot <- FeaturePlot(obj, features = "CD45RO", order = TRUE, keep.scale = "all", min.cutoff = "q10", max.cutoff = "q90", reduction = "harmony") + 
    theme(legend.position = "right")

ggsave("/gpfs/home/yb2612/yb2612_fenyo/data/seurat_objects/plots/immune/immune_integratedHarmony_pca_by_CD45RO.png", plot = pca_plot, width = 8, height = 6)
cat("PCA plots saved.\n")

# run umap
cat("Running UMAP...\n")
obj <- RunUMAP(obj, dims = 1:30, reduction.name="umap.harmony", reduction = "harmony")

cat("Saving UMAP results...\n")
saveRDS(obj, file = "/gpfs/home/yb2612/yb2612_fenyo/data/seurat_objects/immune/Cervical_srtv5_merged_obj_umap_immune_PCA_integratedHarmony_join_UMAP.rds")

# plot UMAPs
cat("Plotting UMAPs...\n")
umap_plot <- DimPlot(obj, reduction = "umap.harmony", group.by = "orig.ident", alpha = 0.5) +
  labs(title = "UMAP Plot colored by Sample")

ggsave("/gpfs/home/yb2612/yb2612_fenyo/data/seurat_objects/plots/immune/immune_integratedHarmony_umap_by_sample.png", plot = umap_plot, width = 8, height = 6)

umap_plot <- DimPlot(obj, reduction = "umap.harmony", group.by = "Final.cell.type", alpha = 0.5) +
  labs(title = "UMAP Plot colored by Cell Type")

ggsave("/gpfs/home/yb2612/yb2612_fenyo/data/seurat_objects/plots/immune/immune_integratedHarmony_umap_by_celltype.png", plot = umap_plot, width = 8, height = 6)

umap_plot <- FeaturePlot(obj, features = "CD45RO", order = TRUE, keep.scale = "all", min.cutoff = "q10", max.cutoff = "q90", reduction = "umap.harmony") + 
    theme(legend.position = "right")

ggsave("/gpfs/home/yb2612/yb2612_fenyo/data/seurat_objects/plots/immune/immune_integratedHarmony_umap_by_CD45RO.png", plot = umap_plot, width = 8, height = 6)
cat("UMAP plots saved.\n")


