# TODO: clean up code, remove hardcoded paths

library(ggplot2)
library(stringr)
library(rlang)
library(dplyr)
library(reshape2)

set.seed(9)

cat("Loading total_metadata...\n")
total_metadata <- read.csv("/gpfs/home/yb2612/yb2612_fenyo/data/seurat_objects/Cervical_v5_obj_metadata_total_metadata_radial_distances_kmeans_parent.csv")

# Pad sample names with 0s to width 5
total_metadata$orig.ident <- str_pad(total_metadata$orig.ident, 5, pad = "0")

samples_chosen <- unique(total_metadata$orig.ident)
cat("Samples to be plotted: ", paste(samples_chosen, collapse = ", "), "\n")

# Define colors for kmeans categories
dist_colors <- c(
  Near = "#3B0F70",              # deep purple
  Peri = "#B63640",   # rich red
  Far = "#F6C141"                # warm yellow
)

# Define cell type colors for stacked bar plot
cell_type_colors <- c(
  # undefined - gray
  Stromal_Undefined_Unknown = "#AAAAAA",  # gray
  # tumor - red
  Tumor = "#790000",           # dark red
  Cycling_Tumor = "#D60000",   # bright red
  # endothelial - beige
  Endothelial = "#A17569",     # muted beige
  # B - orange
  B = "#C25A00",                # dark orange
  Activated_B = "#FFA52F",     # orange
  # neutrophil - yellow
  Neutrophil = "#FDF490",           # pastel yellow
  Activated_Neutrophil = "#FFD700",  # bright yellow
  # macrophage - blue
  Macrophage_CD163neg = "#0774D8",              # cobalt blue
  Activated_Macrophage_CD163neg = "#9AE4FF",    # light sky blue
  Macrophage_CD163pos = "#0000DD",              # royal blue
  Activated_Macrophage_CD163pos = "#00ACC6",    # cyan bluesb
  # T - coral
  T = "#EDB8B8",            # light pink
  Activated_T = "#FF7266",  # coral red
  # CD4_T - green
  CD4_T = "#004B00",                # dark green
  Activated_CD4_T = "#97FF00",      # neon lime
  Treg = "#005659",                 # teal
  Activated_Treg = "#00FDCF",       # turquoise
  Th1 = "#5D7E66",                  # dusty green
  Activated_Th1 = "#018700",        # forest green
  # CD8_T - pink/purple
  CD8_T = "#6B004F",                    # dark magenta
  Activated_CD8_T = "#BF03B8",          # magenta
  Exhausted_CD8 = "#FF7ED1",            # pink
  Activated_Exhausted_CD8 = "#EB0077",   # hot pink
  Cytotoxic_NK = "#645474",             # muted purple
  Activated_Cytotoxic_NK = "#8C3BFF"   # purple violet
)

# Output directory
output_dir <- "/gpfs/home/yb2612/yb2612_fenyo/data/seurat_objects/plots"
dir.create(output_dir, showWarnings = FALSE, recursive = TRUE)

# Loop over samples
for (sam in samples_chosen) {
  message("Processing sample: ", sam)
  chosen_sample <- total_metadata[total_metadata$orig.ident == sam, ]
  
  # Loop over cell types in the chosen sample
  for (cell_type in unique(chosen_sample$Fine.cell.type)) {
    message("  > Processing cell type: ", cell_type)
    
    # Radial distance plot
    rdist_col <- paste0("r_dist_", cell_type)
    if (!rdist_col %in% names(chosen_sample)) {
      message("  >> Skipping rdist plot: column ", rdist_col, " not found.")
      next
    }
    rdist_plot <- ggplot(chosen_sample, aes(x = absolute_x, y = absolute_y, color = !!sym(rdist_col))) +
      geom_point(size = 0.3) +
      scale_color_viridis_c(option = "magma") +
      scale_y_reverse() +
      theme_classic()
    
    ggsave(
      filename = file.path(output_dir, paste0("rdist_plots/Cervical_v5_", sam, "_", cell_type, "_rdist_plot.png")),
      plot = rdist_plot, width = 15, height = 15
    )
    message("  >> Saved rdist plot")
    
    # Check if the kmeans column exists
    kmeans_col <- paste0(cell_type, "_dist_kmeans")
    if (!kmeans_col %in% names(chosen_sample)) {
      message("  >> Skipping kmeans plots: column ", kmeans_col, " not found.")
      next
    }

    # K-means distance plot
    kmeans_plot <- ggplot(chosen_sample, aes(x = absolute_x, y = absolute_y, color = !!sym(kmeans_col))) +
      geom_point(size = 0.3) +
      scale_y_reverse() +
      theme_classic() +
      scale_color_manual(values = dist_colors, na.value = "gray") +
      guides(color = guide_legend(override.aes = list(size = 3)))
    
    ggsave(
      filename = file.path(output_dir, paste0("dist_kmeans_plots/Cervical_v5_", sam, "_", cell_type, "_dist_kmeans_plot.png")),
      plot = kmeans_plot, width = 15, height = 15
    )
    message("  >> Saved dist_kmeans plot")

    # Proportions plot
    gplot_mat <- table(chosen_sample$Fine.cell.type, chosen_sample[[kmeans_col]]) %>%
      melt() %>%
      rename(CellType = Var1, KmeansCluster = Var2, Count = value)

    # Replace NA with the cell type name
    gplot_mat$KmeansCluster <- as.character(gplot_mat$KmeansCluster)
    gplot_mat$KmeansCluster[is.na(gplot_mat$KmeansCluster)] <- cell_type

    # Reorder levels so the cell type appears first
    gplot_mat$KmeansCluster <- factor(
      gplot_mat$KmeansCluster,
      levels = c(cell_type, "Near", "Peri", "Far")
    )

    # Plot
    bar_plot <- ggplot(gplot_mat, aes(x = KmeansCluster, y = Count, fill = CellType)) +
      geom_bar(stat = "identity", position = "fill") +
      scale_fill_manual(values = cell_type_colors) +
      theme_classic() +
      labs(x = paste(cell_type, "distance group"), y = "Proportion", fill = "Cell Type") +
      theme(axis.text.x = element_text(angle = 45, hjust = 1))

    ggsave(
      filename = file.path(output_dir, paste0("dist_proportions_plots/Cervical_v5_", sam, "_", cell_type, "_dist_proportions_plot.png")),
      plot = bar_plot, width = 10, height = 7
    )
    message("  >> Saved proportions plot")
  }
}
