"""
scimap/neighborhoods.py
-----------------------
Scimap-based spatial neighborhood analysis.

Runs spatial expression/count/LDA analysis using scimap, clusters cells into
spatial neighborhoods via k-means, and optionally generates:
  - Stacked bar plots per sample and combined
  - Clinical association boxplots
  - Tumor region (intra/peri) boxplots
  - Omero tables for OMERO.web upload
  - Interactive Plotly spatial scatter plots

This module must be run BEFORE gen_scimap_interaction_summary_table, as it
generates the adata_all_combos.h5ad file that the interaction analysis reads.
"""

import os
import numpy as np
import pandas as pd
import anndata as ad
import scimap as sm
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
from scipy import stats


# =============================================================================
# ENTRY POINT
# =============================================================================

def run_neighborhoods(
    save_dir,
    matrix_path,
    metadata_path,
    celltype_subset,
    immune_subset,
    celltypes_rm,
    slides,
    slides_rm,
    spatial_analysis_list,
    spatial_method_list,
    n_knn_list,
    n_kmeans_list,
    n_radius_list,
    output_dir_scimap,
    omero_dict,
    clinical_data,
    clinical_vars_list,
    t_cell_types,
    cell_type_col_param,
    sample_labels=False,
    PD1_phenotypes=True,
    run_gen_omero_tables=False,
    run_gen_barplots=False,
    run_gen_boxplots=False,
    run_gen_pieplots=False,
    run_correlation_plot=False,
):
    """
    Main entry point for spatial neighborhood analysis.

    Steps:
      1. Load data and run scimap spatial analysis + k-means clustering.
      2. Optionally generate omero tables, barplots, boxplots, and pieplots.

    Parameters
    ----------
    save_dir : str
        Top-level save directory.
    matrix_path : str
        Path to counts matrix (.feather or .npy).
    metadata_path : str
        Path to cell metadata (.feather or .csv).
    celltype_subset : list or None
        Specific cell type subsets to plot separately in barplots.
    immune_subset : bool
        If True, generate immune-only barplots (excluding Tumor, Stromal, Endothelial).
    celltypes_rm : list or None
        Cell types to exclude from spatial analysis (e.g. Artifacts).
    slides : list or None
        If provided, subset analysis to these slide IDs.
    slides_rm : list or None
        Slide IDs to exclude from analysis.
    spatial_analysis_list : list
        Scimap spatial methods to run: 'spatial_count', 'spatial_expression', 'spatial_lda'.
    spatial_method_list : list
        Neighborhood definition method: 'radius' or 'knn'.
    n_knn_list : list of int
        K values for KNN neighborhood definition.
    n_kmeans_list : list of int
        Numbers of k-means clusters to try.
    n_radius_list : list of int
        Radius values (in pixels) for radius-based neighborhoods.
    output_dir_scimap : str
        Directory to write all scimap outputs.
    omero_dict : dict
        Mapping of slide_id -> {'roi_id': ...} for Omero table generation.
    clinical_data : str
        Path to clinical CSV file (must contain 'slide_id' column).
    clinical_vars_list : list of str
        Clinical variables to test for neighborhood association.
    t_cell_types : list of str
        Cell type names considered T cells (used for PD1 phenotype renaming).
    cell_type_col_param : str
        Column name in metadata containing cell type labels.
    sample_labels : bool
        If True, annotate individual data points with sample IDs in boxplots.
    PD1_phenotypes : bool
        If True, append PD1 high/low suffix to T cell phenotype names.
    run_gen_omero_tables : bool
        Generate Omero-compatible CSV tables.
    run_gen_barplots : bool
        Generate stacked bar plots of cell type composition per neighborhood.
    run_gen_boxplots : bool
        Generate clinical association boxplots per neighborhood.
    run_gen_pieplots : bool
        Generate pie charts of cell type composition per neighborhood.
    run_correlation_plot : bool
        Generate scimap groupCorrelation plots.
    """
    os.makedirs(output_dir_scimap, exist_ok=True)

    adata_copy, adata_copy_allcelltypes = _gen_adata_spatial(
        matrix_path, metadata_path, output_dir_scimap, slides, slides_rm,
        spatial_analysis_list, spatial_method_list,
        n_knn_list, n_kmeans_list, n_radius_list,
        t_cell_types, celltypes_rm, cell_type_col_param, PD1_phenotypes
    )

    if run_gen_omero_tables:
        _gen_omero_tables(
            adata_copy, adata_copy_allcelltypes, output_dir_scimap,
            spatial_analysis_list, spatial_method_list,
            n_knn_list, n_kmeans_list, n_radius_list, omero_dict
        )

    if run_gen_barplots:
        _gen_barplots(
            adata_copy, output_dir_scimap,
            spatial_analysis_list, spatial_method_list,
            n_knn_list, n_kmeans_list, n_radius_list,
            celltype_subset, PD1_phenotypes, immune_subset
        )

    if run_gen_boxplots:
        adata_spatial = pd.read_csv(f'{output_dir_scimap}/adata_all_combos.csv')
        _gen_boxplots(
            adata_spatial, output_dir_scimap,
            spatial_analysis_list, spatial_method_list,
            n_knn_list, n_kmeans_list, n_radius_list,
            omero_dict, clinical_data, clinical_vars_list,
            t_cell_types, sample_labels, run_correlation_plot
        )

    if run_gen_pieplots:
        _gen_pieplots(adata_copy, output_dir_scimap)


# =============================================================================
# DATA LOADING & ADATA CONSTRUCTION
# =============================================================================

