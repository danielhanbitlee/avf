import numpy as np
import pandas as pd

from sklearn.preprocessing import StandardScaler

from flask import Flask, render_template, request
from wtforms import SelectField, FormField, FieldList

from avf import calc_avf, count_freq_for_cat, map_freq_to_value, convert_data_to_avf
from data_wrangling import convert_num_to_obj, convert_col_to_cat, convert_num_to_obj_columnwise
from color_cells import color_by_unique_vals, color_by_count_or_pct, color_data_fn, color_avf_data_fn
from js_generator import dynamic_selector_script
from infoform import InfoForm, VarForm, DataVisForm
from dataVis import dataVis

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

color_data = ""

for i, col in enumerate(pd_data):
    if col in cat_col:
        color_data += color_data_fn(pd_data[col], i)
    else:
        color_data += color_by_count_or_pct(pd_data[col], 'Continuous', i, 33, 33) 

num_vars = len(pd_data.columns)


@app.route('/', methods=['GET', 'POST'])
def index():

    class LocalForm(VarForm):
        pass


    LocalForm.variables = FieldList(FormField(InfoForm), min_entries=num_vars, max_entries=num_vars)

    form = LocalForm()

    data_copy = pd_data.copy()

    parameter_dict = dict(var_type=list(), bin_method=list(), bin_number=list(), error_messages=list())

    for i, col in enumerate(data_copy.columns):
        if col not in cat_col:
            parameter_dict['var_type'].append('numeric')
            form.variables[i].bin_method.choices = [('Equal Width Discretization',
                                                     'Equal Width Discretization'),
                                                    ('Equal Frequency Discretization',
                                                     'Equal Frequency Discretization')]
            max_bins = len(data_copy[col].unique())

            form.variables[i].bin_number.choices = [(i, i) for i in range(1, max_bins)]

            parameter_dict['bin_method'].append('Equal Width Discretization')
            parameter_dict['bin_number'].append(10)
            data_copy[col] = convert_num_to_obj_columnwise(series=data_copy[col],
                                                           discretization=parameter_dict['bin_method'][i],
                                                           nbins=int(parameter_dict['bin_number'][i]))
        else:
            parameter_dict['bin_method'].append(None)
            parameter_dict['bin_number'].append(None)
            parameter_dict['var_type'].append('categorical')


    # convert raw data to avf 
    avf_data, counts_dict = convert_data_to_avf(data_copy, True)    

    dataVisForm = DataVisForm()

    script, div = dataVis(dataVisForm, avf_data, counts_dict)

    color_avf_data, _ = color_avf_data_fn(avf_data)

    if request.method == 'POST':
        data_copy = pd_data.copy()
        parameter_dict = dict(var_type=list(), bin_method=list(), bin_number=list(), error_messages=list())
        for i, data in enumerate(form.variables.data):
            parameter_dict['bin_method'].append(data['bin_method'])
            parameter_dict['bin_number'].append(data['bin_number'])
        for i, col in enumerate(data_copy.columns):
            if form.variables[i].data['include_var'] == 'no':
                parameter_dict['bin_method'].append(form.variables[i].data['bin_method'])
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

        # convert raw data to avf 
        avf_data, counts_dict = convert_data_to_avf(data_copy, False)    

        # standardize 
        for i, col in enumerate(avf_data.columns):
            if form.variables[i].data['standardize'] == 'yes':
                scaler = StandardScaler()
                avf_data[col] = scaler.fit_transform(avf_data[[col]])

        avf_data['avf'] = avf_data.apply(np.sum, axis=1) / len(avf_data.columns)

        script, div = dataVis(dataVisForm, avf_data, counts_dict)

        color_avf_data, parameter_dict = color_avf_data_fn(avf_data, form, parameter_dict)

        if form.color_method.data == "NAVF":
            form.red_bin.data = None
            form.yellow_bin.data = None 

    return render_template('index.html',
                           data=pd_data.to_html(table_id="data"),
                           avf_data=avf_data.to_html(table_id='avf_data'),
                           variables=pd_data.columns,
                           form=form, parameter_dict=parameter_dict,
                           color_avf_data=color_avf_data,
                           color_data=color_data, 
                           script=script, 
                           div=div, avf_col_names=avf_data.columns, dataVisForm=dataVisForm)


if __name__ == '__main__':
    app.run(debug=True)

