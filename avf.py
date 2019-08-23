"""Function calc_avf() that calculates attribute value frequency"""

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.types import DoubleType
from pyspark.sql.functions import count, udf, array
from pyspark.sql.window import Window
import numpy as np
import pandas as pd

from sklearn.preprocessing import MinMaxScaler, StandardScaler
from data_wrangling import convert_col_to_cat


def calc_avf(data:DataFrame, cat_col: list):
    """
    Calculate attribute value frequency
    :param data: Spark dataframe
    :param cat_col: list of categorical columns
    :return Spark dataframe with avf column added
    """
    for column in cat_col:
        # get frequency for each column
        data = data.withColumn(column, count(column).over(Window.partitionBy(column)))

    # get average of frequencies for each row
    avg_cols = udf(lambda array: sum(array)/len(array), DoubleType())

    data = data.withColumn("avf", avg_cols(array(*cat_col)))

    return data


# below is converting all columns at once
def count_freq_for_cat(df):
    counts_dict = dict()
    for col in df.select_dtypes(['category']):
        counts_dict[col] = df[col].value_counts().to_dict()
    return counts_dict


def map_freq_to_value(df, counts_dict):
    df_with_freq = pd.DataFrame()
    for col in df:
        if str(df[col].dtypes) == 'category':
            df_with_freq[col] = df[col].map(counts_dict[col]).astype('int64')
        else:
            df_with_freq[col] = df[col]
    return df_with_freq


def convert_data_to_avf(df, add_avf_col: bool):
    # convert object columns to categorical dtypes
    num_obj_data = convert_col_to_cat(df, df.columns)
    # get counts for each category as dictionary 
    counts_dict = count_freq_for_cat(num_obj_data)
    # create df of frequencies: avf_data
    avf_data = map_freq_to_value(num_obj_data, counts_dict)
    if add_avf_col:
        # add avf column
        avf_data['avf'] = avf_data.apply(np.sum, axis=1) / len(avf_data.columns)
    return avf_data, counts_dict 


def convert_data_to_avf_columnwise(df: pd.DataFrame, form=None, var_idx_list=None):
    # convert raw data to avf columnwise
    counts_dict = dict()
    avf_data = pd.DataFrame()

    for i, col in enumerate(df):
       # get dictionary of value counts for column
       counts_dict[col] = df[col].value_counts().to_dict() 

       # map dictionary of value counts and create a new column avf_data[col]
       avf_data[col] = df[col].map(counts_dict[col]).astype('int64')

       if form:
           if form.variables[var_idx_list[i]].data['normalize'] != 'none':
               if form.variables[var_idx_list[i]].data['normalize'] != 'standardize':
                   scaler = StandardScaler()
               elif form.variables[var_idx_list[i]].data['normalize'] != 'min-max scaler':
                   scaler = MinMaxScaler()

               # scale the avf_data[col] column
               scaled_freq_ct = scaler.fit_transform(avf_data[[col]])
               scaled_dict = dict(zip(avf_data[col], scaled_freq_ct))

               avf_data[col] = scaled_freq_ct

               categories_to_delete = list()

               for category_name, freq_ct in counts_dict[col].items():

                   try:
                       scaled_freq_ct = scaled_dict[freq_ct]
                       counts_dict[col][category_name] = scaled_freq_ct

                   except KeyError:
                       categories_to_delete.append(category_name)

               if categories_to_delete:
                   for cat in categories_to_delete:
                       del counts_dict[col][cat]

    return avf_data, counts_dict

