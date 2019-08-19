"""Function calc_avf() that calculates attribute value frequency"""

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.types import DoubleType
from pyspark.sql.functions import count, udf, array
from pyspark.sql.window import Window
import numpy as np
import pandas as pd

from data_wrangling import convert_col_to_cat


def calc_avf(data:DataFrame, cat_col: list):
    """
    Calculate attribute value frequency
    :param data: Spark dataframe
    :param cat_col: list of categorical columns
    :return Spark dataframe with avf column added
    """
    # spark = SparkSession.builder.getOrCreate()
    #
    # if path.endswith('csv'):
    #     # Read in the CSV
    #     data = spark.read.option("inferSchema", "True").csv(path, header=True)
    # else:
    #     # Read in the Parquet
    #     data = spark.read.parquet(*path)

    for column in cat_col:
        # get frequency for each column
        data = data.withColumn(column, count(column).over(Window.partitionBy(column)))

    # get average of frequencies for each row
    avg_cols = udf(lambda array: sum(array)/len(array), DoubleType())

    data = data.withColumn("avf", avg_cols(array(*cat_col)))

    return data


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

