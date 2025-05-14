library(CELESTA)
library(Rmixmod)
library(spdep)
library(ggplot2)
library(reshape2)
library(zeallot)
library(argparse)

set.seed(9)

# -------------------------------------------
# # Parse command-line arguments

parser <- ArgumentParser(description = "Create CELESTA object with specified inputs")

parser$add_argument("--project_title", help = "Title of the project")
parser$add_argument("--prior_marker_info", help = "CSV file with prior marker info")
parser$add_argument("--imaging_data", help = "CSV file with imaging data")
parser$add_argument("--output_dir", help = "Path to output directory", default = "/gpfs/home/yb2612/yb2612_fenyo/results/celesta")
parser$add_argument("--transform_type", type = "integer", help = "0 for pre-normalized, 1 for arcsinh normalization")

args <- parser$parse_args()

project_title <- args$project_title
prior_marker_info_path <- args$prior_marker_info
output_dir <- args$output_dir
if (!dir.exists(output_dir)) {
  dir.create(output_dir, recursive = TRUE)
}
imaging_data_path <- args$imaging_data
transform_type <- args$transform_type


cat("\n-------------------------------\n")
cat("Project title:", project_title, "\n")
cat("-------------------------------\n")

cat("Prior marker info:", prior_marker_info_path, "\n")
cat("Imaging data:", imaging_data_path, "\n")
cat("Transform type:", transform_type, "\n")
cat("Output directory:", output_dir, "\n")
cat("-------------------------------\n\n")

# Load input files
prior_marker_info <- read.csv(prior_marker_info_path)
imaging_data <- read.csv(imaging_data_path)

# Create output directory
output_folder <- file.path(output_dir, project_title)
if (!dir.exists(output_folder)) {
  dir.create(output_folder, recursive = TRUE)
}
setwd(output_folder)
cat("All results saved to:", output_folder, "\n")

# Create CELESTA object
cat("\n[Creating CELESTA object...]\n")

# set transform_type=1 for arcsinh normalization, otherwise 0 if imaging_data is already normalized
CelestaObj <- CreateCelestaObject(project_title=project_title, prior_marker_info, imaging_data, transform_type=transform_type)

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


