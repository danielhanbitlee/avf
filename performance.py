import pandas as pd

from identify_outliers import get_red_yellow_bins


def generate_confusion_matrix(raw_data: pd.core.frame.DataFrame,
                              avf_data: pd.core.frame.DataFrame, outlier_col: str,
                              outlier_label: str, avf_col: str,
                              method: str, red_bin=None, yellow_bin=None):

    if red_bin and yellow_bin:
        try:
            red_bin = int(red_bin)
            yellow_bin = int(yellow_bin)

        # value error if trying to convert float to int
        except ValueError:
            red_bin = float(red_bin)
            yellow_bin = float(yellow_bin)

    true_outliers_idx, true_non_outliers_idx = get_true_outliers_idx(raw_data,
                                                                    outlier_col,
                                                                    outlier_label)

    (pred_outliers_idx,
     pred_potential_outliers_idx,
     pred_non_outliers_idx) = predict_outliers(avf_data, avf_col,
                                               method, red_bin,
                                               yellow_bin)

    # tp
    tp = len(true_outliers_idx.intersection(pred_outliers_idx))

    # tn
    tn = len(true_non_outliers_idx.intersection(pred_non_outliers_idx.union(pred_potential_outliers_idx)))

    # fp
    fp = len(pred_outliers_idx.intersection(true_non_outliers_idx))

    # fn
    fn = len(pred_non_outliers_idx.union(pred_potential_outliers_idx).intersection(true_outliers_idx))

    try:
        # accuracy
        acc = round((tp + tn) / (tp + tn + fp + fn), 2)

    except ZeroDivisionError:
        acc = "Not applicable" 
    try:
        # sensitivity
        sens = round(tp / (tp + fn), 2)

    except ZeroDivisionError:
        sens = "Not applicable"

    try:
        # specificity
        spec = round(tn / (tn + fp), 2)

    except ZeroDivisionError:
        spec = "Not applicable"

    try:
        # precision
        prcsn = round(tp / (tp + fp), 2)

    except ZeroDivisionError:
        prcsn = "Not applicable"

    n_obs = raw_data.shape[0]

    n_outliers = len(true_outliers_idx)

    pct_outliers = round(n_outliers / n_obs * 100, 2)

    return tp, tn, fp, fn, acc, sens, spec, prcsn, n_obs, n_outliers, pct_outliers


def get_true_outliers_idx(raw_data: pd.core.frame.DataFrame, col, outlier_label):
    outliers = set(raw_data.loc[raw_data[col] == outlier_label].index)
    non_outliers = set(raw_data.loc[raw_data[col] != outlier_label].index)
    return outliers, non_outliers 


def predict_outliers(avf_data: pd.core.frame.DataFrame, avf_col: str, method: str,
                     red_bin=None, yellow_bin=None):
    red, yellow = get_red_yellow_bins(avf_data[avf_col], method, red_bin, yellow_bin)

    if red and yellow:    
        outliers_idx = set(avf_data.loc[avf_data[avf_col] <= red, :].index) 
        potential_outliers_idx = set(avf_data.loc[(avf_data[avf_col] > red) & 
                                              (avf_data[avf_col] <= yellow), :].index) 
        non_outliers_idx = set(avf_data.loc[avf_data[avf_col] > yellow, :].index)

        return outliers_idx, potential_outliers_idx, non_outliers_idx

    # If red and yellow values are None, return None for outliers idx and potential outliers idx
    return None, None, None

