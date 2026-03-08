import numpy as np
import pandas as pd
import scipy.stats as stats
from itertools import combinations


def run_stats_tests(clinical_0, clinical_1, clinical_var, run_permutation_test):
    """
    Run statistical tests comparing two groups.

    Returns student t-test, Welch t-test, Mann-Whitney U p-values,
    effect size (median difference), direction, and optionally a
    permutation test p-value.

    Parameters
    ----------
    clinical_0, clinical_1 : array-like
        Values for each group.
    clinical_var : str
        Name of the clinical variable (used for labeling only).
    run_permutation_test : bool
        If True, also runs an exact permutation test on median difference.
    """
    if run_permutation_test:
        if isinstance(clinical_0, pd.DataFrame):
            clinical_0 = clinical_0.iloc[:, 0].values
        if isinstance(clinical_1, pd.DataFrame):
            clinical_1 = clinical_1.iloc[:, 0].values
        if clinical_0.ndim > 1:
            clinical_0 = clinical_0.flatten()
        if clinical_1.ndim > 1:
            clinical_1 = clinical_1.flatten()

        values = np.concatenate([clinical_0, clinical_1])
        labels = np.array([0] * len(clinical_0) + [1] * len(clinical_1))
        permutation_test_df = pd.DataFrame({"metric": values, "clinical_group": labels})

        n_total = len(values)
        n_group1 = len(clinical_0)
        T_perm = []

        for indices_group1 in combinations(range(n_total), n_group1):
            labels_perm = np.zeros(n_total, dtype=int)
            labels_perm[list(indices_group1)] = 1
            median_diff = np.median(values[labels_perm == 1]) - np.median(values[labels_perm == 0])
            T_perm.append(median_diff)

        T_perm = np.array(T_perm)
        group0 = permutation_test_df["metric"][permutation_test_df["clinical_group"] == 0]
        group1 = permutation_test_df["metric"][permutation_test_df["clinical_group"] == 1]
        T_obs = np.median(group1) - np.median(group0)
        pval_permutation_test = (np.sum(np.abs(T_perm) >= np.abs(T_obs)) + 1) / (len(T_perm) + 1)

    effect_size = round(np.median(clinical_1) - np.median(clinical_0), 4)

    _, pval_student_ttest = stats.ttest_ind(clinical_0, clinical_1, equal_var=True)
    _, pval_welch_ttest = stats.ttest_ind(clinical_0, clinical_1, equal_var=False)
    _, pval_mann_whitney = stats.mannwhitneyu(clinical_0, clinical_1)

    pval_student_ttest = float(pval_student_ttest)
    pval_welch_ttest = float(pval_welch_ttest)
    pval_mann_whitney = float(pval_mann_whitney)

    direction = (
        'up_group_1' if np.mean(clinical_1) > np.mean(clinical_0)
        else 'up_group_0' if np.mean(clinical_1) < np.mean(clinical_0)
        else 'No Difference'
    )

    if run_permutation_test:
        return (
            round(pval_student_ttest, 4), round(pval_welch_ttest, 4),
            round(pval_mann_whitney, 4), effect_size,
            round(pval_permutation_test, 4), direction
        )
    else:
        return (
            round(pval_student_ttest, 4), round(pval_welch_ttest, 4),
            round(pval_mann_whitney, 4), effect_size, direction
        )
