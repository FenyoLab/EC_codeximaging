library(CELESTA)
library(Rmixmod)
library(spdep)
library(ggplot2)
library(reshape2)
library(zeallot)

#-----------------------------
# EDIT THIS
project_title <- "endometrial_test_normal" 
cat("Project title:", project_title)

# markers in prior_marker_info must EXACTLY match markers in imaging_data
prior_marker_info <- read.csv("/gpfs/home/yb2612/yb2612_fenyo/data/celesta/endometrial_test/prior_marker_info_3P_noCD20.csv")

# imaging_data cannot contain any markers with all 0 values
imaging_data <- read.csv("/gpfs/home/yb2612/yb2612_fenyo/data/celesta/endometrial_test/imaging_data_3P_normal_noCD20.csv")
#-----------------------------

# set/create output folder based on project title
output_folder <- paste0("/gpfs/home/yb2612/yb2612_fenyo/results/celesta/",project_title)
if (!dir.exists(output_folder)) {
  dir.create(output_folder)
}
setwd(output_folder)
cat("\nAll results saved to:", output_folder)

### The pre-saved imaging data is taken from reg009 of the published CODEX data Schurch et al. Cell,2020

### Create CELESTA object
cat("\n\n-------------------------------")
cat("\nCreating CELESTA object...")
cat("\n-------------------------------\n")
CelestaObj <- CreateCelestaObject(project_title=project_title, prior_marker_info, imaging_data, transform_type=0)

### Filter out questionable cells. 
### **This step is optional.** We suggest starting without running this step to see whether there are many doublets/triplets.
# CelestaObj <- FilterCells(CelestaObj,high_marker_threshold=0.9, low_marker_threshold=0.4)

### Assign cell types. 
### max_iteration = maximum iterations allowed in the EM algorithm per round. 
### cell_change_threshold = user-defined ending condition for the EM algorithm. 
### For example, 0.01 means that when fewer than 1% of the total number of cells do not change identity, the algorithm will stop.
cat("\n\n-------------------------------")
cat("\nAssigning cell types...")
cat("\n-------------------------------\n")
CelestaObj <- AssignCells(CelestaObj,max_iteration=10,cell_change_threshold=0.01,
                          high_expression_threshold_anchor=high_marker_threshold_anchor,
                          low_expression_threshold_anchor=low_marker_threshold_anchor,
                          high_expression_threshold_index=high_marker_threshold_iteration,
                          low_expression_threshold_index=low_marker_threshold_iteration,
                          save_result = T)

### Plot cells with CELESTA assigned cell types.
### plots corresponding cell types given in the "cell_number_to_use" parameter
### vasculature 1 - yellow, tumor cells 2 - red, asma stroma 3 - royalblue, granulocyte 7 - white, macrophage 10 - cyan, cd8 t cells 13 - orchid, cd4 t cells 14 - green, cd4 t cells cd45ro+ 15 - green
cat("\n\n-------------------------------")
cat("\nPlotting cells...")
cat("\n-------------------------------\n")
PlotCellsAnyCombination(cell_type_assignment_to_plot=CelestaObj@final_cell_type_assignment[,(CelestaObj@total_rounds+1)],
                        coords = CelestaObj@coords,
                        prior_info = prior_marker_info,
                        cell_number_to_use=c(1,2,3,7,10,13,14,15),  # 0 is unknown
                        cell_type_colors=c("yellow","red","royalblue","white","cyan","orchid","chartreuse3","chartreuse3"), # default is gray for unknown
                        test_size=3,
                        save_plot = TRUE,
                        output_dir = output_folder)  

### Plot expression probability of all protein markers
cat("\n\n-------------------------------")
cat("\nPlotting expression probability...")
cat("\n-------------------------------\n")
PlotExpProb(coords=CelestaObj@coords,
            marker_exp_prob=CelestaObj@marker_exp_prob,
            prior_marker_info = prior_marker_info,
            save_plot = TRUE,
            output_dir = output_folder)

cat("\n\n-------------------------------")
cat("\nFinished!")
cat("\n-------------------------------")