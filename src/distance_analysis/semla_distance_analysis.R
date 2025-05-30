library(semla)

# total metadata
cat("Loading total metadata...\n")
total_metadata <- read.csv("/gpfs/home/yb2612/yb2612_fenyo/data/seurat_objects/Cervical_v5_obj_metadata_noUnknown.csv", row.names = 1)

# choose samples
samples_chosen<-unique(total_metadata$orig.ident)
samples_chosen<-samples_chosen[c(1:5,7)]
cat("Samples chosen for distance analysis: ", paste(samples_chosen, collapse = ", "), "\n")

# coords list
coords_list<-list()
for( sam in samples_chosen){
coords_list[[sam]] <- data.frame(
  barcode = rownames(total_metadata)[total_metadata$orig.ident==sam],
  x = total_metadata$x[total_metadata$orig.ident==sam],
  y = total_metadata$y[total_metadata$orig.ident==sam],
  sampleID = rep(1,times = sum(total_metadata$orig.ident==sam)),
  stringsAsFactors = FALSE
)
}

# distance analysis
cat("Calculating radial distances...\n")
for(sam in samples_chosen){
    print(paste0("Running sample: ", sam))
for(x in unique(total_metadata$Fine.cell.type[total_metadata$orig.ident==sam])){
    spots<-rownames(total_metadata)[total_metadata$Fine.cell.type==x & total_metadata$orig.ident==sam]
    head(spots)
    radial_distances <- RadialDistance(coords_list[[sam]][,1:4], spots, convert_to_microns = F, maxDist=200, remove_singletons = F)
    total_metadata[total_metadata$orig.ident==sam,paste0("r_dist_",x)]<-radial_distances
}
}

cat("Saving metadata...\n")
write.csv(total_metadata, "/gpfs/home/yb2612/yb2612_fenyo/data/seurat_objects/Cervical_v5_obj_metadata_1to5_7_radial_distances.csv")