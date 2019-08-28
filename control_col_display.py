from flask import Markup


def display_cols(ncols: int):
    displ_js = '{targets: [0], className: "all",},'
    for i in range(ncols): 
        displ_js += f'{{targets: [{i+1}], className: "all",}},'
    return Markup(displ_js)


def hide_cols(ncols: int):
    hide_js = ""
    for i in range(1, ncols + 1):
        hide_js += f'{{targets: [{-i}], className: "none",}},'
    return Markup(hide_js)


def show_hide_control_col(avf_col_number: int):
    return Markup(f"type: 'column', target: {avf_col_number+1}")