def _load_data(matrix_path, metadata_path, output_dir_scimap, slides_rm, cell_type_col_param):
    """Load counts matrix and metadata, construct AnnData, and save to disk."""
    if matrix_path.endswith('.feather'):
        data = pd.read_feather(matrix_path)
    else:
        data = np.load(matrix_path)

    if metadata_path.endswith('.feather'):
        meta = pd.read_feather(metadata_path)
    else:
        meta = pd.read_csv(metadata_path)

    if 'centroid_x' in meta.columns and 'centroid_y' in meta.columns:
        meta['centroid_x_slide'] = meta['centroid_x'] + meta['tile_h']
        meta['centroid_y_slide'] = meta['centroid_y'] + meta['tile_w']

    rename_dict = {
        'centroid_x_slide': 'X_centroid',
        'centroid_y_slide': 'Y_centroid',
        'area': 'Area',
        'cell_label': 'CellID',
        'slide_id': 'imageid',
        f'{cell_type_col_param}': 'phenotype'
    }
    existing_rename_dict = {k: v for k, v in rename_dict.items() if k in meta.columns}
    meta_ann = meta.rename(columns=existing_rename_dict)

    print("Metadata columns after renaming:", meta_ann.columns.tolist())

    adata = ad.AnnData(data)
    adata.obs = meta_ann
    adata.raw = adata
    adata.uns['all_markers'] = [
        'DAPI', 'MPO', 'Ecadherin', 'PDL1', 'CD163', 'PD1', 'CD47', 'GAL3', 'PARP1',
        'LAG3', 'CD4', 'PI3KCA', 'TIM3', 'CD68', 'ER', 'PR', 'MSH2', 'CD8', 'MSH6',
        'bCatenin1', 'HLAABC', 'MLH1', 'Ki67', 'CD20', 'ARID1A', 'IFNG', 'CD31',
        'PMS', 'CD44', 'PanCytokeratin', 'CD3e'
    ]

    if slides_rm is not None:
        adata = adata[~adata.obs['imageid'].isin(slides_rm)]

    adata.write(f'{output_dir_scimap}/adata.h5ad')
    return adata


def _gen_adata_spatial(matrix_path, metadata_path, output_dir_scimap,
                       slides, slides_rm,
                       spatial_analysis_list, spatial_method_list,
                       n_knn_list, n_kmeans_list, n_radius_list,
                       t_cell_types, celltypes_rm, cell_type_col_param,
                       PD1_phenotypes=True):
    """
    Load or generate AnnData, run scimap spatial analyses, and cluster into
    spatial neighborhoods. Skips already-computed combinations.

    Returns
    -------
    adata_copy : AnnData
        AnnData with phenotype-filtered cells and spatial neighborhood assignments.
    adata_copy_allcelltypes : AnnData
        AnnData with all cell types (including artifacts), used for Omero tables.
    """
    combined_h5ad_path = f'{output_dir_scimap}/adata_all_combos.h5ad'
    allcelltypes_h5ad_path = f'{output_dir_scimap}/adata_allcelltypes.h5ad'

    if os.path.exists(combined_h5ad_path):
        print(f"Loading existing combined AnnData: {combined_h5ad_path}")
        adata_copy = ad.read_h5ad(combined_h5ad_path, backed='r').to_memory()
        if os.path.exists(allcelltypes_h5ad_path):
            adata_copy_allcelltypes = ad.read_h5ad(allcelltypes_h5ad_path, backed='r').to_memory()
        else:
            base_adata = _load_data(matrix_path, metadata_path, output_dir_scimap, slides_rm, cell_type_col_param)
            adata_copy_allcelltypes = base_adata.copy()
    else:
        print("Generating new adata object")
        adata = _load_data(matrix_path, metadata_path, output_dir_scimap, slides_rm, cell_type_col_param)
        adata_copy = adata.copy()
        adata_copy_allcelltypes = adata.copy()

    if PD1_phenotypes:
        adata_copy.obs['phenotype'] = adata_copy.obs['phenotype'].astype(str)
        adata_copy.obs.loc[
            (adata_copy.obs['PD1'] == 'H') & (adata_copy.obs['phenotype'].isin(t_cell_types)),
            'phenotype'
        ] += ' (PD1+ High)'
        adata_copy.obs.loc[
            (adata_copy.obs['PD1'] == 'L') & (adata_copy.obs['phenotype'].isin(t_cell_types)),
            'phenotype'
        ] += ' (PD1+ Low)'
        print(f"Saving: {output_dir_scimap}/adata_obs_PD1_phenotype.csv")
        adata_copy.obs.to_csv(f'{output_dir_scimap}/adata_obs_PD1_phenotype.csv', index=False)

    if slides is not None:
        adata_copy = adata_copy[adata_copy.obs['imageid'].isin(slides)]

    if celltypes_rm is not None:
        adata_copy_allcelltypes = adata_copy_allcelltypes.copy()
        adata_copy = adata_copy[~adata_copy.obs['phenotype'].isin(celltypes_rm)].copy()

    for spatial_analysis in spatial_analysis_list:
        print(f"Running spatial analysis: {spatial_analysis}")
        for spatial_method in spatial_method_list:
            num_list = (
                [int(n) for n in n_radius_list] if spatial_method == 'radius'
                else [int(n) for n in n_knn_list]
            )

            for num in num_list:
                print(f"  {spatial_method} = {num}")
                label_name = f'{spatial_analysis}_{spatial_method}_{num}'

                if label_name not in adata_copy.uns:
                    if spatial_analysis == 'spatial_expression':
                        adata_copy = sm.tl.spatial_expression(
                            adata_copy, x_coordinate='X_centroid', y_coordinate='Y_centroid',
                            z_coordinate=None, method=spatial_method, radius=num, knn=num,
                            imageid='imageid', use_raw=True, log=True, label=label_name,
                            verbose=True, output_dir=None
                        )
                    elif spatial_analysis == 'spatial_count':
                        adata_copy = sm.tl.spatial_count(
                            adata_copy, x_coordinate='X_centroid', y_coordinate='Y_centroid',
                            phenotype='phenotype', method=spatial_method, radius=num, knn=num,
                            imageid='imageid', subset=None, label=label_name
                        )
                    elif spatial_analysis == 'spatial_lda':
                        adata_copy = sm.tl.spatial_lda(
                            adata_copy, x_coordinate='X_centroid', y_coordinate='Y_centroid',
                            phenotype='phenotype', method=spatial_method, radius=num, knn=num,
                            imageid='imageid', num_motifs=10, random_state=0, label=label_name
                        )

                for n_kmeans in n_kmeans_list:
                    spatial_kmeans_column = f'spatial_kmeans_{n_kmeans}_{spatial_analysis}_{spatial_method}_{num}'
                    if spatial_kmeans_column in adata_copy.obs.columns:
                        print(f"  Found existing {spatial_kmeans_column}; skipping")
                    else:
                        print(f"  Running k-means: {spatial_kmeans_column}")
                        adata_copy = sm.tl.spatial_cluster(
                            adata_copy, df_name=label_name, method='kmeans',
                            k=n_kmeans, verbose=True, label=spatial_kmeans_column, random_state=42
                        )

                    adata_copy.obs[spatial_kmeans_column] = adata_copy.obs[spatial_kmeans_column].astype('category')
                    adata_copy.obs['phenotype'] = adata_copy.obs['phenotype'].astype('category')

    adata_copy.write(f'{output_dir_scimap}/adata_all_combos.h5ad')
    adata_copy_allcelltypes.write(f'{output_dir_scimap}/adata_allcelltypes.h5ad')
    adata_copy.obs.to_csv(f'{output_dir_scimap}/adata_all_combos.csv', index=False)

    return adata_copy, adata_copy_allcelltypes


