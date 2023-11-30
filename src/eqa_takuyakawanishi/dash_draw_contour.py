import datetime
from dateutil.relativedelta import relativedelta
from dash import Dash, dcc, dash_table, html, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pandas as pd
import scipy.stats
import src.eqa_takuyakawanishi.eqa as eqa
import dashfiles.layouts.fig_template as fig_template


################################################################################
#  Global Constants
################################################################################

DATABASE_START_DATE = '19190101'
DATABASE_END_DATE = '20191231'
DIR_DATA = '../../data/stationwise_fine_old_until_2019/'
FILE2READ_META = '../../intermediates/organized_codes_pre_02.csv'


################################################################################
#  Utility
################################################################################

def round_to_k(x, k):
    return round(x, -int(np.floor(np.log10(abs(x)))) - 1 + k)


def select_station(init_station):
    str_init_station = str(init_station)
    output = html.Div([
        html.H5(['Station Code (primary)']),
        dcc.Input(id='station', type='text', value=str_init_station,
                  style={'width': '40%'}),
        # eval(sid),
        html.Button(id='submit-button-state', n_clicks=0, children='Submit'),
        dcc.Store(id='station-data'),
        html.Div(id='station-data-msg'),
    ])
    return output


################################################################################
#
#  Layout
#
################################################################################


meta = pd.read_csv(FILE2READ_META)
cff = fig_template.FigSettings()
cfd = fig_template.DashSettings()
cfe = eqa.Settings()
# cfs = Settings()
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.layout = dbc.Container([
    cfd.navbar,
    dbc.Container([
        dbc.Row([
            dbc.Col([
                dcc.Store(id='numbers-under-conditions'),
                dcc.Store(id='station-meta'),
                dcc.Store(id='available-periods'),
                dcc.Store(id='set-period'),
                dcc.Store(id='set-period_1'),
                dcc.Store(id='set-period_2'),
                dcc.Store(id='summary'),
                #
                html.Br(),
                html.H4("Settings"),
                # select_station(5510100),
                # html.Div(id="stations-addresses"),
                # html.Div(id="stations-periods"),
                # html.Br(),
                html.H5("Setting the period"),
                html.H6("Primary plot"),
                cfd.select_date_from(1996, 4, 1, 1919, 2020),
                cfd.select_date_to(2019, 12, 31, 1919, 2020),
                # # html.Br(),
                html.H6("Choose stations experienced intensity of"),
                dcc.RadioItems(id="require-occurrence-of-intensity",
                    options=[3, 4, 5],
                    value=4,
                    inputStyle={'margin-right': '4px', 'margin-left': '4px',
                                'display': 'inline-block'}),
                html.H6("Choose stations having records more than or equal to"),
                html.Div([
                    dcc.Input(
                        id="require-duration-of", value=10,
                        style={'display': 'inline-block', 'width': '20%'}),
                    html.Div(
                        [html.P("years")],
                        style={'display': 'inline-block', 'width': '35%',
                               'margin-left': '1rem'}),
                ]),
                html.Button('Submit', id="submit-all", n_clicks=0),

            ], width={'size': 10}, sm=8, md=6, lg=4, xxl=3
            ),
            dbc.Col([
                html.Br(),
                html.H4("Intensity-Frequency"),
            ], width={'size': 12}, lg=8, xxl=9)
        ]),
    ], fluid=False)
], style=cfd.global_style, fluid=True)


################################################################################
#  Callbacks
################################################################################


@app.callback(
    Output('set-period', 'data'),
    Input('start-year_0', 'value'),
    Input('start-month_0', 'value'),
    Input('start-day_0', 'value'),
    Input('end-year_0', 'value'),
    Input('end-month_0', 'value'),
    Input('end-day_0', 'value')
)
def setting_the_analysis_period(sy, sm, sd, ey, em, ed):
    analysis_from = str(sy) + '-' + str(sm).zfill(2) + '-' + str(sd).zfill(2)
    analysis_to = str(ey) + '-' + str(em).zfill(2) + '-' + str(ed).zfill(2)
    period_analyze_dict = {"set_from": analysis_from, "set_to": analysis_to}
    return period_analyze_dict


# @app.callback(
#     Output("numbers-under-conditions", "data"),
#     Input('set-period', 'data'),
#     Input("submit-all", "n_clicks"),
#     State("require-occurrence-of-intensity", "value"),
#     State("require-duration-of", "value"),
# )
# def get_subset_of_stations(set_dict, _, required_int, required_duration):
#     conditions_dict = {"intensity": required_int, "duration": required_duration}
#     res = eqa.screening_stations(
#         meta, conditions_dict, set_dict, dir_data=DIR_DATA)
#     print(res)
#     meta_res = pd.concat([meta, res], axis=1)
#     meta_res_dict = meta_res.to_dict("records")
#     return meta_res_dict


if __name__ == '__main__':
    app.run_server(debug=True, port=8060)
