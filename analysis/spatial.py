import os
import re
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree

from utils.io import load_scimap_data
from stats.tests import run_stats_tests
from visualization.boxplots import gen_boxplots


def gen_median_distance_summary_table(metadata, results_dir, clinical_df, cell_type_columns,
                                      artifact_cells, clinical_vars_list, basic_cell_types,
                                      cell_types_remove, samples_skip, self_interactions,
                                      add_plot_title, cell_types_rename, boxplot_shapes,
                                      um_per_px, run_permutation_test, run_gen_boxplots,
                                      sample_label, add_color_points_stage, title_font_size,
                                      subtitle_font_size, y_tick_font_size, x_tick_font_size,
                                      p_value_tick_font_size, x_tick_labels_dict):
    """
    Compute the median nearest-neighbor distance (in micrometers) between all
    pairs of cell types per sample per region, and test for clinical associations.

    For self-interactions, the second nearest neighbor is used to avoid
    distance-to-self = 0.
    """
    for cell_type_col in cell_type_columns:
        distance_file = (
            f"{results_dir}/Summary_tables/median_distance/{cell_type_col}/"
            f"median_distance_per_sample_{cell_type_col}.csv"
        )

        if os.path.exists(distance_file):
            results_df = pd.read_csv(distance_file)
        else:
            results = []
            for sample_id, metadata_sample in metadata.groupby("slide_id"):
                if sample_id in samples_skip:
                    continue

                for region in ['intra', 'peri', 'whole_tissue']:
                    region_df = metadata_sample if region == 'whole_tissue' else metadata_sample[
                        metadata_sample['peri_intra_tumoral'] == region
                    ]

                    coords_per_type = {
                        cell_type: region_df.loc[
                            region_df[cell_type_col] == cell_type,
                            ['centroid_x_slide', 'centroid_y_slide']
                        ].values
                        for cell_type in region_df[cell_type_col].unique()
                    }

                    for cell_type_anchor, anchor_coords in coords_per_type.items():
                        for cell_type_target, target_coords in coords_per_type.items():
                            if cell_type_anchor in cell_types_remove or cell_type_target in cell_types_remove:
                                continue
                            if cell_type_anchor in artifact_cells or cell_type_target in artifact_cells:
                                continue
                            if not self_interactions and cell_type_anchor == cell_type_target:
                                continue

                            if len(anchor_coords) == 0 or len(target_coords) == 0:
                                median_distance = np.nan
                            else:
                                target_tree = cKDTree(target_coords)
                                if cell_type_anchor == cell_type_target:
                                    distances, _ = target_tree.query(anchor_coords, k=2)
                                    distances = distances[:, 1]
                                else:
                                    distances, _ = target_tree.query(anchor_coords, k=1)
                                median_distance = np.median(distances) if len(distances) > 0 else np.nan

                            results.append({
                                "slide_id": sample_id, "region": region,
                                "cell_type_anchor": cell_type_anchor,
                                "cell_type_target": cell_type_target,
                                "median_distance": median_distance
                            })

            results_df = pd.DataFrame(results)
            os.makedirs(f"{results_dir}/Summary_tables/median_distance/{cell_type_col}", exist_ok=True)
            results_df.to_csv(distance_file, index=False)

        results_clinical_df = results_df.merge(
            clinical_df[['slide_id'] + clinical_vars_list], on='slide_id', how='left'
        )
        results_summarized = []

        for clinical_var in clinical_vars_list:
            results_clinical_subset = results_clinical_df[results_clinical_df[clinical_var].notna()].copy()
            results_clinical_subset[clinical_var] = results_clinical_subset[clinical_var].astype(int)

            for region in results_clinical_subset['region'].unique():
                region_subset = results_clinical_subset[results_clinical_subset['region'] == region]

                for cell_type_anchor in region_subset['cell_type_anchor'].unique():
                    anchor_subset = region_subset[region_subset['cell_type_anchor'] == cell_type_anchor]

                    for cell_type_target in anchor_subset['cell_type_target'].unique():
                        pair_subset = anchor_subset[anchor_subset['cell_type_target'] == cell_type_target]

                        clinical_0 = pair_subset[pair_subset[clinical_var] == 0]['median_distance'].dropna().values * um_per_px
                        clinical_1 = pair_subset[pair_subset[clinical_var] == 1]['median_distance'].dropna().values * um_per_px
                        samples_0 = pair_subset[pair_subset[clinical_var] == 0]['slide_id'].values
                        samples_1 = pair_subset[pair_subset[clinical_var] == 1]['slide_id'].values

                        if len(clinical_0) < 2 or len(clinical_1) < 2:
                            continue

                        if run_permutation_test:
                            pval_student_ttest, pval_welch_ttest, pval_mann_whitney, effect_size, pval_permutation_test, direction = run_stats_tests(clinical_0, clinical_1, clinical_var, run_permutation_test)
                        else:
                            pval_student_ttest, pval_welch_ttest, pval_mann_whitney, effect_size, direction = run_stats_tests(clinical_0, clinical_1, clinical_var, run_permutation_test)

                        result_dict = {
                            'region': region, 'cell_type_anchor': cell_type_anchor,
                            'cell_type_target': cell_type_target, 'clinical_var': clinical_var,
                            'direction': direction, 'student_ttest_pval': pval_student_ttest,
                            'welch_ttest_pval': pval_welch_ttest, 'mann_whitney_pval': pval_mann_whitney,
                            'effect_size': effect_size,
                        }
                        if run_permutation_test:
                            result_dict['pval_permutation_test'] = pval_permutation_test

                        if run_gen_boxplots:
                            sig_dir = 'significant' if pval_mann_whitney < 0.052 else 'not_significant'
                            boxplot_output_dir = os.path.join(
                                results_dir, 'Summary_tables', 'median_distance',
                                cell_type_col, 'boxplots', clinical_var, region, sig_dir
                            )
                            y_axis_label_param = f'Median distance between {cell_type_anchor} and {cell_type_target} (µm)'
                            if cell_type_anchor in cell_types_rename:
                                y_axis_label_param = y_axis_label_param.replace(cell_type_anchor, cell_types_rename[cell_type_anchor])
                            if cell_type_target in cell_types_rename:
                                y_axis_label_param = y_axis_label_param.replace(cell_type_target, cell_types_rename[cell_type_target])

                            gen_boxplots(
                                clinical_0, clinical_1, samples_0, samples_1, clinical_var,
                                'median_distance', region, sample_label, pval_mann_whitney,
                                effect_size, boxplot_output_dir, add_color_points_stage,
                                clinical_df, f'Median_Distance_{cell_type_anchor}_{cell_type_target}_{region}',
                                title_font_size, subtitle_font_size, y_tick_font_size, x_tick_font_size,
                                p_value_tick_font_size, x_tick_labels_dict, y_axis_label_param,
                                boxplot_shapes, plot_title_param=None, sub_title_param=None,
                                add_plot_title=False, range_0_1=False
                            )

                        results_summarized.append(result_dict)

        results_summarized_df = pd.DataFrame(results_summarized)
        os.makedirs(f"{results_dir}/Summary_tables/median_distance/{cell_type_col}", exist_ok=True)
        results_summarized_df.to_csv(
            f"{results_dir}/Summary_tables/median_distance/{cell_type_col}/"
            f"summarized_clinical_{cell_type_col}.csv", index=False
        )