# =============================================================================
# OMERO TABLES
# =============================================================================

def _gen_omero_tables(adata_copy, adata_copy_allcelltypes, output_dir_scimap,
                      spatial_analysis_list, spatial_method_list,
                      n_knn_list, n_kmeans_list, n_radius_list, omero_dict):
    """Assign neighborhood cluster labels to all-celltype AnnData and export Omero CSVs."""
    from src.omero_tables.create_omero_table import create_omero_table

    for spatial_analysis in spatial_analysis_list:
        for spatial_method in spatial_method_list:
            num_list = (
                [int(n) for n in n_radius_list] if spatial_method == 'radius'
                else [int(n) for n in n_knn_list]
            )
            for num in num_list:
                for n_kmeans in n_kmeans_list:
                    spatial_kmeans_column = f'spatial_kmeans_{n_kmeans}_{spatial_analysis}_{spatial_method}_{num}'

                    # Artifact cells get cluster assignment 100
                    adata_copy_allcelltypes.obs[spatial_kmeans_column] = 100
                    matching_indices = adata_copy.obs.index.intersection(adata_copy_allcelltypes.obs.index)
                    adata_copy_allcelltypes.obs.loc[matching_indices, spatial_kmeans_column] = (
                        adata_copy.obs[spatial_kmeans_column].reindex(matching_indices)
                    )

                    for sample in adata_copy_allcelltypes.obs['imageid'].unique():
                        out_dir = os.path.join(output_dir_scimap, "omero_tables", sample)
                        os.makedirs(out_dir, exist_ok=True)
                        table_path = os.path.join(
                            out_dir, f"{spatial_analysis}_{spatial_method}{num}_kmeans{n_kmeans}.csv"
                        )
                        sample_obs = adata_copy_allcelltypes[
                            adata_copy_allcelltypes.obs['imageid'] == sample
                        ].obs[[spatial_kmeans_column, 'phenotype']]
                        roi_value = omero_dict.get(sample, {}).get('roi_id')
                        omero_df = create_omero_table(pd.DataFrame(sample_obs), roi_value)
                        omero_df.to_csv(table_path, index=False)
                        print(f"Omero table saved: {table_path}")


# =============================================================================
# STACKED BAR PLOTS
# =============================================================================

