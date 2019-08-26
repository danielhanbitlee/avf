import pandas as pd

from fuzzyAVF import fuzzy_smf, get_fuzzy_bins


def get_red_yellow_bins(series: pd.Series, method: str, red_bin=None, yellow_bin=None):
    if method == "Percentile":
        red = round(series.quantile(q=red_bin / 100), 6)
        yellow = round(series.quantile(q=(red_bin + yellow_bin) / 100), 6)
        return red, yellow     

    elif method == "Count":

        red = round(series.sort_values().values[int(round(red_bin, 0)) - 1], 6)
        yellow = round(series.sort_values().values[int(round(red_bin + yellow_bin, 0)) - 1], 6)
        return red, yellow

    elif method == "NAVF":
        mean = series.mean()
        sd = series.std()
        red = round(mean - 3 * sd, 6)
        yellow = round(mean - 2 * sd, 6)

        return red, yellow

    elif method == "fuzzy AVF":
        y = fuzzy_smf(series)
        red, yellow = get_fuzzy_bins(series, y, red_bin, yellow_bin)
        return red, yellow

    else:
        red = None
        yellow = None
        return red, yellow
