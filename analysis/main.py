"""
main.py
-------
Entry point for the EC mIF analysis pipeline.

Usage:
    python main.py

All parameters are set in config.py. Toggle analysis modules by setting the
RUN_* flags to True or False in config.py.
"""

import config
from utils.io import load_data
from scimap.neighborhoods import run_neighborhoods
from analysis.proportions import gen_proportion_summary_table, gen_proportion_Tcells
from analysis.ratios import gen_cell_type_ratio_summary_table
from analysis.fraction_intra import gen_fraction_intra_summary_table
from analysis.spatial import (
    gen_median_distance_summary_table,
    gen_scimap_interaction_summary_table,
    interactions_permutation_test
)


def main():

    metadata, clinical_df = load_data(config.RESULTS_DIR, config.METADATA_PATH, config.CLINICAL_DIR)

    # Shared keyword arguments passed to most analysis functions
    shared_kwargs = dict(
        metadata=metadata,
        results_dir=config.RESULTS_DIR,
        clinical_df=clinical_df,
        cell_type_columns=config.CELL_TYPE_COLUMNS,
        artifact_cells=config.ARTIFACT_CELLS,
        clinical_vars_list=config.CLINICAL_VARS_LIST,
        basic_cell_types=config.BASIC_CELL_TYPES,
        cell_types_remove=config.CELL_TYPES_REMOVE,
        samples_skip=config.SAMPLES_SKIP,
        gen_summary_csv=config.GEN_SUMMARY_CSV,
        run_gen_boxplots=config.RUN_GEN_BOXPLOTS,
        sample_label=config.SAMPLE_LABEL,
        add_color_points_stage=config.ADD_COLOR_POINTS_STAGE,
        title_font_size=config.TITLE_FONT_SIZE,
        subtitle_font_size=config.SUBTITLE_FONT_SIZE,
        y_tick_font_size=config.Y_TICK_FONT_SIZE,
        x_tick_font_size=config.X_TICK_FONT_SIZE,
        p_value_tick_font_size=config.P_VALUE_TICK_FONT_SIZE,
        x_tick_labels_dict=config.X_TICK_LABELS_DICT,
        cell_types_rename=config.CELL_TYPES_RENAME,
        add_plot_title=config.ADD_PLOT_TITLE,
        gen_new_marker_positivity_proportion=config.GEN_NEW_MARKER_POSITIVITY_PROPORTION,
        boxplot_shapes=config.BOXPLOT_SHAPES,
        run_permutation_test=config.RUN_PERMUTATION_TEST,
    )

    if config.RUN_GEN_PROPORTION_SUMMARY_TABLE:
        print("Running: cell type proportion analysis...")
        gen_proportion_summary_table(**shared_kwargs)

    if config.RUN_GEN_PROPORTION_TCELLS:
        print("Running: T cell and Macrophage proportion analysis...")
        gen_proportion_Tcells(**shared_kwargs)

    if config.RUN_GEN_CELL_TYPE_RATIO_SUMMARY_TABLE:
        print("Running: cell type ratio analysis...")
        gen_cell_type_ratio_summary_table(
            RATIOS_TO_CHECK=config.RATIOS_TO_CHECK,
            **shared_kwargs
        )

    if config.RUN_GEN_FRACTION_INTRA_SUMMARY_TABLE:
        print("Running: intratumoral fraction analysis...")
        gen_fraction_intra_summary_table(**shared_kwargs)

    if config.RUN_GEN_MEDIAN_DISTANCE_SUMMARY_TABLE:
        print("Running: median distance analysis...")
        gen_median_distance_summary_table(
            self_interactions=config.SELF_INTERACTIONS,
            um_per_px=config.UM_PER_PX,
            **shared_kwargs
        )

    if config.RUN_SCIMAP_NEIGHBORHOODS:
        print("Running: scimap spatial neighborhood analysis...")
        print("NOTE: This must complete before RUN_GEN_SCIMAP_INTERACTION_SUMMARY_TABLE.")
        run_neighborhoods(
            save_dir=config.RESULTS_DIR,
            matrix_path=config.MATRIX_RAW,
            metadata_path=config.METADATA_PATH,
            celltype_subset=config.CELLTYPE_SUBSET,
            immune_subset=config.IMMUNE_SUBSET,
            celltypes_rm=config.CELLTYPES_RM_SCIMAP,
            slides=config.SLIDES,
            slides_rm=config.SLIDES_RM,
            spatial_analysis_list=config.SPATIAL_ANALYSIS_LIST,
            spatial_method_list=config.SPATIAL_METHOD_LIST,
            n_knn_list=config.N_KNN_LIST,
            n_kmeans_list=config.N_KMEANS_LIST,
            n_radius_list=config.N_RADIUS_LIST,
            output_dir_scimap=config.OUTPUT_DIR_SCIMAP,
            omero_dict=config.OMERO_IMAGE_DICT,
            clinical_data=config.CLINICAL_DIR,
            clinical_vars_list=config.CLINICAL_VARS_LIST,
            t_cell_types=config.T_CELL_TYPES,
            cell_type_col_param=config.CELL_TYPE_COL_PARAM,
            sample_labels=config.SCIMAP_SAMPLE_LABELS,
            PD1_phenotypes=config.PD1_PHENOTYPES,
            run_gen_omero_tables=config.RUN_SCIMAP_GEN_OMERO_TABLES,
            run_gen_barplots=config.RUN_SCIMAP_GEN_BARPLOTS,
            run_gen_boxplots=config.RUN_SCIMAP_GEN_BOXPLOTS,
            run_gen_pieplots=config.RUN_SCIMAP_GEN_PIEPLOTS,
            run_correlation_plot=config.RUN_SCIMAP_CORRELATION_PLOT,
        )

    if config.RUN_GEN_SCIMAP_INTERACTION_SUMMARY_TABLE:
        print("Running: scimap spatial interaction analysis...")
        gen_scimap_interaction_summary_table(
            results_dir=config.RESULTS_DIR,
            metadata=metadata,
            cell_type_columns=config.CELL_TYPE_COLUMNS,
            artifact_cells=config.ARTIFACT_CELLS,
            clinical_vars_list=config.CLINICAL_VARS_LIST,
            scimap_data_path=config.SCIMAP_DATA_PATH,
            interaction_radius_px=config.INTERACTION_RADIUS_PX,
            interaction_radius_um=config.INTERACTION_RADIUS_UM,
            cell_types_keep=config.CELL_TYPES_KEEP,
            clinical_dir=config.CLINICAL_DIR,
            out_scimap_interaction_summary_table=config.OUT_SCIMAP_INTERACTION_SUMMARY_TABLE,
            run_gen_boxplots=config.RUN_GEN_BOXPLOTS,
            sample_label=config.SAMPLE_LABEL,
            add_color_points_stage=config.ADD_COLOR_POINTS_STAGE,
            clinical_df=clinical_df,
            title_font_size=config.TITLE_FONT_SIZE,
            subtitle_font_size=config.SUBTITLE_FONT_SIZE,
            y_tick_font_size=config.Y_TICK_FONT_SIZE,
            x_tick_font_size=config.X_TICK_FONT_SIZE,
            p_value_tick_font_size=config.P_VALUE_TICK_FONT_SIZE,
            x_tick_labels_dict=config.X_TICK_LABELS_DICT,
            add_plot_title=config.ADD_PLOT_TITLE,
            interaction_type=config.INTERACTION_TYPE,
            anchor_cell_type=config.ANCHOR_CELL_TYPE,
            interacting_cell_type=config.INTERACTING_CELL_TYPE,
            region=config.REGION,
            cell_types_rename=config.CELL_TYPES_RENAME,
            boxplot_shapes=config.BOXPLOT_SHAPES,
            cell_types_remove=config.CELL_TYPES_REMOVE,
            gen_summary_csv=config.GEN_SUMMARY_CSV,
            run_permutation_test=config.RUN_PERMUTATION_TEST,
        )

    if config.RUN_INTERACTIONS_PERMUTATION_TEST:
        print("Running: interaction permutation test...")
        interactions_permutation_test(
            results_dir=config.RESULTS_DIR,
            metadata=metadata,
            cell_type_columns=config.CELL_TYPE_COLUMNS,
            artifact_cells=config.ARTIFACT_CELLS,
            clinical_vars_list=config.CLINICAL_VARS_LIST,
            scimap_data_path=config.SCIMAP_DATA_PATH,
            interaction_radius_px=config.INTERACTION_RADIUS_PX,
            interaction_radius_um=config.INTERACTION_RADIUS_UM,
            cell_types_keep=config.CELL_TYPES_KEEP,
            clinical_dir=config.CLINICAL_DIR,
            out_scimap_interaction_summary_table=config.OUT_SCIMAP_INTERACTION_SUMMARY_TABLE,
            run_gen_boxplots=config.RUN_GEN_BOXPLOTS,
            sample_label=config.SAMPLE_LABEL,
            add_color_points_stage=config.ADD_COLOR_POINTS_STAGE,
            clinical_df=clinical_df,
            title_font_size=config.TITLE_FONT_SIZE,
            subtitle_font_size=config.SUBTITLE_FONT_SIZE,
            y_tick_font_size=config.Y_TICK_FONT_SIZE,
            x_tick_font_size=config.X_TICK_FONT_SIZE,
            p_value_tick_font_size=config.P_VALUE_TICK_FONT_SIZE,
            x_tick_labels_dict=config.X_TICK_LABELS_DICT,
            interaction_type=config.INTERACTION_TYPE,
            anchor_cell_type=config.ANCHOR_CELL_TYPE,
            interacting_cell_type=config.INTERACTING_CELL_TYPE,
            region=config.REGION,
            gen_interaction_summary_table=config.GEN_INTERACTION_SUMMARY_TABLE,
            gen_null_distribution=config.GEN_NULL_DISTRIBUTION,
            scimap_data_path_test=config.SCIMAP_DATA_PATH_TEST,
            out_scimap_interaction_summary_table_test=config.OUT_SCIMAP_INTERACTION_SUMMARY_TABLE_TEST,
            samples_skip=config.SAMPLES_SKIP,
            add_plot_title=config.ADD_PLOT_TITLE,
            boxplot_shapes=config.BOXPLOT_SHAPES,
            cell_types_remove=config.CELL_TYPES_REMOVE,
            gen_summary_csv=config.GEN_SUMMARY_CSV,
            run_permutation_test=config.RUN_PERMUTATION_TEST,
            cell_types_rename=config.CELL_TYPES_RENAME,
        )

    print("Done.")


if __name__ == "__main__":
    main()