def _gen_barplots(adata_copy, output_dir_scimap, spatial_analysis_list, spatial_method_list,
                  n_knn_list, n_kmeans_list, n_radius_list, celltype_subset,
                  PD1_phenotypes=True, immune_subset=True):
    """Generate stacked bar plots of cell type composition per neighborhood."""
    for spatial_analysis in spatial_analysis_list:
        for spatial_method in spatial_method_list:
            num_list = (
                [int(n) for n in n_radius_list] if spatial_method == 'radius'
                else [int(n) for n in n_knn_list]
            )
            for num in num_list:
                for n_kmeans in n_kmeans_list:
                    spatial_kmeans_column = f'spatial_kmeans_{n_kmeans}_{spatial_analysis}_{spatial_method}_{num}'

                    # Per-sample plots
                    for sample in adata_copy.obs['imageid'].unique():
                        adata_sample = adata_copy[adata_copy.obs['imageid'] == sample]
                        plot_data = adata_sample.obs.groupby(
                            [spatial_kmeans_column, 'phenotype']
                        ).size().reset_index(name='count')
                        total = plot_data['count'].sum()
                        plot_data['count_percentage'] = plot_data['count'] / total

                        out_dir = os.path.join(
                            output_dir_scimap, "stacked_barplots", spatial_analysis,
                            spatial_method, str(num), "slides", sample, "all_celltypes"
                        )
                        os.makedirs(out_dir, exist_ok=True)
                        _plot_stacked_bar(
                            plot_data, spatial_kmeans_column, spatial_analysis,
                            spatial_method, num, n_kmeans,
                            output_dir=out_dir, suffix=f'{sample}.pdf', dpi=300
                        )

                        if immune_subset:
                            subset = plot_data[~plot_data['phenotype'].isin(
                                ['Tumor cells', 'Stromal cells (undefined)', 'Endothelial cells']
                            )]
                            out = os.path.join(out_dir.replace("all_celltypes", "immune_subset"))
                            os.makedirs(out, exist_ok=True)
                            _plot_stacked_bar(subset, spatial_kmeans_column, spatial_analysis,
                                              spatial_method, num, n_kmeans, output_dir=out,
                                              suffix=f'{sample}_immune_subset.pdf', dpi=300)

                        if PD1_phenotypes:
                            _plot_tcell_barplots(
                                adata_sample, plot_data, spatial_kmeans_column, spatial_analysis,
                                spatial_method, num, n_kmeans, output_dir_scimap, sample, per_sample=True
                            )

                        if celltype_subset is not None:
                            for celltypes in celltype_subset:
                                subset = plot_data[plot_data['phenotype'].isin(celltypes)]
                                out = os.path.join(
                                    output_dir_scimap, "stacked_barplots", spatial_analysis,
                                    spatial_method, str(num), "slides", sample, celltypes
                                )
                                os.makedirs(out, exist_ok=True)
                                _plot_stacked_bar(
                                    subset, spatial_kmeans_column, spatial_analysis,
                                    spatial_method, num, n_kmeans,
                                    output_dir=out, suffix=f'{celltypes}.pdf', dpi=300
                                )

                    # Combined (all samples) plots
                    plot_data = adata_copy.obs.groupby(
                        [spatial_kmeans_column, 'phenotype', 'imageid']
                    ).size().reset_index(name='count')
                    totals = plot_data.groupby('imageid')['count'].sum().reset_index(name='total_count')
                    plot_data = plot_data.merge(totals, on='imageid')
                    plot_data['count_percentage_persample'] = plot_data['count'] / plot_data['total_count']
                    plot_data = (
                        plot_data.groupby([spatial_kmeans_column, 'phenotype'])
                        ['count_percentage_persample'].sum().reset_index(name='count_percentage')
                    )

                    out_combined = os.path.join(
                        output_dir_scimap, "stacked_barplots", spatial_analysis,
                        spatial_method, str(num), "slides", "combined", "all_celltypes"
                    )
                    os.makedirs(out_combined, exist_ok=True)
                    _plot_stacked_bar(
                        plot_data, spatial_kmeans_column, spatial_analysis,
                        spatial_method, num, n_kmeans, output_dir=out_combined, dpi=300
                    )

                    if immune_subset:
                        subset = plot_data[~plot_data['phenotype'].isin(
                            ['Tumor cells', 'Stromal cells (undefined)', 'Endothelial cells']
                        )]
                        out = os.path.join(
                            output_dir_scimap, "stacked_barplots", spatial_analysis,
                            spatial_method, str(num), "slides", "combined", "immune_subset"
                        )
                        os.makedirs(out, exist_ok=True)
                        _plot_stacked_bar(subset, spatial_kmeans_column, spatial_analysis,
                                          spatial_method, num, n_kmeans, output_dir=out,
                                          suffix="immune_subset.pdf", dpi=300)

                    if PD1_phenotypes:
                        _plot_tcell_barplots(
                            adata_copy, plot_data, spatial_kmeans_column, spatial_analysis,
                            spatial_method, num, n_kmeans, output_dir_scimap, sample=None, per_sample=False
                        )

                    if celltype_subset is not None:
                        for celltypes in celltype_subset:
                            subset = plot_data[plot_data['phenotype'].isin(celltypes)]
                            out = os.path.join(
                                output_dir_scimap, "stacked_barplots", spatial_analysis,
                                spatial_method, str(num), "slides", "combined", celltypes
                            )
                            os.makedirs(out, exist_ok=True)
                            _plot_stacked_bar(
                                subset, spatial_kmeans_column, spatial_analysis,
                                spatial_method, num, n_kmeans,
                                output_dir=out, suffix=f"{celltypes}.pdf", dpi=300
                            )


def _plot_tcell_barplots(adata_obj, plot_data, spatial_kmeans_column, spatial_analysis,
                         spatial_method, num, n_kmeans, output_dir_scimap, sample, per_sample):
    """Generate T cell, PD1+, and T cell subtype stacked bar plots."""
    base = os.path.join(
        output_dir_scimap, "stacked_barplots", spatial_analysis, spatial_method, str(num),
        "slides", sample if per_sample else "combined"
    )

    # All T cells
    subset = plot_data[plot_data['phenotype'].str.contains('T cells', case=True, na=False)]
    out = os.path.join(base, 'Tcell_subset')
    os.makedirs(out, exist_ok=True)
    suffix = f'{sample}_Tcellsubset.pdf' if per_sample else 'Tcellsubset.pdf'
    _plot_stacked_bar(subset, spatial_kmeans_column, spatial_analysis, spatial_method,
                      num, n_kmeans, output_dir=out, suffix=suffix, dpi=300)

    # PD1+ T cells (as proportion of all T cells)
    obs = adata_obj.obs if hasattr(adata_obj, 'obs') else adata_obj
    for cell_filter, subdir, file_suffix in [
        ('T cell', 'TcellPD1_subset', 'TcellPD1subset'),
        ('Cytotoxic T cells', 'CytotoxicTcellPD1_subset', 'CytotoxicTcellPD1subset'),
        ('Helper T cells', 'HelperTcellPD1_subset', 'HelperTcellPD1subset'),
        ('T cells (other)', 'TcellotherPD1_subset', 'TcellotherPD1subset'),
    ]:
        pd1_plot = obs.groupby([spatial_kmeans_column, 'phenotype', 'imageid']).size().reset_index(name='count')
        totals = (
            pd1_plot[pd1_plot['phenotype'].str.contains(cell_filter, case=False, na=False, regex=False)]
            .groupby('imageid')['count'].sum().reset_index(name='total_count')
        )
        pd1_plot = pd1_plot.merge(totals, on='imageid')
        pd1_plot['count_percentage_persample'] = pd1_plot['count'] / pd1_plot['total_count']
        pd1_plot = (
            pd1_plot.groupby([spatial_kmeans_column, 'phenotype'])
            ['count_percentage_persample'].sum().reset_index(name='count_percentage')
        )

        pd1_filter = 'PD1' if cell_filter == 'T cell' else f'{cell_filter} (PD1'
        subset_pd1 = pd1_plot[pd1_plot['phenotype'].str.contains(pd1_filter, case=True, na=False, regex=False)]
        out = os.path.join(base, subdir)
        os.makedirs(out, exist_ok=True)
        suf = f'{sample}_{file_suffix}.pdf' if per_sample else f'{file_suffix}.pdf'
        _plot_stacked_bar(subset_pd1, spatial_kmeans_column, spatial_analysis,
                          spatial_method, num, n_kmeans, output_dir=out, suffix=suf, dpi=300)