def gen_scimap_interaction_summary_table(results_dir, metadata, cell_type_columns,
                                         artifact_cells, clinical_vars_list, scimap_data_path,
                                         interaction_radius_px, interaction_radius_um,
                                         cell_types_keep, clinical_dir, out_scimap_interaction_summary_table,
                                         run_gen_boxplots, sample_label, add_color_points_stage,
                                         clinical_df, title_font_size, subtitle_font_size,
                                         y_tick_font_size, x_tick_font_size, p_value_tick_font_size,
                                         x_tick_labels_dict, add_plot_title, interaction_type,
                                         anchor_cell_type, interacting_cell_type, region,
                                         cell_types_rename, boxplot_shapes, cell_types_remove,
                                         gen_summary_csv, run_permutation_test):
    """
    Compute cell-cell spatial interaction metrics from scimap neighborhood analysis output
    and test for association with clinical variables.

    Two interaction metrics are computed per anchor/target cell type pair per region:
      - mean_proportion_interacting_cell_type: mean fraction of target cells among
        all neighbors of each anchor cell
      - proportion_of_anchor_cells_interacting: fraction of anchor cells with at
        least one neighboring target cell
    """
    output_file = (
        f'{results_dir}/{out_scimap_interaction_summary_table}/'
        f'interaction_proportion_counts_df_{interaction_radius_px}px.csv'
    )

    if os.path.exists(output_file):
        interaction_proportion_counts_df_clinical = pd.read_csv(output_file)
    else:
        metadata_prop = load_scimap_data(results_dir, scimap_data_path, interaction_radius_px)
        clinical_df_local = pd.read_csv(clinical_dir)
        clinical_df_local = clinical_df_local.rename(columns={'slide_id': 'imageid'})
        clinical_df_local = clinical_df_local[['imageid'] + clinical_vars_list]

        metadata_prop = metadata_prop[~metadata_prop['phenotype'].isin(artifact_cells)]
        metadata_prop = metadata_prop.loc[:, ~metadata_prop.columns.isin(artifact_cells)]

        cell_type_rename_dict = {
            'Macrophages (CD163+)': 'CD163+ Macrophages',
            'Macrophages (CD163-)': 'CD163- Macrophages',
            'Cytotoxic T cells': 'CD8+ T cells',
            'T cells (other)': 'CD3+ CD4- CD8- T cells',
            'Stromal cells (undefined)': 'Undefined cells'
        }
        for old_string, new_string in cell_type_rename_dict.items():
            pattern = re.escape(old_string)
            metadata_prop.columns = metadata_prop.columns.str.replace(pattern, new_string, regex=True)
            if 'phenotype' in metadata_prop.columns:
                metadata_prop['phenotype'] = metadata_prop['phenotype'].str.replace(pattern, new_string, regex=True)

        metadata_cols = ['phenotype', 'peri_intra_tumoral', 'imageid']
        pattern = '|'.join(map(re.escape, cell_types_keep))
        cell_types_keep_all = metadata_prop.filter(regex=pattern, axis=1).columns
        metadata_prop_subset = metadata_prop[metadata_cols + list(cell_types_keep_all)]
        metadata_prop_subset = metadata_prop_subset[metadata_prop_subset['phenotype'].isin(cell_types_keep_all)]

        anchor_id_cols_intra_peri = ["imageid", "peri_intra_tumoral", "phenotype"]
        anchor_id_cols_whole_tissue = ["imageid", "phenotype"]

        metadata_prop_subset_long_intra_peri = metadata_prop_subset.melt(
            id_vars=anchor_id_cols_intra_peri, value_vars=cell_types_keep_all,
            var_name="interacting_cell_type", value_name="proportion"
        )
        metadata_prop_subset_long_whole_tissue = metadata_prop_subset.melt(
            id_vars=anchor_id_cols_whole_tissue, value_vars=cell_types_keep_all,
            var_name="interacting_cell_type", value_name="proportion"
        )

        metadata_prop_subset_long_intra_peri["has_interaction"] = (
            metadata_prop_subset_long_intra_peri["proportion"] > 0).astype(int)
        metadata_prop_subset_long_whole_tissue["has_interaction"] = (
            metadata_prop_subset_long_whole_tissue["proportion"] > 0).astype(int)

        interaction_counts_intra_peri = (
            metadata_prop_subset_long_intra_peri
            .groupby(anchor_id_cols_intra_peri + ["interacting_cell_type"], as_index=False)
            ["has_interaction"].sum().rename(columns={"has_interaction": "n_anchor_cells_interacting"})
        )
        interaction_counts_whole_tissue = (
            metadata_prop_subset_long_whole_tissue
            .groupby(anchor_id_cols_whole_tissue + ["interacting_cell_type"], as_index=False)
            ["has_interaction"].sum().rename(columns={"has_interaction": "n_anchor_cells_interacting"})
        )

        interaction_counts_whole_tissue['region'] = 'whole_tissue'
        interaction_counts_intra_peri = interaction_counts_intra_peri.rename(columns={'peri_intra_tumoral': 'region'})
        interaction_counts = pd.concat([interaction_counts_intra_peri, interaction_counts_whole_tissue], ignore_index=True)

        total_anchor_cells_intra_peri = (
            metadata_prop_subset.groupby(['imageid', 'phenotype', 'peri_intra_tumoral'])
            .size().reset_index(name='total_anchor_cells')
            .rename(columns={'peri_intra_tumoral': 'region'})
        )
        total_anchor_cells_whole_tissue = (
            metadata_prop_subset.groupby(['imageid', 'phenotype'])
            .size().reset_index(name='total_anchor_cells')
        )
        total_anchor_cells_whole_tissue['region'] = 'whole_tissue'
        total_anchor_cells_all = pd.concat([total_anchor_cells_intra_peri, total_anchor_cells_whole_tissue], ignore_index=True)

        avg_prop_intra_peri = (
            metadata_prop_subset_long_intra_peri
            .groupby(anchor_id_cols_intra_peri + ["interacting_cell_type"], as_index=False)
            ["proportion"].mean()
            .rename(columns={'proportion': 'mean_proportion_interacting_cell_type', 'peri_intra_tumoral': 'region'})
        )
        avg_prop_whole_tissue = (
            metadata_prop_subset_long_whole_tissue
            .groupby(anchor_id_cols_whole_tissue + ["interacting_cell_type"], as_index=False)
            ["proportion"].mean()
            .rename(columns={'proportion': 'mean_proportion_interacting_cell_type'})
        )
        avg_prop_whole_tissue['region'] = 'whole_tissue'

        interaction_df_long = pd.concat([avg_prop_intra_peri, avg_prop_whole_tissue], ignore_index=True)
        interaction_df_long['interaction_radius'] = interaction_radius_px
        interaction_df_long = interaction_df_long.merge(total_anchor_cells_all, on=['imageid', 'phenotype', 'region'], how='left')

        interaction_proportion_counts_df = interaction_df_long.merge(
            interaction_counts, on=['imageid', 'phenotype', 'region', 'interacting_cell_type'], how='left'
        )
        interaction_proportion_counts_df['proportion_of_anchor_cells_interacting'] = (
            interaction_proportion_counts_df['n_anchor_cells_interacting'] /
            interaction_proportion_counts_df['total_anchor_cells']
        )

        interaction_proportion_counts_df_clinical = interaction_proportion_counts_df.merge(
            clinical_df_local, left_on='imageid', right_on='imageid', how='left'
        ).rename(columns={"phenotype": "anchor_cell_type"}).round(4)

        os.makedirs(f'{results_dir}/{out_scimap_interaction_summary_table}', exist_ok=True)
        interaction_proportion_counts_df_clinical.to_csv(output_file, index=False)

    if gen_summary_csv or run_gen_boxplots:
        summarized_df = pd.DataFrame()

        for clinical_var in clinical_vars_list:
            if clinical_var not in interaction_proportion_counts_df_clinical.columns:
                interaction_proportion_counts_df_clinical = interaction_proportion_counts_df_clinical.merge(
                    clinical_df[['slide_id', clinical_var]], left_on='imageid', right_on='slide_id', how='left'
                )

            interaction_subset = interaction_proportion_counts_df_clinical[
                interaction_proportion_counts_df_clinical[clinical_var].notna()
            ].copy()
            interaction_subset[clinical_var] = interaction_subset[clinical_var].astype(int)

            for region in interaction_subset['region'].unique():
                for anchor in interaction_subset['anchor_cell_type'].unique():
                    for interacting in interaction_subset['interacting_cell_type'].unique():
                        if anchor in cell_types_remove or interacting in cell_types_remove:
                            continue

                        df_summary = pd.DataFrame([{
                            'region': region, 'anchor_cell_type': anchor,
                            'interacting_cell_type': interacting, 'clinical_var': clinical_var,
                        }])

                        subset = interaction_subset.loc[
                            (interaction_subset['region'] == region) &
                            (interaction_subset['anchor_cell_type'] == anchor) &
                            (interaction_subset['interacting_cell_type'] == interacting)
                        ]

                        for prop_col in ['mean_proportion_interacting_cell_type', 'proportion_of_anchor_cells_interacting']:
                            prop_df = subset[['imageid', 'anchor_cell_type', 'region',
                                              'interacting_cell_type', prop_col, clinical_var]]

                            df_0 = prop_df[prop_df[clinical_var] == 0].dropna(subset=[prop_col, 'imageid'])
                            df_1 = prop_df[prop_df[clinical_var] == 1].dropna(subset=[prop_col, 'imageid'])
                            group_0 = df_0[prop_col].values
                            group_1 = df_1[prop_col].values
                            samples_0 = df_0['imageid'].values
                            samples_1 = df_1['imageid'].values

                            if len(group_0) < 2 or len(group_1) < 2:
                                continue

                            if run_permutation_test:
                                pval_student_ttest, pval_welch_ttest, pval_mann_whitney, effect_size, pval_permutation_test, direction = run_stats_tests(group_0, group_1, clinical_var, run_permutation_test)
                            else:
                                pval_student_ttest, pval_welch_ttest, pval_mann_whitney, effect_size, direction = run_stats_tests(group_0, group_1, clinical_var, run_permutation_test)

                            df_summary.loc[0, f'direction_{prop_col}'] = direction
                            df_summary.loc[0, f'student_ttest_pval_{prop_col}'] = float(pval_student_ttest)
                            df_summary.loc[0, f'welch_ttest_pval_{prop_col}'] = float(pval_welch_ttest)
                            df_summary.loc[0, f'mann_whitney_pval_{prop_col}'] = float(pval_mann_whitney)
                            df_summary.loc[0, f'effect_size_{prop_col}'] = effect_size
                            if run_permutation_test:
                                df_summary.loc[0, f'permutation_test_pval_{prop_col}'] = pval_permutation_test

                            if run_gen_boxplots:
                                if prop_col == 'mean_proportion_interacting_cell_type':
                                    if anchor == interacting:
                                        y_axis_label_param = f'Mean proportion of {interacting.rstrip("s")} neighbors'
                                    else:
                                        y_axis_label_param = f"Mean proportion of {interacting} around {anchor}"
                                    if anchor in cell_types_rename:
                                        y_axis_label_param = y_axis_label_param.replace(anchor, cell_types_rename[anchor].rstrip("s"))
                                    if interacting in cell_types_rename:
                                        y_axis_label_param = y_axis_label_param.replace(interacting, cell_types_rename[interacting])
                                else:
                                    y_axis_label_param = f'Proportion of {anchor} with ≥1 {interacting.rstrip("s")}'
                                    if anchor in cell_types_rename:
                                        y_axis_label_param = y_axis_label_param.replace(anchor, cell_types_rename[anchor])
                                    if interacting in cell_types_rename:
                                        y_axis_label_param = y_axis_label_param.replace(interacting.rstrip("s"), cell_types_rename[interacting].rstrip("s"))

                                sig_dir = 'significant' if pval_mann_whitney < 0.052 else 'not_significant'
                                boxplot_output_dir = (
                                    f'{results_dir}/{out_scimap_interaction_summary_table}/boxplots/'
                                    f'{clinical_var}/{region}/{prop_col}/{sig_dir}'
                                )
                                gen_boxplots(
                                    group_0, group_1, samples_0, samples_1, clinical_var,
                                    prop_col, region, sample_label, pval_mann_whitney,
                                    effect_size, boxplot_output_dir, add_color_points_stage,
                                    clinical_df, f'{anchor}_{interacting}_{region}_{prop_col}',
                                    title_font_size, subtitle_font_size, y_tick_font_size,
                                    x_tick_font_size, p_value_tick_font_size, x_tick_labels_dict,
                                    y_axis_label_param, boxplot_shapes,
                                    plot_title_param=None, sub_title_param=None,
                                    add_plot_title=False, range_0_1=True
                                )

                        summarized_df = pd.concat([summarized_df, df_summary])

        summarized_df = summarized_df[~summarized_df['anchor_cell_type'].isin(cell_types_remove)]
        summarized_df = summarized_df[~summarized_df['interacting_cell_type'].isin(cell_types_remove)]
        summarized_df = summarized_df.round(4)

        if gen_summary_csv:
            os.makedirs(f'{results_dir}/{out_scimap_interaction_summary_table}', exist_ok=True)
            summarized_df.to_csv(
                f'{results_dir}/{out_scimap_interaction_summary_table}/'
                f'summarized_df_{interaction_radius_px}px.csv', index=False
            )


