from flask import Flask, render_template, redirect, url_for, session, request
from flask_wtf import FlaskForm
from wtforms import (StringField, BooleanField, DateTimeField,
                     RadioField,SelectField,TextField,
                     TextAreaField,SubmitField, FormField, FieldList, Form)
from wtforms.validators import DataRequired


class InfoForm(Form):
    '''
    This general class gets a lot of form about puppies.
    Mainly a way to go through many of the WTForms Fields.
    '''
    var_type = SelectField(u'Variable Type:',
                           choices=[('numeric', 'numeric'), ('categorical', 'categorical'),
                                    ('none', 'none')], default='categorical')
    bin_method = SelectField(u'Bin Method:', choices=list())
    bin_number = SelectField(u'Number of Bins:', choices=list())
    # bin_method = SelectField(u'Bin Method:',
    #                          choices=[('Equal Width Discretization', 'Equal Width Discretization'),
    #                                   ('Equal Frequency Discretization', 'Equal Frequency Discretization')],
    #                          default='Equal Width Discretization')
    # bin_number = SelectField(u'Number of Bins:',
    #                          choices=[('m', 'm'),
    #                                   ('1', '1'),
    #                                   ('2', '2'),
    #                                   ('3', '3'),
    #                                   ('4', '4'),
    #                                   ('5', '5'),
    #                                   ('6', '6'),
    #                                   ('7', '7'),
    #                                   ('8', '8'),
    #                                   ('9', '9'),
    #                                   ('10', '10')],
    #                          default='10')


class VarForm(FlaskForm):

    variables = FieldList(FormField(InfoForm))
    color_method = SelectField(u'Color Method:',
                               choices=[('Count', 'Count'), ('Percentile', 'Percentile'),
                                        ('none', 'none')], default='Percentile')
    red_bin = StringField(u'Red Bin:', default='33')
    yellow_bin = StringField(u'Yellow Bin:', default='33')