def _plot_stacked_bar(plot_data, spatial_kmeans_column, spatial_analysis, spatial_method,
                      num, n_kmeans, output_dir, suffix='.pdf', dpi=300):
    """Render and save a single stacked bar plot."""
    filename = f"stacked_barplot_{spatial_analysis}_{spatial_method}_{num}_kmeans_{n_kmeans}{suffix}"
    if os.path.exists(os.path.join(output_dir, filename)):
        return

    plt.figure(figsize=(23, 8))
    unique_kmeans_sorted = sorted(plot_data[spatial_kmeans_column].unique(), key=int)
    unique_phenotypes = []

    for kmeans_value in unique_kmeans_sorted:
        current_data = plot_data[plot_data[spatial_kmeans_column] == kmeans_value]
        counts = current_data['count_percentage']
        phenotypes = current_data['phenotype']

        plt.bar(
            kmeans_value, counts, label=phenotypes,
            color=sns.color_palette("husl", len(phenotypes)),
            bottom=counts.cumsum().shift(fill_value=0)
        )
        for p in phenotypes:
            if p not in unique_phenotypes:
                unique_phenotypes.append(p)

    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels[::-1], handles[::-1]))
    plt.legend(by_label.values(), by_label.keys(), title='Phenotype',
               loc='upper right', bbox_to_anchor=(1.2, 1))

    title_suffix = suffix.replace('.pdf', '')
    plt.title(f'Stacked Bar Plot of {spatial_analysis} {spatial_method} {num} vs Phenotype - {title_suffix}')
    plt.xlabel('Spatial K-means Clusters', fontsize=12)
    plt.ylabel('Count percentage')
    plt.xticks(rotation=45)
    plt.subplots_adjust(right=0.75)

    plt.savefig(os.path.join(output_dir, filename), dpi=dpi)
    plt.close()


# =============================================================================
# BOXPLOTS (CLINICAL & TUMOR REGION)
# =============================================================================

