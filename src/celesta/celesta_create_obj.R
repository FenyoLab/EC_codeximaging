library(CELESTA)
library(Rmixmod)
library(spdep)
library(ggplot2)
library(reshape2)
library(zeallot)
library(yaml)

set.seed(9)

# Parse command-line arguments
args <- commandArgs(trailingOnly = TRUE)
config <- yaml.load_file("../../config/config_celesta_pipeline.yaml")
sample <- args[1]

project_title <- paste0(config$project_title_prefix, "_", sample)
imaging_data_path <- file.path(config$paths$imaging_data_dir, paste0("imaging_data_", sample, ".csv"))
prior_marker_info_path <- config$paths$prior_marker_info
transform_type <- config$transform_type

results_dir <- config$paths$results_dir
if (!dir.exists(results_dir)) {
  dir.create(results_dir, recursive = TRUE)
}

cat("\n-------------------------------\n")
cat("Project title:", project_title, "\n")
cat("-------------------------------\n")

cat("Prior marker info:", prior_marker_info_path, "\n")
cat("Imaging data:", imaging_data_path, "\n")
cat("Transform type:", transform_type, "\n")
cat("Output directory:", results_dir, "\n")
cat("-------------------------------\n\n")

# Load input files
prior_marker_info <- read.csv(prior_marker_info_path)
imaging_data <- read.csv(imaging_data_path)

# Create output directory
output_folder <- file.path(results_dir, project_title)
if (!dir.exists(output_folder)) {
  dir.create(output_folder, recursive = TRUE)
}
setwd(output_folder)
cat("All results saved to:", output_folder, "\n")

# Create CELESTA object
cat("\n[Creating CELESTA object...]\n")

# Set transform_type=1 for arcsinh normalization or 0 for none
CelestaObj <- CreateCelestaObject(
  project_title=project_title, 
  prior_marker_info, 
  imaging_data, 
  transform_type=transform_type)

# Save CELESTA object
saveRDS(CelestaObj, file = file.path(output_folder, paste0(project_title, "_unassigned_CelestaObj.rds")))

cat("\n[CELESTA object created and saved.]\n")

# Save coords + marker expression probabilities to CSV
exp_prob <- as.data.frame(CelestaObj@marker_exp_prob)
coords <- as.data.frame(CelestaObj@coords)
combined_df <- cbind(coords, exp_prob)
output_path <- file.path(output_folder, paste0(project_title, "_marker_exp_prob.csv"))
write.csv(combined_df, file = output_path, row.names = FALSE)

cat("Saved marker expression probability CSV to:\n", output_path, "\n")


