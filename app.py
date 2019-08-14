from flask import Flask, render_template, redirect, url_for, request, jsonify
from wtforms import (StringField, BooleanField, DateTimeField,
                     RadioField,SelectField,TextField,
                     TextAreaField,SubmitField, FormField, FieldList, Form)

import numpy as np
import pandas as pd

from werkzeug import ImmutableMultiDict
from infoform import InfoForm, VarForm, DataVisForm

from avf import calc_avf, count_freq_for_cat, map_freq_to_value
from data_wrangling import convert_num_to_obj, convert_col_to_cat, convert_num_to_obj_columnwise
from color_cells import color_by_unique_vals, color_by_count_or_pct, color_data_fn
from js_generator import dynamic_selector_script
import pprint
from flask import Flask, render_template

from bokeh.plotting import figure
from bokeh.embed import components


pd_data = pd.read_csv('../anomaly_detection-master/data/predict_income.csv').iloc[:1000, ]
pd_data.drop(columns=['id', 'fnlwgt'], inplace=True)

# obtained from kaggle website
cat_col = ['workclass', 'education',
           'marital-status', 'occupation',
           'relationship',
           'race', 'sex',
           'native-country', 'income']

num_col = [col for col in pd_data.columns if col not in cat_col]

app = Flask(__name__)

app.config['SECRET_KEY'] = 'mysecretkey'