def _gen_boxplots(adata_spatial, output_dir_scimap, spatial_analysis_list, spatial_method_list,
                  n_knn_list, n_kmeans_list, n_radius_list, omero_dict, clinical_data,
                  clinical_vars_list, t_cell_types, sample_labels, run_correlation_plot):
    """Generate clinical association boxplots and tumor region comparisons per neighborhood."""
    df_significance_clinical = pd.DataFrame(
        columns=['kmeans', 'neighborhood', 'spatial_analysis', 'spatial_method', 'num', 'clinical_var', 'pvalue']
    )
    df_significance_tumorregion = pd.DataFrame(
        columns=['kmeans', 'neighborhood', 'spatial_analysis', 'spatial_method', 'num', 'clinical_var', 'pvalue']
    )
    df_significance_tumorregion_clinical = pd.DataFrame(
        columns=['kmeans', 'neighborhood', 'spatial_analysis', 'spatial_method', 'num', 'clinical_var', 'pvalue', 'tumor_region']
    )

    n_kmeans_str = '_'.join(map(str, n_kmeans_list))
    n_radius_str = '_'.join(map(str, n_radius_list))
    spatial_method_str = '_'.join(spatial_method_list)

    if not isinstance(adata_spatial, pd.DataFrame):
        adata_spatial = adata_spatial.obs

    for spatial_analysis in spatial_analysis_list:
        for spatial_method in spatial_method_list:
            num_list = (
                [int(n) for n in n_radius_list] if spatial_method == 'radius'
                else [int(n) for n in n_knn_list]
            )
            for num in num_list:
                for n_kmeans in n_kmeans_list:
                    spatial_kmeans_column = f'spatial_kmeans_{n_kmeans}_{spatial_analysis}_{spatial_method}_{num}'

                    if run_correlation_plot:
                        sm.pl.groupCorrelation(
                            adata=f'{output_dir_scimap}/adata_all_combos.h5ad',
                            groupBy=spatial_kmeans_column, condition='phenotype',
                            fileName=f'Correlation_{spatial_analysis}_{spatial_method}{num}_kmeans{n_kmeans}.pdf',
                            saveDir=f"{output_dir_scimap}/correlationplots/", figsize=(6, 4)
                        )

                    for sample in adata_spatial['imageid'].unique():
                        _plotly_scatter(
                            adata_spatial,
                            output_dir=f"{output_dir_scimap}/spatial_plots/{spatial_analysis}/{spatial_method}/{num}/kmeans{n_kmeans}",
                            suffix=f'{spatial_analysis}_{spatial_method}_{num}_kmeans{n_kmeans}_{sample}',
                            phenotype=spatial_kmeans_column, image_id=sample, size=2
                        )

                    merged_clinical = _gen_clinical_boxplot_input(
                        adata_spatial, spatial_kmeans_column, clinical_data
                    )
                    has_region = 'peri_intra_tumoral' in adata_spatial.columns

                    if has_region:
                        merged_region = _gen_tumor_region_boxplot_input(
                            adata_spatial, spatial_kmeans_column, clinical_data
                        )

                    for neighborhood in range(n_kmeans):
                        neighborhood_clinical = merged_clinical[
                            merged_clinical[spatial_kmeans_column] == neighborhood
                        ]

                        if has_region:
                            neighborhood_region = merged_region[
                                merged_region[spatial_kmeans_column] == neighborhood
                            ]
                            df_significance_tumorregion = _plot_tumor_region_boxplots(
                                neighborhood_region, output_dir_scimap, n_kmeans, neighborhood,
                                num, spatial_method, spatial_analysis, df_significance_tumorregion, sample_labels
                            )
                            for region in neighborhood_region['peri_intra_tumoral'].unique():
                                region_subset = neighborhood_region[
                                    neighborhood_region['peri_intra_tumoral'] == region
                                ]
                                df_significance_tumorregion_clinical = _plot_clinical_boxplots(
                                    region_subset, output_dir_scimap, n_kmeans, neighborhood, num,
                                    spatial_method, spatial_analysis, df_significance_tumorregion_clinical,
                                    clinical_vars_list, sample_labels, region=region
                                )

                        df_significance_clinical = _plot_clinical_boxplots(
                            neighborhood_clinical, output_dir_scimap, n_kmeans, neighborhood, num,
                            spatial_method, spatial_analysis, df_significance_clinical,
                            clinical_vars_list, sample_labels, region=None
                        )

    sig_dir = f'{output_dir_scimap}/significant_boxplot_results'
    os.makedirs(sig_dir, exist_ok=True)

    df_significance_clinical['pvalue'] = pd.to_numeric(df_significance_clinical['pvalue'])
    df_significance_clinical = df_significance_clinical.sort_values('pvalue')
    df_significance_clinical.to_csv(
        f'{sig_dir}/df_significance_clinical_{clinical_vars_list}_kmeans_{n_kmeans_str}_{spatial_method_str}_{n_radius_str}.csv'
    )

    if 'peri_intra_tumoral' in adata_spatial.columns:
        df_significance_tumorregion['pvalue'] = pd.to_numeric(df_significance_tumorregion['pvalue'])
        df_significance_tumorregion_clinical['pvalue'] = pd.to_numeric(df_significance_tumorregion_clinical['pvalue'])
        df_significance_tumorregion.sort_values('pvalue').to_csv(
            f'{sig_dir}/df_significance_tumorregion_kmeans_{n_kmeans_str}_{spatial_method_str}_{n_radius_str}.csv'
        )
        df_significance_tumorregion_clinical.sort_values('pvalue').to_csv(
            f'{sig_dir}/df_significance_tumorregion_clinical_{clinical_vars_list}_kmeans_{n_kmeans_str}_{spatial_method_str}_{n_radius_str}.csv'
        )


def _gen_clinical_boxplot_input(adata_spatial, spatial_kmeans_column, clinical_data):
    """Build merged DataFrame of neighborhood proportions + clinical variables."""
    plot_data = adata_spatial.groupby([spatial_kmeans_column, 'imageid']).size().reset_index(name='count')
    totals = plot_data.groupby('imageid')['count'].sum().reset_index(name='total_count')
    plot_data = plot_data.merge(totals, on='imageid')
    plot_data['count_percentage_persample'] = plot_data['count'] / plot_data['total_count']
    clinical_df = pd.read_csv(clinical_data).rename(columns={"slide_id": "imageid"})
    return plot_data.merge(clinical_df, on='imageid', how='left')


def _gen_tumor_region_boxplot_input(adata_spatial, spatial_kmeans_column, clinical_data):
    """Build merged DataFrame of neighborhood proportions per tumor region + clinical variables."""
    plot_data = adata_spatial.groupby(
        [spatial_kmeans_column, 'imageid', 'peri_intra_tumoral']
    ).size().reset_index(name='count')
    totals = plot_data.groupby(['imageid', 'peri_intra_tumoral'])['count'].sum().reset_index(name='total_count')
    plot_data = plot_data.merge(totals, on=['imageid', 'peri_intra_tumoral'])
    plot_data['count_percentage_persample'] = plot_data['count'] / plot_data['total_count']
    clinical_df = pd.read_csv(clinical_data).rename(columns={"slide_id": "imageid"})
    return plot_data.merge(clinical_df, on='imageid', how='left')