def interactions_permutation_test(results_dir, metadata, cell_type_columns, artifact_cells,
                                   clinical_vars_list, scimap_data_path, interaction_radius_px,
                                   interaction_radius_um, cell_types_keep, clinical_dir,
                                   out_scimap_interaction_summary_table, run_gen_boxplots,
                                   sample_label, add_color_points_stage, clinical_df,
                                   title_font_size, subtitle_font_size, y_tick_font_size,
                                   x_tick_font_size, p_value_tick_font_size, x_tick_labels_dict,
                                   interaction_type, anchor_cell_type, interacting_cell_type,
                                   region, gen_interaction_summary_table, gen_null_distribution,
                                   scimap_data_path_test, out_scimap_interaction_summary_table_test,
                                   samples_skip, add_plot_title, boxplot_shapes, cell_types_remove,
                                   gen_summary_csv, run_permutation_test, cell_types_rename):
    """
    Run a spatial interaction permutation test.

    If gen_interaction_summary_table is True, generates interaction summary tables
    for each permuted neighborhood analysis directory.

    If gen_null_distribution is True, builds a per-sample null distribution from
    permuted interaction proportions and computes an empirical p-value for each sample.
    """
    if gen_interaction_summary_table:
        for permutation_dir in os.listdir(f'{results_dir}/{scimap_data_path}'):
            scimap_path_perm = f'{scimap_data_path}/{permutation_dir}'
            if not os.path.exists(f'{results_dir}/{scimap_path_perm}/adata_all_combos.h5ad'):
                continue
            out_perm = f'{out_scimap_interaction_summary_table}/{permutation_dir}'
            output_file = f'{results_dir}/{out_perm}/interaction_proportion_counts_df_{interaction_radius_px}px.csv'
            if not os.path.exists(output_file):
                gen_scimap_interaction_summary_table(
                    results_dir, metadata, cell_type_columns, artifact_cells, clinical_vars_list,
                    scimap_path_perm, interaction_radius_px, interaction_radius_um, cell_types_keep,
                    clinical_dir, out_perm, run_gen_boxplots, sample_label, add_color_points_stage,
                    clinical_df, title_font_size, subtitle_font_size, y_tick_font_size, x_tick_font_size,
                    p_value_tick_font_size, x_tick_labels_dict, add_plot_title, interaction_type,
                    anchor_cell_type, interacting_cell_type, region, cell_types_rename, boxplot_shapes,
                    cell_types_remove, gen_summary_csv, run_permutation_test
                )
                print(f'{permutation_dir} done')
            else:
                print(f'{permutation_dir} already done')

    if gen_null_distribution:
        interaction_table_test = pd.read_csv(
            f'{results_dir}/{out_scimap_interaction_summary_table_test}/'
            f'interaction_proportion_counts_df_{interaction_radius_px}px.csv'
        )
        interaction_table_test = interaction_table_test[~interaction_table_test['imageid'].isin(samples_skip)]
        interaction_test_proportion = interaction_table_test.loc[
            (interaction_table_test['anchor_cell_type'] == anchor_cell_type) &
            (interaction_table_test['interacting_cell_type'] == interacting_cell_type) &
            (interaction_table_test['region'] == region),
            ['imageid', interaction_type]
        ]

        permutation_dir_list = os.listdir(f'{results_dir}/{out_scimap_interaction_summary_table}')

        for sample in interaction_test_proportion['imageid']:
            if sample in samples_skip:
                continue
            null_distribution = []
            obs = interaction_test_proportion.loc[
                interaction_test_proportion['imageid'] == sample, interaction_type
            ].values[0]

            for permutation_dir in permutation_dir_list:
                perm_table = pd.read_csv(
                    f'{results_dir}/{out_scimap_interaction_summary_table}/{permutation_dir}/'
                    f'interaction_proportion_counts_df_{interaction_radius_px}px.csv'
                )
                perm_val = perm_table.loc[
                    (perm_table['imageid'] == sample) &
                    (perm_table['anchor_cell_type'] == anchor_cell_type) &
                    (perm_table['interacting_cell_type'] == interacting_cell_type) &
                    (perm_table['region'] == region),
                    interaction_type
                ].values[0]
                null_distribution.append(perm_val)

            p_value = (np.sum(np.array(null_distribution) >= obs) + 1) / (len(null_distribution) + 1)
            print(
                f'{sample} - Observed: {obs:.4f}, N permutations: {len(null_distribution)}, '
                f'Mean perm: {np.mean(null_distribution):.4f}, p-value: {p_value:.4f}'
            )
