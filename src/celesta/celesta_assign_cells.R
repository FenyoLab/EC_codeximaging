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

parser$add_argument("--project_title", help = "Same title as in create_celesta_obj.sh, name of subdirectory in results_dir.")

parser$add_argument("--results_dir", help = "Path to results directory created by create_celesta_obj.sh", default = "/gpfs/data/proteomics/home/yb2612/results/celesta")

parser$add_argument("--high_anchor", nargs = "+", type = "double",
                    help = "High marker thresholds for anchor round (space-separated)", 
                    required = FALSE, default = NULL)

parser$add_argument("--high_iter", nargs = "+", type = "double",
                    help = "High marker thresholds for iteration rounds (space-separated)", 
                    required = FALSE, default = NULL)

parser$add_argument("--low_anchor", nargs = "+", type = "double",
                    help = "Low marker thresholds for anchor round (space-separated)", 
                    required = FALSE, default = NULL)

parser$add_argument("--low_iter", nargs = "+", type = "double",
                    help = "Low marker thresholds for iteration rounds (space-separated)", 
                    required = FALSE, default = NULL)

args <- parser$parse_args()

project_title <- args$project_title
celesta_obj_path <- paste0(args$results_dir, "/", project_title, "/", project_title, "_unassigned_CelestaObj.rds")

results_dir <- args$results_dir

high_marker_threshold_anchor <- if (!is.null(args$high_anchor)) args$high_anchor else rep(0.7, 50)
high_marker_threshold_iteration <- if (!is.null(args$high_iter)) args$high_iter else rep(0.5, 50)
low_marker_threshold_anchor <- if (!is.null(args$low_anchor)) args$low_anchor else rep(0.9, 50)
low_marker_threshold_iteration <- if (!is.null(args$low_iter)) args$low_iter else rep(1.0, 50)

cat("\n-------------------------------\n")
cat("Project title:", project_title, "\n")
cat("-------------------------------\n")

cat("Output directory:", results_dir, "\n")
cat("CELESTA object path:", celesta_obj_path, "\n")
cat("High marker threshold (anchor):", paste(high_marker_threshold_anchor, collapse = ", "), "\n")
cat("High marker threshold (iteration):", paste(high_marker_threshold_iteration, collapse = ", "), "\n")
cat("Low marker threshold (anchor):", paste(low_marker_threshold_anchor, collapse = ", "), "\n")
cat("Low marker threshold (iteration):", paste(low_marker_threshold_iteration, collapse = ", "), "\n")
cat("-------------------------------\n\n")

# Create output directory
output_folder <- file.path(results_dir, project_title)
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
                          save_result = F)

# Determine whether thresholds are default
is_default <- function(arg, default_val) {
  is.null(arg) || all(arg == rep(default_val, length(arg)))
}

# Label for each threshold group
high_anchor_label <- if (is_default(args$high_anchor, 0.7)) "high_anchor_default" else paste0("high_anchor_", paste(high_marker_threshold_anchor, collapse = "_"))
high_iter_label  <- if (is_default(args$high_iter, 0.5)) "high_iter_default" else paste0("high_iter_", paste(high_marker_threshold_iteration, collapse = "_"))

cat("\n[Saving CELESTA object...]\n")

saveRDS(
  CelestaObj,
  file = file.path(
    output_folder,
    paste0(
      project_title, "_",
      high_anchor_label, "_",
      high_iter_label,
      "_CelestaObj.rds"
    )
  )
)

# Save coords + final cell type assignment to CSV
final_assign <- as.data.frame(CelestaObj@final_cell_type_assignment)
coords <- as.data.frame(CelestaObj@coords)
combined_df <- cbind(coords, final_assign)
output_path <- file.path(
    output_folder,
    paste0(
      project_title, "_",
      high_anchor_label, "_",
      high_iter_label,
      "_final_cell_type_assignment.csv"
    )
  )
write.csv(combined_df, file = output_path, row.names = FALSE)

cat("Saved final cell type assignments CSV to:\n", output_path, "\n")

cat("\n[Saving CELESTA object...]\n")

saveRDS(
  CelestaObj,
  file = file.path(
    output_folder,
    paste0(
      project_title, "_",
      high_anchor_label, "_",
      high_iter_label,
      "_CelestaObj.rds"
    )
  )
)

cat("\n[Finished!]\n")