def _plot_clinical_boxplots(merged_data, output_dir_scimap, n_kmeans, neighborhood,
                             num, spatial_method, spatial_analysis, df_significance,
                             clinical_vars_list, sample_labels, region=None):
    """Plot and save a boxplot for each clinical variable vs neighborhood proportion."""
    for clinical_var in clinical_vars_list:
        if clinical_var not in merged_data.columns:
            print(f"Warning: {clinical_var} not found in data")
            continue

        unique_outcomes = merged_data[clinical_var].dropna().unique()
        if len(unique_outcomes) < 2:
            print(f"Skipping {clinical_var}: insufficient unique values")
            continue

        plt.figure(figsize=(9, 11))
        sns.boxplot(data=merged_data, x=clinical_var, y='count_percentage_persample')
        ax = plt.gca()
        sns.stripplot(data=merged_data, x=clinical_var, y='count_percentage_persample',
                      color='red', alpha=0.3, size=10)

        if sample_labels:
            unique_outcomes_sorted = sorted(list(unique_outcomes))
            for _, row in merged_data.iterrows():
                if pd.isna(row[clinical_var]):
                    continue
                x_pos = unique_outcomes_sorted.index(row[clinical_var])
                ax.annotate(row['imageid'], (x_pos, row['count_percentage_persample']),
                            xytext=(5, 0), textcoords='offset points',
                            fontsize=10, ha='left', va='center')

        title = f'Counts by {clinical_var}, neighborhood:{neighborhood}, {n_kmeans} clusters, {spatial_analysis}, {spatial_method}, {num}'
        if region is not None:
            title += f', {region}'
        plt.title(title, pad=20)
        plt.xlabel(clinical_var)
        plt.ylabel('Count Percentage per Sample')

        if len(unique_outcomes) == 2:
            g0 = merged_data[merged_data[clinical_var] == unique_outcomes[0]]['count_percentage_persample']
            g1 = merged_data[merged_data[clinical_var] == unique_outcomes[1]]['count_percentage_persample']
            if len(g0) > 1 and len(g1) > 1:
                _, pval = stats.ttest_ind(g0, g1)
                plt.subplots_adjust(top=0.85)
                plt.figtext(0.5, 0.9, f'p-value: {pval:.3f}', ha='center')

                if pval <= 0.05:
                    print(f'{clinical_var} kmeans{n_kmeans} {neighborhood} {spatial_analysis} {spatial_method}{num} p={pval:.6f}')
                    sig_title = f'boxplot_{clinical_var}_kmeans{n_kmeans}_{neighborhood}_{spatial_analysis}_{spatial_method}_{num}'
                    sig_dir = f'{output_dir_scimap}/clinical_boxplots/significant'
                    if region is not None:
                        sig_dir += f'/{region}'
                        sig_title += f'_{region}'
                    if sample_labels:
                        sig_title += '_sample_labels'
                    os.makedirs(sig_dir, exist_ok=True)
                    plt.savefig(f'{sig_dir}/{sig_title}.pdf')

                    new_row = {
                        'kmeans': n_kmeans, 'neighborhood': neighborhood,
                        'spatial_analysis': spatial_analysis, 'spatial_method': spatial_method,
                        'num': num, 'clinical_var': clinical_var, 'pvalue': pval
                    }
                    if region is not None:
                        new_row['tumor_region'] = region
                    df_significance = pd.concat(
                        [df_significance, pd.DataFrame([new_row])], ignore_index=True
                    )

        out_path = os.path.join(
            output_dir_scimap, 'clinical_boxplots', spatial_analysis,
            spatial_method, str(num), f'kmeans{n_kmeans}', clinical_var
        )
        plot_title = f'boxplot_{clinical_var}_kmeans{n_kmeans}_{neighborhood}_{spatial_analysis}_{spatial_method}_{num}'
        if region is not None:
            out_path += f'/{region}'
            plot_title += f'_{region}'
        os.makedirs(out_path, exist_ok=True)
        plt.savefig(f'{out_path}/{plot_title}.pdf', bbox_inches='tight', dpi=300)
        plt.close()

    return df_significance


def _plot_tumor_region_boxplots(merged_data, output_dir_scimap, n_kmeans, neighborhood,
                                 num, spatial_method, spatial_analysis, df_significance,
                                 sample_labels, x_var='peri_intra_tumoral'):
    """Plot and save a boxplot comparing intra vs peritumoral neighborhood proportions."""
    unique_outcomes = merged_data[x_var].unique()

    plt.figure(figsize=(9, 11))
    sns.boxplot(data=merged_data, x=x_var, y='count_percentage_persample')
    ax = plt.gca()
    sns.stripplot(data=merged_data, x=x_var, y='count_percentage_persample',
                  color='red', alpha=0.3, size=4)

    if sample_labels:
        unique_outcomes_sorted = sorted(list(unique_outcomes))
        for _, row in merged_data.iterrows():
            if pd.isna(row[x_var]):
                continue
            x_pos = unique_outcomes_sorted.index(row[x_var])
            ax.annotate(row['imageid'], (x_pos, row['count_percentage_persample']),
                        xytext=(2, 0), textcoords='offset points',
                        fontsize=8, ha='left', va='center')

    plt.title(
        f'Cell Counts by Tumor Region, neighborhood:{neighborhood}, {n_kmeans} clusters, {spatial_analysis}, {spatial_method}, {num}',
        pad=20
    )
    plt.xlabel(x_var)
    plt.ylabel('Count Percentage per Sample per Region')

    if len(unique_outcomes) == 2:
        g0 = merged_data[merged_data[x_var] == unique_outcomes[0]]['count_percentage_persample']
        g1 = merged_data[merged_data[x_var] == unique_outcomes[1]]['count_percentage_persample']
        if len(g0) > 1 and len(g1) > 1:
            _, pval = stats.ttest_ind(g0, g1)
            plt.subplots_adjust(top=0.85)
            if pval <= 0.05:
                pval_str = f"{pval:.2e}" if pval < 0.0001 else str(round(pval, 4))
                plt.figtext(0.5, 0.9, f'p-value: {pval_str}', ha='center')
                print(f'{x_var} kmeans{n_kmeans} {neighborhood} {spatial_analysis} {spatial_method}{num} p={pval_str}')

                sig_dir = f'{output_dir_scimap}/{x_var}_boxplots/significant'
                os.makedirs(sig_dir, exist_ok=True)
                file_name = f"boxplot_{x_var}_kmeans{n_kmeans}_{neighborhood}_{spatial_analysis}_{spatial_method}_{num}"
                if sample_labels:
                    file_name += '_sample_labels'
                plt.savefig(f'{sig_dir}/{file_name}.pdf')

                df_significance = pd.concat([df_significance, pd.DataFrame([{
                    'kmeans': n_kmeans, 'neighborhood': neighborhood,
                    'spatial_analysis': spatial_analysis, 'spatial_method': spatial_method,
                    'num': num, 'tumor_region': 'NA', 'clinical_var': x_var, 'pvalue': pval
                }])], ignore_index=True)

    out_path = os.path.join(
        output_dir_scimap, f'{x_var}_boxplots', spatial_analysis,
        spatial_method, str(num), f'kmeans{n_kmeans}'
    )
    os.makedirs(out_path, exist_ok=True)
    plt.savefig(
        os.path.join(out_path, f'boxplot_kmeans{n_kmeans}_{neighborhood}_{spatial_analysis}_{spatial_method}_{num}.pdf'),
        bbox_inches='tight', dpi=300
    )
    plt.close()

    return df_significance


