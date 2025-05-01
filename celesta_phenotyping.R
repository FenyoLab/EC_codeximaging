library(CELESTA)
library(Rmixmod)
library(spdep)
library(ggplot2)
library(reshape2)
library(zeallot)

# -------------------------------------------
# Parse command-line arguments
args <- commandArgs(trailingOnly = TRUE)

if (length(args) < 4) {
  stop("Usage: Rscript script.R <project_title> <prior_marker_info.csv> <imaging_data.csv> <transform_type>")
}

project_title <- args[1]
prior_marker_info_path <- args[2]
imaging_data_path <- args[3]
transform_type <- as.integer(args[4])

cat("\n-------------------------------\n")
cat("Project title:", project_title, "\n")
cat("-------------------------------\n")

cat("Prior marker info:", prior_marker_info_path, "\n")
cat("Imaging data:", imaging_data_path, "\n")
cat("Transform type:", transform_type, "\n")
# -------------------------------------------

# Load input files
prior_marker_info <- read.csv(prior_marker_info_path)
imaging_data <- read.csv(imaging_data_path)

# Create output directory
output_folder <- file.path("/gpfs/home/yb2612/yb2612_fenyo/results/celesta", project_title)
if (!dir.exists(output_folder)) {
  dir.create(output_folder, recursive = TRUE)
}
setwd(output_folder)
cat("All results saved to:", output_folder, "\n")

### The pre-saved imaging data is taken from reg009 of the published CODEX data Schurch et al. Cell,2020

### Create CELESTA object
cat("\n[Creating CELESTA object...]\n")

# set transform_type=1 for arcsinh normalization, otherwise 0 if imaging_data is already normalized
CelestaObj <- CreateCelestaObject(project_title=project_title, prior_marker_info, imaging_data, transform_type=0)

### Filter out questionable cells. 
### **This step is optional.** We suggest starting without running this step to see whether there are many doublets/triplets.
# CelestaObj <- FilterCells(CelestaObj,high_marker_threshold=0.9, low_marker_threshold=0.4)

### Assign cell types. 
### max_iteration = maximum iterations allowed in the EM algorithm per round. 
### cell_change_threshold = user-defined ending condition for the EM algorithm. 
### For example, 0.01 means that when fewer than 1% of the total number of cells do not change identity, the algorithm will stop.
cat("\n[Assigning cell types...]\n")
high_marker_threshold_anchor=c(0.8, 0.6, 0.8, 0.8, 0.5, 0.7, 0.6, 0.8, 0.6, 0.8)
high_marker_threshold_iteration=c(0.7, 0.5, 0.7, 0.7, 0.5, 0.6, 0.5, 0.7, 0.5, 0.7)
low_marker_threshold_anchor=c(1,1,1,1,1,1,1,1,1,1)
low_marker_threshold_iteration=c(1,1,1,1,1,1,1,1,1,1)

CelestaObj <- AssignCells(CelestaObj,max_iteration=10,cell_change_threshold=0.01,
                          high_expression_threshold_anchor=high_marker_threshold_anchor,
                          low_expression_threshold_anchor=low_marker_threshold_anchor,
                          high_expression_threshold_index=high_marker_threshold_iteration,
                          low_expression_threshold_index=low_marker_threshold_iteration,
                          save_result = T)

### Plot cells with CELESTA assigned cell types.
### plots corresponding cell types given in the "cell_number_to_use" parameter

cat("\nPlotting cells...")
PlotCellsAnyCombination(cell_type_assignment_to_plot=CelestaObj@final_cell_type_assignment[,(CelestaObj@total_rounds+1)],
                        coords = CelestaObj@coords,
                        prior_info = prior_marker_info,
                        cell_number_to_use=c(0,1,2,3,4,5,6,7,8,9,10),  # 0 is unknown
                        cell_type_colors = c(
                          "yellow",
                          "red",
                          "royalblue",
                          "white",
                          "cyan",
                          "orchid",
                          "chartreuse3",
                          "orange",
                          "darkgreen",
                          "goldenrod"
                        ),
                        test_size=0.5,
                        save_plot = TRUE,
                        output_dir = output_folder)  

### Plot expression probability of all protein markers

cat("\nPlotting expression probability...")
PlotExpProb(coords=CelestaObj@coords,
            marker_exp_prob=CelestaObj@marker_exp_prob,
            prior_marker_info = prior_marker_info,
            save_plot = TRUE,
            output_dir = output_folder)

cat("\nFinished!")
