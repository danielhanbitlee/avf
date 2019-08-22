import numpy as np
import pandas as pd


def fuzzy_smf(series: pd.Series):
    avg_avf = series.mean()
    sd_avf = series.std() 
    max_avf = series.max()

    # calculate a
    a = calc_a(avg_avf, sd_avf, max_avf)

    # calculate c
    c = calc_c(avg_avf, sd_avf, max_avf) 
    
    return smf(series, a, c)


def calc_a(avg_avf, sd_avf, max_avf):
    if max_avf > 3 * sd_avf:
        return avg_avf - 3 * sd_avf
    elif max_avf > 2 * sd_avf:
        return avg_avf - 2 * sd_avf
    else:
        return avg_avf - sd_avf


def calc_c(avg_avf, sd_avf, max_avf):
    if max_avf > 3 * sd_avf:
        return avg_avf + 3 * sd_avf
    elif max_avf > 2 * sd_avf:
        return avg_avf + 2 * sd_avf
    else:
        return avg_avf


def get_fuzzy_bins(series: pd.Series, y: np.ndarray, red_bin: float, yellow_bin: float):
    """
    Get avf values that correspond to cut off values from fuzzy s-function
    """
    # get index of y where y is max of (y <= red bin)
    red_idx = np.where(y == max(y[y <= red_bin]))[0][0] 
    red_value = series[red_idx]

    # get index of y where y is max of (y <= red bin + yellow_bin)
    yellow_idx = np.where(y == max(y[y <= red_bin + yellow_bin]))[0][0]
    yellow_value = series[yellow_idx]

    return red_value, yellow_value 
 

def smf(x, a, b):
    """
    S-function fuzzy membership generator.
    From https://github.com/scikit-fuzzy/scikit-fuzzy/blob/master/skfuzzy/membership/generatemf.py
    Parameters
    ----------
    x : 1d array
        Independent variable.
    a : float
        'foot', where the function begins to climb from zero.
    b : float
        'ceiling', where the function levels off at 1.
    Returns
    -------
    y : 1d array
        S-function.
    Notes
    -----
    Named such because of its S-like shape.
    """
    assert a <= b, 'a <= b is required.'
    y = np.ones(len(x))
    idx = x <= a
    y[idx] = 0

    idx = np.logical_and(a <= x, x <= (a + b) / 2.)
    y[idx] = 2. * ((x[idx] - a) / (b - a)) ** 2.

    idx = np.logical_and((a + b) / 2. <= x, x <= b)
    y[idx] = 1 - 2. * ((x[idx] - b) / (b - a)) ** 2.

    return y
