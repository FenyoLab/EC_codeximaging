import numpy as np
import pandas as pd
import scipy.stats as stats
from itertools import combinations


def run_stats_tests(clinical_0, clinical_1, clinical_var, run_permutation_test):
    """
    Run statistical tests comparing two groups.

    Returns student t-test, Welch t-test, Mann-Whitney U p-values,
    effect size (median difference), direction

    Parameters
    ----------
    clinical_0, clinical_1 : array-like
        Values for each group.
    clinical_var : str
        Name of the clinical variable (used for labeling only).
   
    """

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


    return (
        round(pval_student_ttest, 4), round(pval_welch_ttest, 4),
        round(pval_mann_whitney, 4), effect_size, direction
    )