@app.route('/', methods=['GET', 'POST'])
def index():

    num_vars = len(pd_data.columns)


    color_data = ""

    for i, col in enumerate(pd_data):
        if col in cat_col:
            color_data += color_data_fn(pd_data[col], i)
        else:
            color_data += color_by_count_or_pct(pd_data[col], 'Continuous', i, 33, 33) 

    class LocalForm(VarForm):
        pass

    LocalForm.variables = FieldList(FormField(InfoForm), min_entries=num_vars, max_entries=num_vars)
    form = LocalForm()

    data_copy = pd_data.copy()

    parameter_dict = dict(var_type=list(), bin_method=list(), bin_number=list(), error_messages=list())

    for i, col in enumerate(data_copy.columns):
        # if parameter_dict['var_type'][i] != 'categorical':
        if col not in cat_col:
            parameter_dict['var_type'].append('numeric')
            form.variables[i].bin_method.choices = [('Equal Width Discretization',
                                                     'Equal Width Discretization'),
                                                    ('Equal Frequency Discretization',
                                                     'Equal Frequency Discretization')]
            max_bins = len(data_copy[col].unique())

            form.variables[i].bin_number.choices = [(i, i) for i in range(1, max_bins)]
            # form.variables[i].bin_number = 10

            parameter_dict['bin_method'].append('Equal Width Discretization')
            parameter_dict['bin_number'].append(10)
            data_copy[col] = convert_num_to_obj_columnwise(series=data_copy[col],
                                                           discretization=parameter_dict['bin_method'][i],
                                                           nbins=int(parameter_dict['bin_number'][i]))
        else:
            parameter_dict['bin_method'].append(None)
            parameter_dict['bin_number'].append(None)
            parameter_dict['var_type'].append('categorical')


    # convert object columns to categorical dtypes
    num_obj_data = convert_col_to_cat(data_copy, data_copy.columns)

    counts_dict = count_freq_for_cat(num_obj_data)

    avf_data = map_freq_to_value(num_obj_data, counts_dict)

    avf_data['avf'] = avf_data.apply(np.sum, axis=1) / len(avf_data.columns)

    dataVisForm = DataVisForm()

    dataVisForm.variable.choices = [(col, col) for col in avf_data.columns]

    js_selector_script = ""

    for i, col in enumerate(data_copy):
        js_selector_script += dynamic_selector_script(data_copy[col], i)

    color_avf_data = ""

    # add function to color the cells
    for col in avf_data:
        if col != "avf":
            avf_data[col].quantile(q=.33)
            color_avf_data += color_by_unique_vals(avf_data[col], int(avf_data.columns.get_loc(col)))

    # avf_form_dict is not necessary here
    avf_form_dict = dict()
    avf_form_dict['color_method'] = "Percentile"
    avf_form_dict['red_bin'] = 33
    avf_form_dict['yellow_bin'] = 33
    color_avf_data += color_by_count_or_pct(avf_data['avf'], method=avf_form_dict['color_method'],
                              col_idx=int(avf_data.columns.get_loc('avf')),
                              red_bin=int(avf_form_dict['red_bin']),
                              yellow_bin=int(avf_form_dict['yellow_bin']))

    # data visualization
    current_avf_col_name = request.args.get("avf_column_name")
    print(current_avf_col_name)
    if current_avf_col_name not in avf_data.columns:
        current_avf_col_name = avf_data.columns[0] 
    categories = [str(cat) for cat in counts_dict[current_avf_col_name].keys()]
    counts = list(counts_dict[current_avf_col_name].values())
    p = figure(x_range=categories, title=current_avf_col_name, toolbar_location=None, tools="pan,wheel_zoom,box_zoom,reset",
               sizing_mode='scale_width', height=200)
    p.vbar(x=categories, top=counts, width=0.9)
    p.xgrid.grid_line_color = None
    p.xaxis.major_label_text_font_size = "12pt"
    p.y_range.start = 0
    script, div = components(p) 

    # if form.validate_on_submit():
    if request.method == 'POST':
        data_copy = pd_data.copy()
        parameter_dict = dict(var_type=list(), bin_method=list(), bin_number=list(), error_messages=list())
        for i, data in enumerate(form.variables.data):
            parameter_dict['bin_method'].append(data['bin_method'])
            parameter_dict['bin_number'].append(data['bin_number'])
        for i, col in enumerate(data_copy.columns):
            if form.variables[i].data['include_var'] == 'no':
                parameter_dict['bin_method'].append(data['bin_method'])
                if col not in cat_col:
                    parameter_dict['var_type'].append('numeric')
                else:
                    parameter_dict['var_type'].append('categorical')
                parameter_dict['bin_number'].append(data['bin_number'])
                data_copy.drop(columns=col, inplace=True)
            elif col not in cat_col:
                parameter_dict['var_type'].append('numeric')
                form.variables[i].bin_method.choices = [('Equal Width Discretization',
                                                         'Equal Width Discretization'),
                                                        ('Equal Frequency Discretization',
                                                         'Equal Frequency Discretization')]
                max_bins = len(data_copy[col].unique())

                form.variables[i].bin_number.choices = [(i, i) for i in range(1, max_bins)]

                data_copy[col] = convert_num_to_obj_columnwise(series=data_copy[col],
                                                               discretization=parameter_dict['bin_method'][i],
                                                               nbins=int(parameter_dict['bin_number'][i]))
            else:
                parameter_dict['var_type'].append('categorical')


        # convert object columns to categorical dtypes
        num_obj_data = convert_col_to_cat(data_copy, data_copy.columns)

        counts_dict = count_freq_for_cat(num_obj_data)

        avf_data = map_freq_to_value(num_obj_data, counts_dict)

        avf_data['avf'] = avf_data.apply(np.sum, axis=1) / len(avf_data.columns)

        color_avf_data = ""

        # add function to color the cells
        for col in avf_data:
            if col != "avf":
                avf_data[col].quantile(q=.33)
                color_avf_data += color_by_unique_vals(avf_data[col], int(avf_data.columns.get_loc(col)))

        # avf_form_dict is not necessary here
        avf_form_dict = dict()
        avf_form_dict['color_method'] = form.color_method.data
        avf_form_dict['red_bin'] = form.red_bin.data
        avf_form_dict['yellow_bin'] = form.yellow_bin.data
        try:
            color_avf_data += color_by_count_or_pct(avf_data['avf'], method=avf_form_dict['color_method'],
                                      col_idx=int(avf_data.columns.get_loc('avf')),
                                      red_bin=float(avf_form_dict['red_bin']),
                                      yellow_bin=float(avf_form_dict['yellow_bin']))
        except ValueError as e:
            color_avf_data += color_by_count_or_pct(avf_data['avf'], method="None",
                                      col_idx=int(avf_data.columns.get_loc('avf')),
                                      red_bin=float(avf_form_dict['red_bin']),
                                      yellow_bin=float(avf_form_dict['yellow_bin']))
            parameter_dict['error_messages'].append("Percentiles should all be in the interval [0, 100].")

        # data visualization
        dataVisForm.variable.choices = [(col, col) for col in avf_data.columns]
        current_avf_col_name = dataVisForm.data['variable']
        print(current_avf_col_name)
        if current_avf_col_name not in avf_data.columns:
            current_avf_col_name = avf_data.columns[0] 
        if current_avf_col_name == 'avf':
            hist, edges = np.histogram(avf_data[current_avf_col_name])
            p = figure(plot_height = 200, sizing_mode='scale_width', title = 'Histogram of Attribute Value Frequency Values')
            p.quad(bottom=0, top=hist, left=edges[:-1],
                   right=edges[1:], fill_color="navy", line_color="white", alpha=0.5)
        else:
            categories = [str(cat) for cat in counts_dict[current_avf_col_name].keys()]
            counts = list(counts_dict[current_avf_col_name].values())
            p = figure(x_range=categories, title=current_avf_col_name, toolbar_location=None, tools="pan,wheel_zoom,box_zoom,reset",
                       sizing_mode='scale_width', height=200)
            p.vbar(x=categories, top=counts, width=0.9)
            p.xgrid.grid_line_color = None
            p.xaxis.major_label_text_font_size = "12pt"
            p.y_range.start = 0
        script, div = components(p) 

    return render_template('index.html',
                           data=pd_data.to_html(table_id="data"),
                           avf_data=avf_data.to_html(table_id='avf_data'),
                           variables=pd_data.columns,
                           form=form, parameter_dict=parameter_dict,
                           color_avf_data=color_avf_data,
                           js_selector_script=js_selector_script,
                           color_data=color_data, script=script, div=div, current_avf_col_name=current_avf_col_name, avf_col_names=avf_data.columns, dataVisForm=dataVisForm)


if __name__ == '__main__':
    app.run(debug=True)
