import os
import re
import numpy as np
import pandas as pd

from stats.tests import run_stats_tests
from visualization.boxplots import gen_boxplots


def gen_proportion_summary_table(metadata, results_dir, clinical_df, cell_type_columns,
                                  artifact_cells, clinical_vars_list, basic_cell_types,
                                  cell_types_remove, samples_skip, gen_summary_csv,
                                  run_gen_boxplots, sample_label, add_color_points_stage,
                                  title_font_size, subtitle_font_size, y_tick_font_size,
                                  x_tick_font_size, p_value_tick_font_size, x_tick_labels_dict,
                                  cell_types_rename, add_plot_title,
                                  gen_new_marker_positivity_proportion, boxplot_shapes,
                                  ):
    """
    Compute per-sample cell type proportions and run statistical comparisons
    against clinical variables.

    Proportions are calculated three ways:
      - proportion_total_cell_count: fraction of all cells in region
      - proportion_total_T_cells: fraction of all T cells (T cell subtypes only)
      - proportion_total_basic_cell_count: fraction of parent cell type
        (e.g. PD1+ CD8+ T cells / all CD8+ T cells)

    Results are saved as CSVs and optionally as boxplots.
    """
    for cell_type_col in cell_type_columns:
        metadata_summary = pd.DataFrame()

        if gen_new_marker_positivity_proportion:
            cell_type_proportion_per_sample_file = (
                f"{results_dir}/Summary_tables/cell_type_proportions/{cell_type_col}/"
                f"cell_type_proportion_per_sample_{cell_type_col}_prop_L_H.csv"
            )
        else:
            cell_type_proportion_per_sample_file = (
                f"{results_dir}/Summary_tables/cell_type_proportions/{cell_type_col}/"
                f"cell_type_proportion_per_sample_{cell_type_col}.csv"
            )

        if os.path.exists(cell_type_proportion_per_sample_file):
            metadata_summary = pd.read_csv(cell_type_proportion_per_sample_file)
        else:
            metadata_cols = ['slide_id', 'peri_intra_tumoral']
            metadata_subset = metadata[metadata_cols + [cell_type_col]].copy()

            pattern_artifact_cells = '|'.join(map(re.escape, artifact_cells))
            metadata_subset = metadata_subset[
                ~metadata_subset[cell_type_col].str.contains(
                    pattern_artifact_cells, case=False, na=False, regex=True
                )
            ]

            total_cell_counts_intra_peri = (
                metadata_subset.groupby(['slide_id', 'peri_intra_tumoral', cell_type_col])
                .size().reset_index(name=f'count_{cell_type_col}')
            )
            total_cell_counts_whole_tissue = (
                metadata_subset.groupby(['slide_id', cell_type_col])
                .size().reset_index(name=f'count_{cell_type_col}')
            )

            # Fill missing sample/cell_type/region combinations with 0
            for sample in metadata_subset['slide_id'].unique():
                for cell_type in metadata_subset[cell_type_col].unique():
                    for region in ['intra', 'peri', 'whole_tissue']:
                        if region in ['intra', 'peri']:
                            exists = sample in total_cell_counts_intra_peri.loc[
                                (total_cell_counts_intra_peri['peri_intra_tumoral'] == region) &
                                (total_cell_counts_intra_peri[cell_type_col] == cell_type)
                            ]['slide_id'].unique()
                            if not exists:
                                new_row = pd.DataFrame([{
                                    'slide_id': sample,
                                    'peri_intra_tumoral': region,
                                    cell_type_col: cell_type,
                                    f'count_{cell_type_col}': 0
                                }])
                                total_cell_counts_intra_peri = pd.concat(
                                    [total_cell_counts_intra_peri, new_row], ignore_index=True
                                )
                        else:
                            exists = sample in total_cell_counts_whole_tissue.loc[
                                total_cell_counts_whole_tissue[cell_type_col] == cell_type
                            ]['slide_id'].unique()
                            if not exists:
                                new_row = pd.DataFrame([{
                                    'slide_id': sample,
                                    cell_type_col: cell_type,
                                    f'count_{cell_type_col}': 0
                                }])
                                total_cell_counts_whole_tissue = pd.concat(
                                    [total_cell_counts_whole_tissue, new_row], ignore_index=True
                                )

            total_cell_counts_intra_peri.rename(columns={'peri_intra_tumoral': 'Region'}, inplace=True)
            total_cell_counts_whole_tissue['Region'] = 'whole_tissue'
            metadata_summary = pd.concat([total_cell_counts_intra_peri, total_cell_counts_whole_tissue])

            total_tcells_per_region = (
                metadata_summary[
                    metadata_summary[f'{cell_type_col}'].str.contains("T cells", case=False, na=False)
                ]
                .groupby(['slide_id', 'Region'], as_index=False)[f'count_{cell_type_col}']
                .sum()
                .rename(columns={f'count_{cell_type_col}': 'total_T_cells'})
            )
            metadata_summary = metadata_summary.merge(total_tcells_per_region, on=['slide_id', 'Region'], how='left')

            total_counts_region = (
                metadata_summary.groupby(['slide_id', 'Region'])
                .agg(total_cell_count=(f'count_{cell_type_col}', 'sum'))
            )
            metadata_summary = metadata_summary.merge(total_counts_region, on=['slide_id', 'Region'], how='left')

            pattern_basic_cell_types = '|'.join(map(re.escape, basic_cell_types))
            metadata_summary['basic_cell_type'] = metadata_summary[f'{cell_type_col}'].str.extract(
                f'({pattern_basic_cell_types})', expand=False
            )
            mixed_mask = metadata_summary[f'{cell_type_col}'].str.contains(r'\band\b', case=False, na=False)
            metadata_summary.loc[mixed_mask, 'basic_cell_type'] = metadata_summary.loc[mixed_mask, f'{cell_type_col}']

            if gen_new_marker_positivity_proportion:
                marker_positivity_mask = metadata_summary[f'{cell_type_col}'].str.endswith(('_L', '_H'), na=False)
                metadata_summary.loc[marker_positivity_mask, 'basic_cell_type'] = (
                    metadata_summary.loc[marker_positivity_mask, f'{cell_type_col}']
                    .str.replace(r'_(L|H)$', '', regex=True)
                )

            total_cell_counts_basic_cell_type_region = (
                metadata_summary.groupby(['slide_id', 'Region', 'basic_cell_type'], as_index=False)
                [f'count_{cell_type_col}'].sum()
                .rename(columns={f'count_{cell_type_col}': 'total_basic_cell_count'})
            )
            metadata_summary = metadata_summary.merge(
                total_cell_counts_basic_cell_type_region, on=['slide_id', 'Region', 'basic_cell_type'], how='left'
            )

            metadata_summary['proportion_total_cell_count'] = (
                metadata_summary[f'count_{cell_type_col}'] / metadata_summary['total_cell_count']
            )
            metadata_summary['proportion_total_T_cells'] = (
                metadata_summary[
                    metadata_summary[f'{cell_type_col}'].str.contains("T cells", case=False, na=False)
                ][f'count_{cell_type_col}'] / metadata_summary['total_T_cells']
            )
            metadata_summary['proportion_total_basic_cell_count'] = (
                metadata_summary[f'count_{cell_type_col}'] / metadata_summary['total_basic_cell_count']
            )

            metadata_summary = metadata_summary.merge(
                clinical_df[['slide_id'] + clinical_vars_list], on=['slide_id'], how='left'
            )
            metadata_summary = metadata_summary.round(4)

            os.makedirs(f"{results_dir}/Summary_tables/cell_type_proportions/{cell_type_col}", exist_ok=True)
            metadata_summary.to_csv(cell_type_proportion_per_sample_file, index=False)

        proportion_types = [
            'proportion_total_cell_count',
            'proportion_total_T_cells',
            'proportion_total_basic_cell_count'
        ]
        summary_table_all = pd.DataFrame()
        metadata_summary = metadata_summary[~metadata_summary['slide_id'].isin(samples_skip)]

        for clinical_var in clinical_vars_list:
            if clinical_var not in metadata_summary.columns:
                metadata_summary = metadata_summary.merge(
                    clinical_df[['slide_id', clinical_var]], on=['slide_id'], how='left'
                )
            metadata_summary_clinical = metadata_summary[metadata_summary[clinical_var].notna()]

            for region in metadata_summary_clinical['Region'].unique():
                metadata_summary_clinical_region = metadata_summary_clinical[
                    metadata_summary_clinical['Region'] == region
                ]

                for cell_type in metadata_summary_clinical[f'{cell_type_col}'].unique():
                    if cell_type in cell_types_remove:
                        continue

                    metadata_summary_clinical_cell_type_region = metadata_summary_clinical_region[
                        metadata_summary_clinical_region[f'{cell_type_col}'] == cell_type
                    ]
                    results_dict = {
                        'cell_type': str(cell_type),
                        'region': str(region),
                        'clinical_var': str(clinical_var)
                    }

                    for proportion_type in proportion_types:
                        if proportion_type not in metadata_summary_clinical_cell_type_region.columns:
                            continue

                        if proportion_type == 'proportion_total_T_cells':
                            metadata_subset_cell_type_region = metadata_summary_clinical_cell_type_region[
                                metadata_summary_clinical_cell_type_region[f'{cell_type_col}']
                                .str.contains("T cells", case=False, na=False)
                            ]
                        else:
                            metadata_subset_cell_type_region = metadata_summary_clinical_cell_type_region

                        clinical_0 = metadata_subset_cell_type_region[
                            metadata_subset_cell_type_region[clinical_var] == 0
                        ][proportion_type].values
                        clinical_1 = metadata_subset_cell_type_region[
                            metadata_subset_cell_type_region[clinical_var] == 1
                        ][proportion_type].values
                        samples_0 = metadata_subset_cell_type_region[
                            metadata_subset_cell_type_region[clinical_var] == 0
                        ]['slide_id'].unique()
                        samples_1 = metadata_subset_cell_type_region[
                            metadata_subset_cell_type_region[clinical_var] == 1
                        ]['slide_id'].unique()

                        if len(clinical_0) < 2 or len(clinical_1) < 2:
                            continue

                        pval_student_ttest, pval_welch_ttest, pval_mann_whitney, effect_size, direction = run_stats_tests(clinical_0, clinical_1, clinical_var)

                        if run_gen_boxplots:
                            base_dir = os.path.join(
                                results_dir, 'Summary_tables', 'cell_type_proportions',
                                cell_type_col, 'box_plots', clinical_var
                            )
                            if gen_new_marker_positivity_proportion:
                                base_dir = os.path.join(base_dir, 'prop_L_H')

                            figure_name = f'{cell_type}_{region}_{proportion_type}'
                            region_label = 'whole tissue' if region == 'whole_tissue' else f'{region}tumoral'
                            y_axis_label_param = f'Proportion of {region_label} {cell_type}'
                            if cell_type in cell_types_rename:
                                y_axis_label_param = y_axis_label_param.replace(cell_type, cell_types_rename[cell_type])

                            sig_dir = 'significant' if pval_mann_whitney < 0.052 else 'not_significant'
                            boxplot_output_dir = os.path.join(base_dir, sig_dir)

                            gen_boxplots(
                                clinical_0, clinical_1, samples_0, samples_1, clinical_var,
                                proportion_type, region, sample_label, pval_mann_whitney,
                                effect_size, boxplot_output_dir, add_color_points_stage,
                                clinical_df, figure_name, title_font_size, subtitle_font_size,
                                y_tick_font_size, x_tick_font_size, p_value_tick_font_size,
                                x_tick_labels_dict, y_axis_label_param, boxplot_shapes,
                                plot_title_param=None, sub_title_param=None,
                                add_plot_title=False, range_0_1=True
                            )

                        results_dict.update({
                            f'students_ttest_pval_{proportion_type}': float(pval_student_ttest) if pval_student_ttest is not None and not pd.isna(pval_student_ttest) else None,
                            f'welch_ttest_pval_{proportion_type}': float(pval_welch_ttest) if pval_welch_ttest is not None and not pd.isna(pval_welch_ttest) else None,
                            f'mann_whitney_pval_{proportion_type}': float(pval_mann_whitney) if pval_mann_whitney is not None and not pd.isna(pval_mann_whitney) else None,
                            f'effect_size_{proportion_type}': float(effect_size) if effect_size is not None and not pd.isna(effect_size) else None,
                            f'direction_{proportion_type}': direction
                        })

                    summary_table_all = pd.concat(
                        [summary_table_all, pd.DataFrame([results_dict])], ignore_index=True
                    )

        summary_table_all = summary_table_all.round(4)
        os.makedirs(f"{results_dir}/Summary_tables/cell_type_proportions/{cell_type_col}", exist_ok=True)
        if gen_summary_csv:
            summary_table_all.to_csv(
                f"{results_dir}/Summary_tables/cell_type_proportions/{cell_type_col}/"
                f"summarized_clinical_results_{cell_type_col}.csv", index=False
            )