# =============================================================================
# PIE CHARTS
# =============================================================================

def _gen_pieplots(adata_copy, output_dir_scimap):
    """Generate pie charts of cell type composition per neighborhood, per tumor region."""
    spatial_kmeans_cols = [col for col in adata_copy.obs.columns if "spatial_kmeans" in col]
    for col in spatial_kmeans_cols:
        for neighborhood in range(len(adata_copy.obs[col].unique())):
            if 'peri_intra_tumoral' in adata_copy.obs.columns:
                for region in adata_copy.obs['peri_intra_tumoral'].unique():
                    adata_region = adata_copy[adata_copy.obs['peri_intra_tumoral'] == region]
                    celltypes = adata_region.obs[
                        (adata_region.obs[col] == str(neighborhood)) &
                        (adata_region.obs['peri_intra_tumoral'] == region)
                    ]['phenotype'].unique()
                    celltypes_no_tumor = [c for c in celltypes if 'Tumor cells' not in c]
                    celltypes_no_stromal = [c for c in celltypes_no_tumor if 'Stromal cells (undefined)' not in c]

                    save_dir = f"{output_dir_scimap}/piecharts/{col}/{neighborhood}"
                    sm.pl.pie(adata_region, phenotype='phenotype', group_by=col,
                              subset_groupby=[str(neighborhood)], subset_phenotype=celltypes,
                              legend=False, saveDir=save_dir, title=col,
                              fileName=f'piechart_{col}_allcells_{region}.pdf')
                    sm.pl.pie(adata_region, phenotype='phenotype', group_by=col,
                              subset_groupby=[str(neighborhood)], subset_phenotype=celltypes_no_tumor,
                              legend=False, saveDir=save_dir, title=col,
                              fileName=f'piechart_{col}_without_tumor_{region}.pdf')
                    sm.pl.pie(adata_region, phenotype='phenotype', group_by=col,
                              subset_groupby=[str(neighborhood)], subset_phenotype=celltypes_no_stromal,
                              legend=False, saveDir=save_dir, title=col,
                              fileName=f'piechart_{col}_without_tumor_stromal_cells_{region}.pdf')

            celltypes = adata_copy.obs[adata_copy.obs[col] == str(neighborhood)]['phenotype'].unique()
            celltypes_no_tumor = [c for c in celltypes if 'Tumor cells' not in c]
            celltypes_no_stromal = [c for c in celltypes_no_tumor if 'Stromal cells (undefined)' not in c]
            save_dir = f"{output_dir_scimap}/piecharts/{col}/{neighborhood}"

            sm.pl.pie(adata_copy, phenotype='phenotype', group_by=col,
                      subset_groupby=[str(neighborhood)], subset_phenotype=celltypes,
                      legend=False, saveDir=save_dir, title=col,
                      fileName=f'piechart_{col}_allcells.pdf')
            sm.pl.pie(adata_copy, phenotype='phenotype', group_by=col,
                      subset_groupby=[str(neighborhood)], subset_phenotype=celltypes_no_tumor,
                      legend=False, saveDir=save_dir, title=col,
                      fileName=f'piechart_{col}_without_tumor.pdf')
            sm.pl.pie(adata_copy, phenotype='phenotype', group_by=col,
                      subset_groupby=[str(neighborhood)], subset_phenotype=celltypes_no_stromal,
                      legend=False, saveDir=save_dir, title=col,
                      fileName=f'piechart_{col}_without_tumor_stromal_cells.pdf')


# =============================================================================
# PLOTLY SPATIAL SCATTER
# =============================================================================

def _plotly_scatter(adata, output_dir, suffix, phenotype, image_id=None,
                    x='X_centroid', y='Y_centroid', size=2, **kwargs):
    """Save an interactive HTML scatter plot colored by phenotype/neighborhood."""
    if image_id is not None:
        adata = adata[adata['imageid'] == image_id]
    data = pd.DataFrame({'x': adata[x], 'y': adata[y], 'col': adata[phenotype]})
    data = data.sort_values(by=['col'])
    fig = px.scatter(data, x="x", y="y", color="col", **kwargs)
    fig.update_traces(marker=dict(size=size), selector=dict(mode='markers'),
                      hoverlabel=dict(namelength=-1))
    fig.update_yaxes(autorange="reversed", tickformat='g')
    fig.update_xaxes(tickformat='g')
    fig.update_layout({'plot_bgcolor': 'rgba(0,0,0,0)', 'paper_bgcolor': 'rgba(0,0,0,0)'})
    os.makedirs(output_dir, exist_ok=True)
    fig.write_html(f'{output_dir}/{suffix}.html')
