from flask import Markup
import pandas as pd


def dynamic_selector_script(series: pd.Series, idx: int):
    max_bins = len(series.unique())
    bin_script = ""

    for i in range(1, max_bins + 1):
        bin_script += f"""optionHTML_bin_number += '<option value="{i}">{i}</option>';"""

    return Markup(f"""
        var var_type_select_{idx} = document.getElementById('variables-{idx}-var_type');
        var bin_method_select_{idx} = document.getElementById('variables-{idx}-bin_method');
        var bin_number_select_{idx} = document.getElementById('variables-{idx}-bin_number');

        var_type_select_{idx}.onchange = function() {{
            var_type = var_type_select_{idx}.value;
            if (var_type == "numeric") {{

                var optionHTML_bin_method = '';
                var optionHTML_bin_number = '';

                optionHTML_bin_method += '<option value="Equal Width Discretization">Equal Width Discretization</option>';
                optionHTML_bin_method += '<option value="Equal Frequency Discretization">Equal Frequency Discretization</option>';
                {bin_script}
                }}

                bin_method_select_{idx}.innerHTML = optionHTML_bin_method;
                bin_number_select_{idx}.innerHTML = optionHTML_bin_number;
            }}""")
