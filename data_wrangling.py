import numpy as np
import pandas as pd


# convert numeric columns to categorical
# def convert_num_to_obj(df: pd.core.frame.DataFrame, numeric_cols: list, discretization: str, nbins: int):
def convert_num_to_obj(df: pd.core.frame.DataFrame, numeric_cols: list):

    """
    Convert numeric columns to categorical columns
    :param df: dataframe with raw data
    :param numeric_cols: column names of numeric columns
    :return pandas dataframe with numeric columns converted
    """
    df_with_converted_cols = pd.DataFrame()
    for col in df:
        if col in numeric_cols:
            df_with_converted_cols[col] = pd.cut(df[col], bins=10,
                                                 include_lowest=True).astype(str).astype('category')
        else:
            df_with_converted_cols[col] = df[col]
    return df_with_converted_cols


def convert_col_to_cat(df: pd.core.frame.DataFrame, cat_col: list):
    """Convert categorical columns to type 'category'"""
    df_with_cat = pd.DataFrame()
    for col in df:
        if col in cat_col:
            df_with_cat[col] = df[col].astype('category')
        else:
            df_with_cat[col] = df[col]
    return df_with_cat


# convert numeric column to categorical
def convert_num_to_obj_columnwise(series: pd.Series, discretization: str, nbins: int):
    """
    Convert numeric columns to categorical columns
    :param series: contains numeric raw data
    :param discretization: "equal_width", "equal_freq"
    :param nbins: number of bins to divide the numeric columns by
    :return pandas series with numeric column converted
    """
    if discretization == 'Equal Width Discretization':
        try:
            return pd.cut(series, bins=nbins)
        except TypeError as e:
            print(e)
            return series
    return pd.qcut(series, q=nbins, duplicates='drop')

