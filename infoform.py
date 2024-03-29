from flask import Flask, render_template, redirect, url_for, session, request
from flask_wtf import FlaskForm
from wtforms import (StringField, BooleanField, DateTimeField,
                     RadioField,SelectField,TextField,
                     TextAreaField,SubmitField, FormField, FieldList, Form)
from wtforms.validators import DataRequired


class InfoForm(Form):
    '''
    Mainly a way to go through many of the WTForms Fields.
    '''
    bin_method = SelectField(u'Bin Method:', choices=list())
    bin_number = SelectField(u'Number of Bins:', choices=list(), default=10)
    include_var = SelectField(u'Include Variable?',
                              choices=[('yes', 'yes'), ('no', 'no')],
                              default="yes")
    normalize = SelectField(u'Scale',
                              choices=[('standardize', 'standardize'),
                                       ('min-max scaler', 'min-max scaler'),
                                       ('none', 'none')],
                              default="none")
    

class VarForm(FlaskForm):

    variables = FieldList(FormField(InfoForm))
    color_method = SelectField(u'Color Method:',
                               choices=[('Count', 'Count'),
                                        ('Percentile', 'Percentile'),
                                        ('NAVF', 'NAVF'),
                                        ('fuzzy AVF', 'fuzzy AVF'),
                                        ('None', 'None')],
                               default='Percentile')
    red_bin = StringField(u'Red Bin:', default='33')
    yellow_bin = StringField(u'Yellow Bin:', default='33')
    all_variables = SelectField(u'Normalize:',
                                choices=[('standardize', 'standardize'),
                                         ('min-max scaler', 'min-max scaler'),
                                         ('none', 'none'),
                                         ('not applicable', 'not applicable')],
                                default="not applicable")


class DataVisForm(FlaskForm):

    variable = SelectField(u'Column Name:',
                           choices=list())