def gen_proportion_Tcells(metadata, results_dir, clinical_df, cell_type_columns,
                          artifact_cells, clinical_vars_list, basic_cell_types,
                          cell_types_remove, samples_skip, gen_summary_csv,
                          run_gen_boxplots, sample_label, add_color_points_stage,
                          title_font_size, subtitle_font_size, y_tick_font_size,
                          x_tick_font_size, p_value_tick_font_size, x_tick_labels_dict,
                          cell_types_rename, add_plot_title,
                          gen_new_marker_positivity_proportion, boxplot_shapes,
                          ):
    """
    Compute per-sample proportions of T cells and Macrophages out of all cells,
    per region, and run statistical comparisons against clinical variables.
    """
    for cell_type_col in cell_type_columns:
        metadata_summary = pd.DataFrame()

        if gen_new_marker_positivity_proportion:
            cell_type_proportion_per_sample_file = (
                f"{results_dir}/Summary_tables/cell_type_proportions_Tcells_Macrophages/{cell_type_col}/"
                f"cell_type_proportion_per_sample_{cell_type_col}_prop_L_H.csv"
            )
        else:
            cell_type_proportion_per_sample_file = (
                f"{results_dir}/Summary_tables/cell_type_proportions_Tcells_Macrophages/{cell_type_col}/"
                f"cell_type_proportion_per_sample_{cell_type_col}.csv"
            )

        if os.path.exists(cell_type_proportion_per_sample_file):
            metadata_summary = pd.read_csv(cell_type_proportion_per_sample_file)
        else:
            metadata_cols = ['slide_id', 'peri_intra_tumoral']
            metadata_subset = metadata[metadata_cols + [cell_type_col]].copy()

            pattern_artifact_cells = '|'.join(map(re.escape, artifact_cells))
            metadata_subset = metadata_subset[
                ~metadata_subset[cell_type_col].str.contains(
                    pattern_artifact_cells, case=False, na=False, regex=True
                )
            ]

            total_cell_counts_intra_peri = (
                metadata_subset.groupby(['slide_id', 'peri_intra_tumoral', cell_type_col])
                .size().reset_index(name=f'count_{cell_type_col}')
            )
            total_cell_counts_whole_tissue = (
                metadata_subset.groupby(['slide_id', cell_type_col])
                .size().reset_index(name=f'count_{cell_type_col}')
            )

            for sample in metadata_subset['slide_id'].unique():
                for cell_type in metadata_subset[cell_type_col].unique():
                    for region in ['intra', 'peri', 'whole_tissue']:
                        if region in ['intra', 'peri']:
                            exists = sample in total_cell_counts_intra_peri.loc[
                                (total_cell_counts_intra_peri['peri_intra_tumoral'] == region) &
                                (total_cell_counts_intra_peri[cell_type_col] == cell_type)
                            ]['slide_id'].unique()
                            if not exists:
                                new_row = pd.DataFrame([{
                                    'slide_id': sample, 'peri_intra_tumoral': region,
                                    cell_type_col: cell_type, f'count_{cell_type_col}': 0
                                }])
                                total_cell_counts_intra_peri = pd.concat(
                                    [total_cell_counts_intra_peri, new_row], ignore_index=True
                                )
                        else:
                            exists = sample in total_cell_counts_whole_tissue.loc[
                                total_cell_counts_whole_tissue[cell_type_col] == cell_type
                            ]['slide_id'].unique()
                            if not exists:
                                new_row = pd.DataFrame([{
                                    'slide_id': sample, cell_type_col: cell_type,
                                    f'count_{cell_type_col}': 0
                                }])
                                total_cell_counts_whole_tissue = pd.concat(
                                    [total_cell_counts_whole_tissue, new_row], ignore_index=True
                                )

            total_cell_counts_intra_peri.rename(columns={'peri_intra_tumoral': 'Region'}, inplace=True)
            total_cell_counts_whole_tissue['Region'] = 'whole_tissue'
            metadata_summary = pd.concat([total_cell_counts_intra_peri, total_cell_counts_whole_tissue])

            total_tcells_per_region = (
                metadata_summary[
                    metadata_summary[f'{cell_type_col}'].str.contains("T cells", case=False, na=False)
                ]
                .groupby(['slide_id', 'Region'], as_index=False)[f'count_{cell_type_col}']
                .sum().rename(columns={f'count_{cell_type_col}': 'total_T_cells'})
            )
            total_macrophages_per_region = (
                metadata_summary[
                    metadata_summary[f'{cell_type_col}'].str.contains("Macrophages", case=False, na=False)
                ]
                .groupby(['slide_id', 'Region'], as_index=False)[f'count_{cell_type_col}']
                .sum().rename(columns={f'count_{cell_type_col}': 'total_Macrophages'})
            )

            metadata_summary = metadata_summary.merge(total_tcells_per_region, on=['slide_id', 'Region'], how='left')
            metadata_summary = metadata_summary.merge(total_macrophages_per_region, on=['slide_id', 'Region'], how='left')

            total_counts_region = (
                metadata_summary.groupby(['slide_id', 'Region'])
                .agg(total_cell_count=(f'count_{cell_type_col}', 'sum'))
            )
            metadata_summary = metadata_summary.merge(total_counts_region, on=['slide_id', 'Region'], how='left')

            metadata_summary['proportion_total_T_cells'] = (
                metadata_summary['total_T_cells'] / metadata_summary['total_cell_count']
            )
            metadata_summary['proportion_total_Macrophages'] = (
                metadata_summary['total_Macrophages'] / metadata_summary['total_cell_count']
            )

            metadata_summary = metadata_summary[
                ['slide_id', 'Region', 'proportion_total_T_cells', 'proportion_total_Macrophages']
            ].drop_duplicates()

            metadata_summary = metadata_summary.merge(
                clinical_df[['slide_id'] + clinical_vars_list], on=['slide_id'], how='left'
            )
            metadata_summary = metadata_summary.round(4)

            os.makedirs(
                f"{results_dir}/Summary_tables/cell_type_proportions_Tcells_Macrophages/{cell_type_col}",
                exist_ok=True
            )
            metadata_summary.to_csv(cell_type_proportion_per_sample_file, index=False)

        proportion_types = ['proportion_total_T_cells', 'proportion_total_Macrophages']
        summary_table_all = pd.DataFrame()
        metadata_summary = metadata_summary[~metadata_summary['slide_id'].isin(samples_skip)]

        for clinical_var in clinical_vars_list:
            if clinical_var not in metadata_summary.columns:
                metadata_summary = metadata_summary.merge(
                    clinical_df[['slide_id', clinical_var]], on=['slide_id'], how='left'
                )
            metadata_summary_clinical = metadata_summary[metadata_summary[clinical_var].notna()]

            for region in metadata_summary_clinical['Region'].unique():
                metadata_summary_clinical_region = metadata_summary_clinical[
                    metadata_summary_clinical['Region'] == region
                ]
                results_dict = {'region': str(region), 'clinical_var': str(clinical_var)}

                for proportion_type in proportion_types:
                    if proportion_type not in metadata_summary_clinical_region.columns:
                        continue

                    clinical_0 = metadata_summary_clinical_region[
                        metadata_summary_clinical_region[clinical_var] == 0
                    ][proportion_type].values
                    clinical_1 = metadata_summary_clinical_region[
                        metadata_summary_clinical_region[clinical_var] == 1
                    ][proportion_type].values
                    samples_0 = metadata_summary_clinical_region[
                        metadata_summary_clinical_region[clinical_var] == 0
                    ]['slide_id'].unique()
                    samples_1 = metadata_summary_clinical_region[
                        metadata_summary_clinical_region[clinical_var] == 1
                    ]['slide_id'].unique()

                    if len(clinical_0) < 2 or len(clinical_1) < 2:
                        continue

                    pval_student_ttest, pval_welch_ttest, pval_mann_whitney, effect_size, direction = run_stats_tests(clinical_0, clinical_1, clinical_var)

                    print(f'{proportion_type} {region} {clinical_var} {pval_mann_whitney} {effect_size}')

                    if run_gen_boxplots:
                        base_dir = os.path.join(
                            results_dir, 'Summary_tables', 'cell_type_proportions_Tcells_Macrophages',
                            cell_type_col, 'box_plots', clinical_var
                        )
                        if gen_new_marker_positivity_proportion:
                            base_dir = os.path.join(base_dir, 'prop_L_H')

                        figure_name = f'{region}_{proportion_type}'
                        y_axis_label_param = (
                            'Proportion of T cells' if proportion_type == 'proportion_total_T_cells'
                            else 'Proportion of Macrophages'
                        )
                        region_label = 'whole tissue' if region == 'whole_tissue' else f'{region}tumoral'
                        y_axis_label_param = f'{y_axis_label_param} in {region_label}'

                        sig_dir = 'significant' if pval_mann_whitney < 0.052 else 'not_significant'
                        gen_boxplots(
                            clinical_0, clinical_1, samples_0, samples_1, clinical_var,
                            proportion_type, region, sample_label, pval_mann_whitney,
                            effect_size, os.path.join(base_dir, sig_dir), add_color_points_stage,
                            clinical_df, figure_name, title_font_size, subtitle_font_size,
                            y_tick_font_size, x_tick_font_size, p_value_tick_font_size,
                            x_tick_labels_dict, y_axis_label_param, boxplot_shapes,
                            plot_title_param=None, sub_title_param=None,
                            add_plot_title=False, range_0_1=True
                        )

                    results_dict.update({
                        f'students_ttest_pval_{proportion_type}': float(pval_student_ttest) if pval_student_ttest is not None and not pd.isna(pval_student_ttest) else None,
                        f'welch_ttest_pval_{proportion_type}': float(pval_welch_ttest) if pval_welch_ttest is not None and not pd.isna(pval_welch_ttest) else None,
                        f'mann_whitney_pval_{proportion_type}': float(pval_mann_whitney) if pval_mann_whitney is not None and not pd.isna(pval_mann_whitney) else None,
                        f'effect_size_{proportion_type}': float(effect_size) if effect_size is not None and not pd.isna(effect_size) else None,
                        f'direction_{proportion_type}': direction
                    })

                summary_table_all = pd.concat(
                    [summary_table_all, pd.DataFrame([results_dict])], ignore_index=True
                )

        summary_table_all = summary_table_all.round(4)
        os.makedirs(
            f"{results_dir}/Summary_tables/cell_type_proportions_Tcells_Macrophages/{cell_type_col}",
            exist_ok=True
        )
        if gen_summary_csv:
            summary_table_all.to_csv(
                f"{results_dir}/Summary_tables/cell_type_proportions_Tcells_Macrophages/{cell_type_col}/"
                f"summarized_clinical_results_{cell_type_col}.csv", index=False
            )
