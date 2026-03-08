import os
import pandas as pd

from stats.tests import run_stats_tests
from visualization.boxplots import gen_boxplots
from analysis.proportions import gen_proportion_summary_table


def gen_fraction_intra_summary_table(metadata, results_dir, clinical_df, cell_type_columns,
                                     artifact_cells, clinical_vars_list, basic_cell_types,
                                     cell_types_remove, samples_skip, cell_types_rename,
                                     add_plot_title, boxplot_shapes, run_permutation_test,
                                     gen_summary_csv, run_gen_boxplots, sample_label,
                                     add_color_points_stage, title_font_size, subtitle_font_size,
                                     y_tick_font_size, x_tick_font_size, p_value_tick_font_size,
                                     x_tick_labels_dict, gen_new_marker_positivity_proportion):
    """
    Compute the fraction of each cell type found in the intratumoral region
    (count_intra / (count_intra + count_peri)) and test for clinical associations.
    """
    for cell_type_col in cell_type_columns:
        fraction_file = (
            f"{results_dir}/Summary_tables/fraction_intra/{cell_type_col}/"
            f"fraction_intra_per_sample_{cell_type_col}.csv"
        )

        if os.path.exists(fraction_file):
            results_df = pd.read_csv(fraction_file)
        else:
            if gen_new_marker_positivity_proportion:
                proportion_file = (
                    f"{results_dir}/Summary_tables/cell_type_proportions/{cell_type_col}/"
                    f"cell_type_proportion_per_sample_{cell_type_col}_prop_L_H.csv"
                )
            else:
                proportion_file = (
                    f"{results_dir}/Summary_tables/cell_type_proportions/{cell_type_col}/"
                    f"cell_type_proportion_per_sample_{cell_type_col}.csv"
                )

            if not os.path.exists(proportion_file):
                gen_proportion_summary_table(
                    metadata, results_dir, clinical_df, cell_type_columns, artifact_cells,
                    clinical_vars_list, basic_cell_types, cell_types_remove, samples_skip,
                    gen_summary_csv, run_gen_boxplots, sample_label, add_color_points_stage,
                    title_font_size, subtitle_font_size, y_tick_font_size, x_tick_font_size,
                    p_value_tick_font_size, x_tick_labels_dict, cell_types_rename,
                    add_plot_title, gen_new_marker_positivity_proportion, boxplot_shapes,
                    run_permutation_test
                )

            proportions_per_sample = pd.read_csv(proportion_file)
            results = []

            for (slide_id, cell_type), group_df in proportions_per_sample.groupby(["slide_id", cell_type_col]):
                if cell_type in cell_types_remove:
                    continue
                if 'intra' not in group_df['Region'].values or 'peri' not in group_df['Region'].values:
                    continue

                count_intra = group_df.loc[group_df['Region'] == 'intra', f'count_{cell_type_col}'].sum()
                count_peri = group_df.loc[group_df['Region'] == 'peri', f'count_{cell_type_col}'].sum()
                fraction_intra = count_intra / (count_intra + count_peri)

                results.append({
                    "slide_id": slide_id, "cell_type": cell_type,
                    "count_intra": count_intra, "count_peri": count_peri,
                    "fraction_intra": fraction_intra,
                })

            results_df = pd.DataFrame(results)
            os.makedirs(f"{results_dir}/Summary_tables/fraction_intra/{cell_type_col}", exist_ok=True)
            results_df.to_csv(fraction_file, index=False)

        results_clinical = results_df.merge(
            clinical_df[['slide_id'] + clinical_vars_list], on='slide_id', how='left'
        )
        results_clinical = results_clinical[~results_clinical['slide_id'].isin(samples_skip)]
        results_summarized = []

        for clinical_var in clinical_vars_list:
            results_clinical_subset = results_clinical[results_clinical[clinical_var].notna()].copy()
            results_clinical_subset[clinical_var] = results_clinical_subset[clinical_var].astype(int)

            for cell_type in results_clinical_subset['cell_type'].unique():
                results_cell_type = results_clinical_subset[results_clinical_subset['cell_type'] == cell_type]
                clinical_0 = results_cell_type[results_cell_type[clinical_var] == 0]['fraction_intra'].dropna().values
                clinical_1 = results_cell_type[results_cell_type[clinical_var] == 1]['fraction_intra'].dropna().values
                samples_0 = results_cell_type[results_cell_type[clinical_var] == 0]['slide_id'].values
                samples_1 = results_cell_type[results_cell_type[clinical_var] == 1]['slide_id'].values

                if len(clinical_0) < 2 or len(clinical_1) < 2:
                    continue

                if run_permutation_test:
                    pval_student_ttest, pval_welch_ttest, pval_mann_whitney, effect_size, pval_permutation_test, direction = run_stats_tests(clinical_0, clinical_1, clinical_var, run_permutation_test)
                else:
                    pval_student_ttest, pval_welch_ttest, pval_mann_whitney, effect_size, direction = run_stats_tests(clinical_0, clinical_1, clinical_var, run_permutation_test)

                result_dict = {
                    'cell_type': cell_type, 'clinical_var': clinical_var,
                    'direction': direction, 'student_ttest_pval': pval_student_ttest,
                    'welch_ttest_pval': pval_welch_ttest, 'mann_whitney_pval': pval_mann_whitney,
                    'effect_size': effect_size,
                }
                if run_permutation_test:
                    result_dict['pval_permutation_test'] = pval_permutation_test

                if run_gen_boxplots:
                    sig_dir = 'significant' if pval_mann_whitney < 0.052 else 'not_significant'
                    boxplot_output_dir = os.path.join(
                        results_dir, 'Summary_tables', 'fraction_intra',
                        cell_type_col, 'boxplots', clinical_var, sig_dir
                    )
                    y_axis_label_param = f'Fraction of {cell_type} in intratumoral region'
                    if cell_type in cell_types_rename:
                        y_axis_label_param = y_axis_label_param.replace(cell_type, cell_types_rename[cell_type])

                    gen_boxplots(
                        clinical_0, clinical_1, samples_0, samples_1, clinical_var,
                        "fraction_intra", 'whole_tissue', sample_label, pval_mann_whitney,
                        effect_size, boxplot_output_dir, add_color_points_stage,
                        clinical_df, cell_type, title_font_size, subtitle_font_size,
                        y_tick_font_size, x_tick_font_size, p_value_tick_font_size,
                        x_tick_labels_dict, y_axis_label_param, boxplot_shapes,
                        plot_title_param=None, sub_title_param=None,
                        add_plot_title=False, range_0_1=True
                    )

                results_summarized.append(result_dict)

        results_summarized_df = pd.DataFrame(results_summarized)
        os.makedirs(f"{results_dir}/Summary_tables/fraction_intra/{cell_type_col}", exist_ok=True)
        results_summarized_df.to_csv(
            f"{results_dir}/Summary_tables/fraction_intra/{cell_type_col}/"
            f"summarized_clinical_{cell_type_col}.csv", index=False
        )
