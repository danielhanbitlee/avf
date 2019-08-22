from flask import Markup
import pandas as pd

from fuzzyAVF import fuzzy_smf, get_fuzzy_bins 

def color_by_unique_vals(series: pd.Series, col_idx: int):
    # get distinct values
    unique = sorted(series.unique())
    nunique = len(unique)
    if nunique == 1:
        return Markup(f"""
        if (aData[{col_idx + 1}] == {round(unique[0], 6)})
        {{
        $(nRow).find('td:eq({col_idx})').css('background-color', 'green');
        }}
        """.replace("\n", ""))
    if nunique == 2:
        return Markup(f"""
        if (aData[{col_idx + 1}] == {round(unique[0], 6)})
        {{
        $(nRow).find('td:eq({col_idx})').css('background-color', 'yellow');
        }}
        if (aData[{col_idx + 1}] == {round(unique[1], 6)})
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


def color_by_count_or_pct(series: pd.Series, method: str, col_idx: int, red_bin=None, yellow_bin=None):
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
        red = round(series.sort_values().values[int(round(red_bin, 0)) - 1], 6)
        yellow = round(series.sort_values().values[int(round(red_bin + yellow_bin, 0)) - 1], 6)
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

    elif method == "Continuous":
        red_pct = round(series.quantile(q=red_bin / 100), 6)
        yellow_pct = round(series.quantile(q=(red_bin + yellow_bin) / 100), 6)
        return Markup(f"""
                if (aData[{col_idx + 1}] > {yellow_pct})
                {{
                $(nRow).find('td:eq({col_idx})').css('background-color', '#089000');
                }}
                if ((aData[{col_idx + 1}] > {red_pct}) && (aData[{col_idx + 1}] <= {yellow_pct}))
                {{
                $(nRow).find('td:eq({col_idx})').css('background-color', '#1fc600');
                }}
                if (aData[{col_idx + 1}] <= {red_pct})
                {{
                $(nRow).find('td:eq({col_idx})').css('background-color', '#0eff00');
                }}
                """.replace("\n", ""))

    elif method == "NAVF":
        mean = series.mean()
        sd = series.std()
        red = round(mean - 3 * sd, 6)
        yellow = round(mean - 2 * sd, 6)

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

    elif method == "fuzzy AVF":
        y = fuzzy_smf(series)
        red, yellow = get_fuzzy_bins(series, y, red_bin, yellow_bin)
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

    else:
        return ""


def color_data_fn(series: pd.Series, col_idx):
    """
    Color cells for data table
    :param series:
    :param col_idx:
    :return:
    """
    # distinct colors
    colors = ['#F0FFF0', '#FFE4E1', '#F0E68C', '#ADFF2F', '#7FFF00', '#C0C0C0', '#EEE8AA', '#B0C4DE', '#00FF00', '#228B22', '#FFFF00', '#90EE90', '#483D8B', '#6495ED', '#3CB371', '#FFB6C1', '#EE82EE', '#008B8B', '#00FFFF', '#0000CD', '#4169E1', '#800080', '#40E0D0', '#800000', '#000080', '#FAFAD2', '#778899', '#FFF8DC', '#FF7F50', '#DAA520']
    # get distinct values
    unique_values = series.unique()
    color_js = ""
    for i, unique in enumerate(unique_values):
        color_js += f"""
		    var cellValue = aData[{col_idx + 1}].split('&gt;').join('>').split('&lt;').join('<')
                    if (cellValue == '{unique}')
                    {{
                    $(nRow).find('td:eq({col_idx})').css('background-color', '{colors[i]}');
                    }}
                    """
    return Markup(color_js)


def color_avf_data_fn(avf_data, form=None, parameter_dict=None):
    """
    Generates javascript to color data table cells
    """ 
    color_avf_data = ""

    # add function to color the cells
    for col in avf_data:
        if col != "avf":
            avf_data[col].quantile(q=.33)
            color_avf_data += color_by_unique_vals(avf_data[col],
                                                   int(avf_data.columns.get_loc(col)))

    if form:
        color_method = form.color_method.data
        red_bin = form.red_bin.data
        yellow_bin = form.yellow_bin.data

    else:
        color_method = "Percentile"
        red_bin = 33
        yellow_bin = 33
    try:
        if color_method in ["NAVF", "None"]:
            color_avf_data += color_by_count_or_pct(avf_data['avf'], method=color_method,
                                                    col_idx=int(avf_data.columns.get_loc('avf')))
                                                    
        else:
             color_avf_data += color_by_count_or_pct(avf_data['avf'], method=color_method,
                                                    col_idx=int(avf_data.columns.get_loc('avf')),
                                                    red_bin=float(red_bin),
                                                    yellow_bin=float(yellow_bin))
   

    except ValueError as e:
        color_avf_data += color_by_count_or_pct(avf_data['avf'], method=color_method,
    	                                        col_idx=int(avf_data.columns.get_loc('avf')),
    	                                        red_bin=float(red_bin),
    	                                        yellow_bin=float(yellow_bin))
        if parameter_dict:	
            parameter_dict['error_messages'].append("Percentiles should all be in the interval [0, 100].")

    return color_avf_data, parameter_dict

