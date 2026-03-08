import os
import pandas as pd

from stats.tests import run_stats_tests
from visualization.boxplots import gen_boxplots
from analysis.proportions import gen_proportion_summary_table


def gen_cell_type_ratio_summary_table(metadata, results_dir, clinical_df, cell_type_columns,
                                      artifact_cells, clinical_vars_list, basic_cell_types,
                                      cell_types_remove, samples_skip, RATIOS_TO_CHECK,
                                      add_plot_title, boxplot_shapes,
                                      gen_summary_csv, run_gen_boxplots, sample_label,
                                      add_color_points_stage, title_font_size, subtitle_font_size,
                                      y_tick_font_size, x_tick_font_size, p_value_tick_font_size,
                                      x_tick_labels_dict, cell_types_rename,
                                      gen_new_marker_positivity_proportion):
    """
    Compute user-defined cell type ratios (e.g. CD8/CD4) per sample per region
    and test for association with clinical variables.
    """
    for cell_type_col in cell_type_columns:
        proportion_file = (
            f"{results_dir}/Summary_tables/cell_type_proportions/{cell_type_col}/"
            f"cell_type_proportion_per_sample_{cell_type_col}.csv"
        )
        if os.path.exists(proportion_file):
            metadata_summary = pd.read_csv(proportion_file)
        else:
            gen_proportion_summary_table(
                metadata, results_dir, clinical_df, cell_type_columns, artifact_cells,
                clinical_vars_list, basic_cell_types, cell_types_remove, samples_skip,
                gen_summary_csv, run_gen_boxplots, sample_label, add_color_points_stage,
                title_font_size, subtitle_font_size, y_tick_font_size, x_tick_font_size,
                p_value_tick_font_size, x_tick_labels_dict, cell_types_rename,
                add_plot_title, gen_new_marker_positivity_proportion, boxplot_shapes,
            )
            metadata_summary = pd.read_csv(proportion_file)

        results = []
        for (sample_id, region), metadata_sample_region in metadata_summary.groupby(["slide_id", "Region"]):
            for ratio in RATIOS_TO_CHECK:
                if ratio["use_pattern"]:
                    num_mask = metadata_sample_region[cell_type_col].str.contains(ratio["num"], regex=True)
                    den_mask = metadata_sample_region[cell_type_col].str.contains(ratio["den"], regex=True)
                else:
                    num_mask = metadata_sample_region[cell_type_col].isin(
                        ratio["num"] if isinstance(ratio["num"], list) else [ratio["num"]]
                    )
                    den_mask = metadata_sample_region[cell_type_col].isin(
                        ratio["den"] if isinstance(ratio["den"], list) else [ratio["den"]]
                    )

                numerator = metadata_sample_region.loc[num_mask, f"count_{cell_type_col}"].sum()
                denominator = metadata_sample_region.loc[den_mask, f"count_{cell_type_col}"].sum()
                value = numerator / denominator if denominator > 0 else None

                results.append({
                    "slide_id": sample_id, "Region": region, "ratio_name": ratio["name"],
                    "numerator": numerator, "denominator": denominator, "ratio_value": value,
                })

        results_df = pd.DataFrame(results)
        os.makedirs(f"{results_dir}/Summary_tables/cell_type_ratios/{cell_type_col}", exist_ok=True)
        results_df.to_csv(
            f"{results_dir}/Summary_tables/cell_type_ratios/{cell_type_col}/ratio_per_sample_{cell_type_col}.csv",
            index=False
        )

        results_clinical = results_df.merge(
            clinical_df[['slide_id'] + clinical_vars_list], on='slide_id', how='left'
        )
        results_clinical = results_clinical[~results_clinical['slide_id'].isin(samples_skip)]

        summarized_df = pd.DataFrame()
        for clinical_var in clinical_vars_list:
            results_clinical_subset = results_clinical[results_clinical[clinical_var].notna()].copy()
            results_clinical_subset[clinical_var] = results_clinical_subset[clinical_var].astype(int)

            for region in results_clinical_subset['Region'].unique():
                results_region = results_clinical_subset[results_clinical_subset['Region'] == region]

                for ratio in RATIOS_TO_CHECK:
                    df_summary = pd.DataFrame([{
                        'region': region, 'ratio_name': ratio["name"], 'clinical_var': clinical_var
                    }])

                    results_ratio = results_region[results_region['ratio_name'] == ratio["name"]]
                    clinical_0 = results_ratio[results_ratio[clinical_var] == 0]['ratio_value'].dropna().values
                    clinical_1 = results_ratio[results_ratio[clinical_var] == 1]['ratio_value'].dropna().values
                    samples_0 = results_ratio[results_ratio[clinical_var] == 0]['slide_id'].values
                    samples_1 = results_ratio[results_ratio[clinical_var] == 1]['slide_id'].values

                    pval_student_ttest, pval_welch_ttest, pval_mann_whitney, effect_size, direction = run_stats_tests(clinical_0, clinical_1, clinical_var)

                    df_summary.loc[0, 'direction'] = direction
                    df_summary.loc[0, 'student_ttest_pval'] = pval_student_ttest
                    df_summary.loc[0, 'welch_ttest_pval'] = pval_welch_ttest
                    df_summary.loc[0, 'mann_whitney_pval'] = pval_mann_whitney
                    df_summary.loc[0, 'effect_size'] = effect_size

                    if run_gen_boxplots:
                        sig_dir = 'significant' if pval_mann_whitney < 0.052 else 'not_significant'
                        boxplot_output_dir = (
                            f'{results_dir}/Summary_tables/cell_type_ratios/{cell_type_col}/'
                            f'boxplots/{clinical_var}/{region}/{sig_dir}'
                        )
                        region_label = f'{region.capitalize()}tumoral' if region in ['intra', 'peri'] else region.capitalize()
                        y_axis_label_param = f'{region_label} {ratio["name"]}'

                        gen_boxplots(
                            clinical_0, clinical_1, samples_0, samples_1, clinical_var,
                            ratio["name"], region, sample_label, pval_mann_whitney,
                            effect_size, boxplot_output_dir, add_color_points_stage,
                            clinical_df, ratio["name"].replace("/", "_"), title_font_size,
                            subtitle_font_size, y_tick_font_size, x_tick_font_size,
                            p_value_tick_font_size, x_tick_labels_dict, y_axis_label_param,
                            boxplot_shapes, plot_title_param=None, sub_title_param=None,
                            add_plot_title=False, range_0_1=True
                        )

                    summarized_df = pd.concat([summarized_df, df_summary])

        summarized_df.to_csv(
            f"{results_dir}/Summary_tables/cell_type_ratios/{cell_type_col}/"
            f"summarized_clinical_{cell_type_col}_ratios.csv", index=False
        )
