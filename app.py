from flask import Flask, render_template, redirect, url_for, request, jsonify
from wtforms import (StringField, BooleanField, DateTimeField,
                     RadioField,SelectField,TextField,
                     TextAreaField,SubmitField, FormField, FieldList, Form)

import numpy as np
import pandas as pd

from werkzeug import ImmutableMultiDict
from infoform import InfoForm, VarForm

from avf import calc_avf, count_freq_for_cat, map_freq_to_value
from data_wrangling import convert_num_to_obj, convert_col_to_cat, convert_num_to_obj_columnwise
from color_cells import color_by_unique_vals, color_avf, color_data_fn
from js_generator import dynamic_selector_script
import pprint


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
        print(col)
        color_data += color_data_fn(pd_data[col], i)

    class LocalForm(VarForm):
        pass

    LocalForm.variables = FieldList(FormField(InfoForm), min_entries=num_vars, max_entries=num_vars)
    form = LocalForm()

    parameter_dict = False
    data_copy = pd_data.copy()

    # convert numeric columns to object columns
    num_obj_data = convert_num_to_obj(pd_data, num_col)

    # convert object columns to categorical dtypes
    num_obj_data = convert_col_to_cat(num_obj_data, num_obj_data.columns)

    counts_dict = count_freq_for_cat(num_obj_data)

    avf_data = map_freq_to_value(num_obj_data, counts_dict)

    avf_data['avf'] = avf_data.apply(np.sum, axis=1) / len(avf_data.columns)

    js_selector_script = ""

    for i, col in enumerate(avf_data):
        js_selector_script += dynamic_selector_script(avf_data[col], i)

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
    color_avf_data += color_avf(avf_data['avf'], method=avf_form_dict['color_method'],
                              col_idx=int(avf_data.columns.get_loc('avf')),
                              red_bin=int(avf_form_dict['red_bin']),
                              yellow_bin=int(avf_form_dict['yellow_bin']))
    # if form.validate_on_submit():
    if request.method == 'POST':
        parameter_dict = dict(var_type=list(), bin_method=list(), bin_number=list(), error_messages=list())
        for i, data in enumerate(form.variables.data):
            parameter_dict['var_type'].append(data['var_type'])
            parameter_dict['bin_method'].append(data['bin_method'])
            parameter_dict['bin_number'].append(data['bin_number'])
        for i, col in enumerate(data_copy.columns):

            if parameter_dict['var_type'][i] == 'numeric':
                if col not in cat_col:
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
                    parameter_dict['error_messages'].append(f"Cannot convert categorical column '{col}' to numeric")

                    # this code updates the form variable to categorical. however, "categorical" is not necessary.
                    # not sure exactly how this works
                    form.variables[i].process(ImmutableMultiDict(
                        [('var_type', 'categorical')]
                    ))

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
        color_avf_data += color_avf(avf_data['avf'], method=avf_form_dict['color_method'],
                                  col_idx=int(avf_data.columns.get_loc('avf')),
                                  red_bin=int(avf_form_dict['red_bin']),
                                  yellow_bin=int(avf_form_dict['yellow_bin']))

    return render_template('index.html',
                           data=pd_data.to_html(table_id="data"),
                           avf_data=avf_data.to_html(table_id='avf_data'),
                           variables=num_obj_data.columns,
                           form=form, parameter_dict=parameter_dict,
                           color_avf_data=color_avf_data,
                           js_selector_script=js_selector_script,
                           color_data=color_data)


if __name__ == '__main__':
    app.run(debug=True)
