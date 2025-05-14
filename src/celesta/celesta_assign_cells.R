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

parser <- ArgumentParser(description = "Run CELESTA with specified inputs and thresholds")

parser$add_argument("--project_title", help = "Title of the project")
parser$add_argument("--celesta_obj_path", help = "Path to unassigned CELESTA object (RDS file)")
parser$add_argument("--output_dir", help = "Path to output directory", default = "/gpfs/home/yb2612/yb2612_fenyo/results/celesta")

parser$add_argument("--high_anchor", nargs = "+", type = "double",
                    help = "High marker thresholds for anchor round (space-separated)", required = TRUE)

parser$add_argument("--high_iter", nargs = "+", type = "double",
                    help = "High marker thresholds for iteration rounds (space-separated)", required = TRUE)

parser$add_argument("--low_anchor", nargs = "+", type = "double",
                    help = "Low marker thresholds for anchor round (space-separated)", required = TRUE)

parser$add_argument("--low_iter", nargs = "+", type = "double",
                    help = "Low marker thresholds for iteration rounds (space-separated)", required = TRUE)

args <- parser$parse_args()

project_title <- args$project_title
celesta_obj_path <- args$celesta_obj_path
output_dir <- args$output_dir
if (!dir.exists(output_dir)) {
  dir.create(output_dir, recursive = TRUE)
}

high_marker_threshold_anchor <- args$high_anchor
high_marker_threshold_iteration <- args$high_iter
low_marker_threshold_anchor <- args$low_anchor
low_marker_threshold_iteration <- args$low_iter


cat("\n-------------------------------\n")
cat("Project title:", project_title, "\n")
cat("-------------------------------\n")

cat("Output directory:", output_dir, "\n")
cat("CELESTA object path:", celesta_obj_path, "\n")
cat("High marker threshold (anchor):", paste(high_marker_threshold_anchor, collapse = ", "), "\n")
cat("High marker threshold (iteration):", paste(high_marker_threshold_iteration, collapse = ", "), "\n")
cat("Low marker threshold (anchor):", paste(low_marker_threshold_anchor, collapse = ", "), "\n")
cat("Low marker threshold (iteration):", paste(low_marker_threshold_iteration, collapse = ", "), "\n")
cat("-------------------------------\n\n")

# Create output directory
output_folder <- file.path(output_dir, project_title)
if (!dir.exists(output_folder)) {
  dir.create(output_folder, recursive = TRUE)
}
setwd(output_folder)
cat("All results saved to:", output_folder, "\n")

# Load CELESTA object
CelestaObj <- readRDS(celesta_obj_path)
cat("Loaded CELESTA object from:", celesta_obj_path, "\n")

### Assign cell types. 
### max_iteration = maximum iterations allowed in the EM algorithm per round. 
### cell_change_threshold = user-defined ending condition for the EM algorithm. 
### For example, 0.01 means that when fewer than 1% of the total number of cells do not change identity, the algorithm will stop.

cat("\n[Assigning cell types...]\n")
CelestaObj <- AssignCells(CelestaObj,max_iteration=10,cell_change_threshold=0.01,
                          high_expression_threshold_anchor=high_marker_threshold_anchor,
                          low_expression_threshold_anchor=low_marker_threshold_anchor,
                          high_expression_threshold_index=high_marker_threshold_iteration,
                          low_expression_threshold_index=low_marker_threshold_iteration,
                          save_result = T)

# Save coords + final cell type assignment to CSV
final_assign <- as.data.frame(CelestaObj@final_cell_type_assignment)
coords <- as.data.frame(CelestaObj@coords)
combined_df <- cbind(coords, final_assign)
output_path <- file.path(
    output_folder,
    paste0(
      project_title,
      "_high_anchor_", paste(high_marker_threshold_anchor, collapse = "_"),
      "_high_iter_", paste(high_marker_threshold_iteration, collapse = "_"),
      "_final_cell_type_assignment.csv"
    )
  )
write.csv(combined_df, file = output_path, row.names = FALSE)

cat("Saved final cell type assignments CSV to:\n", output_path, "\n")

cat("\n[Saving CELESTA object...]\n")
# Save CELESTA object
saveRDS(
  CelestaObj,
  file = file.path(
    output_folder,
    paste0(
      project_title,
      "_high_anchor_", paste(high_marker_threshold_anchor, collapse = "_"),
      "_high_iter_", paste(high_marker_threshold_iteration, collapse = "_"),
      "_CelestaObj.rds"
    )
  )
)

cat("\n[Finished!]\n")