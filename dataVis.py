import numpy as np
from bokeh.plotting import figure
from bokeh.embed import components


def dataVis(dataVisForm, avf_data, counts_dict):
    # data visualization
    dataVisForm.variable.choices = [(col, col) for col in avf_data.columns]
    current_avf_col_name = dataVisForm.data['variable']
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
        # get min value
        p.y_range.start = min(avf_data[current_avf_col_name].min() * 1.1, 0) 
    return components(p)
     
