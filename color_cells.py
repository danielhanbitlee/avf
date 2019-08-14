from flask import Markup
import pandas as pd


def color_by_unique_vals(series: pd.Series, col_idx: int):
    # get distinct values
    unique = sorted(series.unique())
    nunique = len(unique)
    if nunique == 1:
        return Markup(f"""
        if (aData[{col_idx + 1}] == {unique[0]})
        {{
        $(nRow).find('td:eq({col_idx})').css('background-color', 'green');
        }}
        """.replace("\n", ""))
    if nunique == 2:
        return Markup(f"""
        if (aData[{col_idx + 1}] == {unique[0]})
        {{
        $(nRow).find('td:eq({col_idx})').css('background-color', 'yellow');
        }}
        if (aData[{col_idx + 1}] == {unique[1]})
        {{
        $(nRow).find('td:eq({col_idx})').css('background-color', 'green');
        }}
        """.replace("\n", ""))
    else:
        pct_33 = unique[int(nunique / 3)]
        pct_66 = unique[int(nunique / 3) * 2]
        return Markup(f"""
        if (aData[{col_idx + 1}] > {pct_66})
        {{
        $(nRow).find('td:eq({col_idx})').css('background-color', 'green');
        }}
        if ((aData[{col_idx + 1}] > {pct_33}) && (aData[{col_idx + 1}] <= {pct_66}))
        {{
        $(nRow).find('td:eq({col_idx})').css('background-color', 'yellow');
        }}
        if (aData[{col_idx + 1}] <= {pct_33})
        {{
        $(nRow).find('td:eq({col_idx})').css('background-color', 'red');
        }}
        """.replace("\n", ""))


def color_avf(series: pd.Series, method: str, col_idx: int, red_bin: int, yellow_bin: int):
    if method == "Percentile":
        red_pct = round(series.quantile(q=red_bin / 100), 6)
        yellow_pct = round(series.quantile(q=(red_bin + yellow_bin) / 100), 6)
        return Markup(f"""
                if (aData[{col_idx + 1}] > {yellow_pct})
                {{
                $(nRow).find('td:eq({col_idx})').css('background-color', 'green');
                }}
                if ((aData[{col_idx + 1}] > {red_pct}) && (aData[{col_idx + 1}] <= {yellow_pct}))
                {{
                $(nRow).find('td:eq({col_idx})').css('background-color', 'yellow');
                }}
                if (aData[{col_idx + 1}] <= {red_pct})
                {{
                $(nRow).find('td:eq({col_idx})').css('background-color', 'red');
                }}
                """.replace("\n", ""))
    elif method == "Count":
        red = round(series.sort_values().values[red_bin - 1], 6)
        yellow = round(series.sort_values().values[red_bin + yellow_bin - 1], 6)
        return Markup(f"""
                if (aData[{col_idx + 1}] > {yellow})
                {{
                $(nRow).find('td:eq({col_idx})').css('background-color', 'green');
                }}
                if ((aData[{col_idx + 1}] > {red}) && (aData[{col_idx + 1}] <= {yellow}))
                {{
                $(nRow).find('td:eq({col_idx})').css('background-color', 'yellow');
                }}
                if (aData[{col_idx + 1}] <= {red})
                {{
                $(nRow).find('td:eq({col_idx})').css('background-color', 'red');
                }}
                """.replace("\n", ""))


def color_data_fn(series: pd.Series, col_idx):
    """
    Color cells for data table
    :param series:
    :param col_idx:
    :return:
    """
    # get distinct values
    unique_values = sorted(series.unique())
    color_js = ""
    for unique in unique_values:
        color_js += f"""
                    if (aData[{col_idx + 1}] == '{unique}')
                    {{
                    $(nRow).find('td:eq({col_idx})').css('background-color', 'green');
                    }}
                    """
    return Markup(color_js)
