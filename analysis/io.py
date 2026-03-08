import pandas as pd
import anndata as ad


def load_data(results_dir, metadata_path, clinical_dir):
    """Load metadata feather file and clinical CSV."""
    metadata = pd.read_feather(f"{results_dir}/{metadata_path}")
    clinical_df = pd.read_csv(clinical_dir)
    return metadata, clinical_df


def load_scimap_data(results_dir, scimap_data_path, interaction_radius_px):
    """Load scimap AnnData object and merge obs with spatial count data."""
    adata_path = f'{results_dir}/{scimap_data_path}/adata_all_combos.h5ad'
    adata = ad.read_h5ad(adata_path)
    adata_metadata = adata.obs.merge(
        adata.uns[f'spatial_count_radius_{interaction_radius_px}'],
        left_index=True, right_index=True
    )
    return adata_metadata
