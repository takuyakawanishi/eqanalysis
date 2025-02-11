import datetime
from dateutil.relativedelta import relativedelta
from dash import Dash, dcc, dash_table, html, Input, Output, State
from dash.dash_table.Format import Format, Scheme, Trim
from collections import OrderedDict
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pandas as pd
import scipy.stats
import eqa
import sys
sys.path.append("./")
import eqanalysis.dashfiles.layouts.fig_template as fig_template


################################################################################
#  Global Constants and Variables
################################################################################

DATABASE_START_DATE = '19190101'
DATABASE_END_DATE = '20191231'
# DIR_DATA = '../../data/stationwise_fine_old_until_2019/'
# FILE2READ_META = '../../data/code_p_df.csv'
DIR_DATA = 'eqanalysis/data_2024/stationwise_2021/'
FILE2READ_META = 'eqanalysis/data_2024/code_p_20231205_df.csv'
FILE2READ_ORG = "eqanalysis/data_2024/intermediates/organized_code_2024_04.csv"
cud_orange = "#e69900"  # (0.9, 0.6, 0)
cud_skyblue = "#59b3e6"  # (.35, .7, .9)
cud_green = "#009980"  # (0, .6, .5)
cud_blue = "#0073b3"  # (0, .45, .7)
cudr_base_pink_ap3 = (255/255, 202/255, 191/255, .3)
cudr_base_cream_ap3 = (255/255, 255/255, 128/255, .3)
cudr_base_beige = (255/255, 202/255, 128/255)
cudr_base_yellowgreen_ap3 = (216/255, 242/255, 85/255, .3)
curd_base_brightblue_ap3 = (191/255, 228/255, 255/255, .3)


################################################################################
#  Utility
################################################################################

def round_to_k(x, k):
    try:
        return round(x, -int(np.floor(np.log10(abs(x)))) - 1 + k)
    except Exception as ex:
        print(ex)
        return np.nan


################################################################################
#  Layout functions
################################################################################

class Settings:

    def __init__(self):
        self.reg_int_occ_low = 2
        self.reg_int_occ_upp = 4


def select_station(init_station):
    str_init_station = str(init_station)
    output = html.Div([
        html.H6(['Station Code']),
        dcc.Input(id='station', type='text', value=str_init_station,
                  style={'width': '40%'}),
        # eval(sid),
        html.Button(id='select-station-submit-button-state', n_clicks=0,
                    children='Submit'),
        # dcc.Store(id='available-period'),
        html.Div(id='station-data-msg'),
        html.Div([
            dash_table.DataTable(
                id="available-period",
            ),
        ], style={"margin-top": "-.5rem", "margin-bottom":".5rem",
                  "padding-right": '12px'})
    ])
    return output


def set_datetime(idx):
    data_init = [["From", 1996, 4, 1, 12, 0, 0 ],
          ["to", 2021, 12, 31, 23, 59, 59]]
    columns=['attrib', 'yr', 'mo', 'day', 'hr', 'min', 'sec']
    df = pd.DataFrame(data_init, columns=columns)
    output = html.Div([
        html.H6(['Setting Period']),
        html.Div([
            dash_table.DataTable(
                editable=True,
                id="set-datetime_" + str(idx),
                columns=[{'name': i, 'id': i} for i in df.columns],
                data=df.to_dict("records"),
                persistence=True,
                persistence_type='memory',
                persisted_props = ['columns.name', 'data'],
                style_cell={
                    'width': '12%'.format(len(df.columns)),
                },
                style_cell_conditional=[
                    {'if': {'column_id': 'attrib'},'width': '15%'},
                    {'if': {'column_id': 'yr'},'width': '15%'},
                ],            
            ),    
        ], style={'padding-right': '12px'}),
        html.Button(id='set-period-submit-button-state', n_clicks=0,
            children='Submit'),
    ])
    return output


def select_fitting_intensities(init_label, value):
    # Select if draw regression or not
    output = html.Div([
        html.H6(['Draw regression for corrected?']),
        html.Div([
            dcc.RadioItems(
                options=[{'label': 'Yes', 'value': 'Yes'},
                            {'label': 'No', 'value': 'No'}],
                value=init_label,
                id='draw-or-not-reg-corrected',
                inline=True,
                inputStyle={'margin-right': '4px', 'margin-left': '4px'})
        ], style={'display': 'flex', 'width': '50%'}),
        html.P(['The lowest intensity to fit']),
        html.Div([
            dcc.Dropdown([1, 2, 3], value, id='seleft-fit-intensity-low'),
            html.Button(id='button-select-fit-intensity', n_clicks=0,
                children='Submit', style={'width': '40%'}),
        ], style={'display': 'flex', 'margin-top': '-.5rem',
                  'margin-bottom': '.5rem'})
    ])
    return output


def set_range_fit_intervals(idx, low, upp, factor_user):
    data = [['Range (days)', low, upp]]
    df = pd.DataFrame(data, columns=['Your fitting', 'low', 'upp'])
    if factor_user is None:
        dis = True
    else:
        dis = False
    output = html.Div([
        html.Div([
            html.Div([
                dash_table.DataTable(
                    editable=True,
                    id='interval-fit-range_' + str(idx),
                    columns=[
                        dict(id='Your fitting', name='Your fitting'),
                        dict(id='low', name='low', type='numeric', 
                            format=Format(precision=0, scheme=Scheme.fixed)),
                        dict(id='upp', name='upp', type='numeric', 
                            format=Format(precision=0, scheme=Scheme.fixed))
                    ],
                    data=df.to_dict("records"),
                    persistence=True,
                    persistence_type='memory',
                    persisted_props = ['columns.name', 'data'],
                    style_cell_conditional=[
                        {'if': {'column_id': 'Your fitting'},'width': '35%'},
                    ]
                ),
            ], style={
                'display': 'inline-block', 'width': '80%', 
                'vertical-align': 'bottom'}
            ),
            html.Button(id='button-interval-fit-range_' + str(idx), n_clicks=0,
                children='Fit', 
                style={
                    'width':'20%', 'display': 'inline-block',
                    'vertical-align': 'bottom'}
            )
            # 'button-interval-fit-range_1'
        ]),
        html.Div([
            html.Div(
                "Your Factor", 
                style={'display': 'inline-block', 'width':'35%',
                    'vertical-align': 'bottom'}
            ),
            dcc.Input(id='factor-user-temp_' + str(idx), type='number', 
                      value=factor_user,
                    style={'width': '45%', 'display': 'inline-block'},
                    debounce=True,
            ),
            # 'button-use-factor-user_1'
            html.Button(id='button-use-factor-user_' + str(idx), n_clicks=0,
                children='Use', 
                style={
                    'width':'20%', 'display': 'inline-block',
                    'vertical-align': 'bottom'},
                disabled=dis
            )  
        ])
    ], style={'width': '312px', 'margin': '2px', 'padding-right': '24px'})
    return output    


# def display_calculated_factor_and_ask_if_it_be_used(idx):
#     output = html.Div([
#         html.P(
#             ["Factor = "], 
#             style={'display': 'inline-block', 'vertical-align': 'bottom',
#                    'width': '30%'}
#         ),
#         html.P(
#             id='factor-intensity_' + str(idx),
#             style={'display': 'inline-block', 'vertical-align': 'bottom',
#                    'width': '40%'}
#         ),
#         html.Button(id='button-factor-intensity_' + str(idx), n_clicks=0,
#             children='Submit', 
#             style={
#                 'width':'30%', 'display': 'inline-block',
#                 'vertical-align': 'bottom'}
#         ),
#     ])

# def set_datetime(msg, n, init_dt):
#     init_y = int(init_dt[:4])
#     init_m = int(init_dt[5:7])
#     init_d = int(init_dt[8:10])
#     init_h = int(init_dt[11:13])
#     init_n = int(init_dt[14:16])
#     init_s = int(init_dt[17:19])
#     idy = "set-year_" + str(n)
#     idm = "set-month_" + str(n)
#     idd = "set-day_" + str(n)
#     idh = "set_hour_" + str(n)
#     idn = "set_minute_" + str(n)
#     ids = "set_second_" + str(n)
#     output = html.Div([
#         html.P([msg], style={'display': 'inline-block', 'width': '15%'}),
#         html.Div([
#             dcc.Dropdown(
#                 id=idy, options=[
#                     {'label': x, 'value': x} for x in range(1919, 2100)],
#                 value=init_y)
#         ], style={'display': 'inline-block', 'width': '35%'}),
#         html.Div([
#             dcc.Dropdown(
#                 id=idm, options=[
#                     {'label': x, 'value': x} for x in range(1, 13)],
#                 value=init_m)
#         ], style={'display': 'inline-block', 'width': '25%'}),
#         html.Div([
#             dcc.Dropdown(
#                 id=idd,
#                 options=[{'label': x, 'value': x} for x in range(1, 32)],
#                 value=init_d)
#         ], style={'display': 'inline-block', 'max-width': '25%'}),
#         html.Br(),
#         html.P([''], style={'display': 'inline-block', 'width': '15%'}),
#         html.Div([
#             dcc.Dropdown(
#                 id=idh, options=[
#                     {'label': x, 'value': x} for x in range(0, 13)],
#                 value=init_h)
#         ], style={'display': 'inline-block', 'width': '35%'}),
#         html.Div([
#             dcc.Dropdown(
#                 id=idn, options=[
#                     {'label': x, 'value': x} for x in range(0, 61)],
#                 value=init_n)
#         ], style={'display': 'inline-block', 'width': '25%'}),
#         html.Div([
#             dcc.Dropdown(
#                 id=ids,
#                 options=[{'label': x, 'value': x} for x in range(0, 61)],
#                 value=init_s)
#         ], style={'display': 'inline-block', 'max-width': '25%'}),
#     ])
#     return output



def set_range_regression_intensity_occurrence(val_0, val_1, low, upp):
    output = html.Div([
        html.Div(
            [html.P("Intensity from")],
            style={'width': '40%', 'display': 'inline-block'}),
        html.Div([
            dcc.Dropdown(
                id='intensity-from',
                options=[{'label': x, 'value': x} for x in range(low, upp)],
                value=val_0)
        ], style={'width': '25%', 'display': 'inline-block'}),
        html.Div(
            [html.P(" to ")],
            style={'width': '8%', 'display': 'inline-block',
                   'margin-left': '2%', 'margin-right': 'auto'}),
        html.Div([
            dcc.Dropdown(
                id='intensity-to',
                options=[{'label': x, 'value': x} for x in range(low, upp)],
                value=val_1)
        ], style={'width': '25%', 'display': 'inline-block'}),
    ])
    return output


def print_raw_count(idx):
    output = html.Div([
        html.Div(
            [html.P("n of raw count")],
            style={'width': '85%', 'display': 'inline-block'}),
        html.Div(
            [html.P(id='count-raw_' + str(idx))],
            style={'width': '15%', 'display': 'inline-block'})
    ])
    return output


def set_limits_fit_to_expon_dist_for_adjustment(idx, int_value_0, int_value_1):
    idstr_0 = 'Input-ef-range-low_' + str(idx)
    idstr_1 = 'Input-ef-range-upp_' + str(idx)
    idbtn = 'set-button-state-ef-range_' + str(idx)
    output = html.Div([
        html.Div(
            [html.P("Range of fit from")],
            style={'width': '44%', 'display': 'inline-block'}),
        dcc.Input(
            id=idstr_0, type='number', value=int_value_0,
            style={'width': '20%', 'display': 'inline-block'}),
        html.Div(
            [html.P("to")],
            style={'width': '8%', 'display': 'inline-block',
                   'padding-left': '2%', 'padding-right': '2%'}),
        dcc.Input(
            id=idstr_1, type='number', value=int_value_1,
            style={'width': '28%', 'display': 'inline-block'}),
    ])
    return output


def print_n_by_fit(idx):
    output = html.Div([
        html.Div(
            [html.P("n by src to exponential dist.")],
            style={'width': '85%', 'display': 'inline-block'}),
        html.Div(
            id='n-by-fit_' + str(idx),
            style={'width': '15%', 'display': 'inline-block'}),
    ], style={'display': 'inline'})
    return output


def set_cutoff_interval_for_adjustment(idx, int_value):
    idstr = 'Input-interval-threshold_' + str(idx)
    output = html.Div([
        html.Div([
            html.Div(
                [html.P("Ignore intervals less than ")],
                style={'width': '80%', 'display': 'inline-block'}),
            dcc.Input(
                id=idstr, type='number', value=int_value,
                style={'width': '20%', 'display': 'inline-block'}),
        ])
    ])
    return output


def print_n_by_cut(idx):
    output = html.Div([
        html.Div(
            [html.P("n by cutting small intervals")],
            style={'width': '85%', 'display': 'inline-block'}),
        html.Div(
            id='n-by-cut_' + str(idx),
            style={'width': '15%', 'display': 'inline-block'}),
    ], style={'display': 'inline'})
    return output


def select_from_raw_fit_cut(idx):
    id_string = 'select-one-of-raw-fit-cut_' + str(idx)
    id_string_output = 'n-to-use_' + str(idx)
    true_or_false = False
    output = html.Div([
        html.Div([
            dcc.RadioItems(
                options=[
                    {'label': 'Raw n', 'value': 'Raw n',
                     'disabled': true_or_false},
                    {'label': 'n by fit', 'value': 'n by fit',
                     'disabled': true_or_false},
                    {'label': 'n by cut', 'value': 'n by cut',
                     'disabled': true_or_false}
                ],
                value='n by fit',
                id=id_string,
                InputStyle={'margin-right': '4px', 'margin-left': '4px',
                            'display': 'inline-block'}
            )
        ], style={'display': 'inline-block', 'width': '85%'}),
        html.Div([
            html.Div(id=id_string_output),
        ], style={'display': 'inline-block', 'width': '15%'})
    ])
    return output


def choose_count_occurrence_for_regression(idx, cutoff):
    low = cfe.range_exp_fit_low[idx - 1]
    upp = cfe.range_exp_fit_upp[idx - 1]
    output = html.Div([
        html.Div([
            html.H6("Intensity >= " + str(idx)),
            print_raw_count(idx),
            set_limits_fit_to_expon_dist_for_adjustment(idx, low, upp),
            print_n_by_fit(idx),
            set_cutoff_interval_for_adjustment(idx, cutoff),
            print_n_by_cut(idx),
            html.Div([html.P("Which one do you use?")]),
            select_from_raw_fit_cut(idx),
        ], style={'display': 'inline', 'font-size': '.9rem',
                  'line-height': '.5rem'}),  # , 'line-height': '0.2rem'}),
        html.Br()
    ])
    return output


def choose_log_or_linear_for_intervals_scale():
    output = html.Div([
        html.Div(
            [html.P("Interval scale")], style={
                'display': 'inline-block', 'width': '50%'}
        ),
        html.Div([
            dcc.RadioItems(
                options=[{'label': 'Linear', 'value': 'linear'},
                         {'label': 'Log', 'value': 'log'}],
                value='linear',
                id='intervals-linear-or-log',
                InputStyle={'margin-right': '4px', 'margin-left': '4px'})
        ], style={'display': 'inline-block', 'width': '50%'})
    ])
    return output


################################################################################
#  To be put into eqanalysis
################################################################################


def fit_intervals_to_exponential(df, d_low, d_upp):
    df_sel = df[df['interval'] >= d_low]
    df_sel = df_sel[df_sel['interval'] <= d_upp]
    x = df_sel['interval']
    log10y = df_sel['counts'].apply(np.log10)
    res = scipy.stats.linregress(x, log10y)
    return res


# def count_after_ignoring_lteq_threshold(df, interval_threshold):
#     df_sel = df[df['interval'] >= interval_threshold]
#     return len(df_sel) + 1


################################################################################
#   Preparation and Layout
################################################################################

meta = pd.read_csv(FILE2READ_META)
cff = fig_template.FigSettings()
cfd = fig_template.DashSettings()
cfe = eqa.Settings()
cfs = Settings()
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP],
           suppress_callback_exceptions=True,)
mathjax = 'https://cdnjs.cloudflare.com/ajax/libs/mathjax/3.2.0/es5/tex-mml-chtml.js'
app.scripts.append_script({ 'external_url' : mathjax })
app.layout = dbc.Container([
    cfd.navbar,
    dbc.Container([
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.Br(),
                    html.H5("Settings"),
                    html.Div(id="station-data-msg"),
                    select_station(3710233),
                    html.Br(),
                    set_datetime(0),
                    
                    dcc.Store(id='station-prime'),
                    dcc.Store(id='available-period_dict'),
                    dcc.Store(id='set-period'),
                    html.Br(),
                    select_fitting_intensities("Yes", 2),
                    dcc.Store(id='intensity-lowest-fit'),
                    dcc.Store(id='regression-corrected-params')

                #     html.Div([html.Div(id='conditions-period')]),
                #     dcc.Store(id='station-meta-period'),
                #     dcc.Store(id='data-range-reg-int-occ'),
                #     dcc.Store(id='intensity-gteq_1'),
                #     dcc.Store(id='intensity-gteq_2'),
                #     dcc.Store(id='intensity-gteq_3'),
                #     dcc.Store(id='intensity-gteq_4'),
                #     dcc.Store(id='intensity-gteq_5'),
                #     dcc.Store(id='intensity-gteq_6'),
                #     dcc.Store(id='intensity-gteq_7'),
                #     dcc.Store(id='n-raw-counts'),

                #     html.H5("Regression intensity vs occurrence"),
                #     set_range_regression_intensity_occurrence(2, 4, 1, 7),
                #     html.Button(id='submit-button-state-all', n_clicks=0,
                #                 children='Draw Figures', style={'width': '80%'}),
                #     html.Br(),
                #     html.Br(),
                #     html.Br(),

                #     html.H5("Adjustment of occurrence"),
                #     #
                #     # CONSIDER take the values from eqanalysis.Settings or cfe
                #     #
                #     choose_log_or_linear_for_intervals_scale(),
                #     choose_count_occurrence_for_regression(1, 7),
                #     choose_count_occurrence_for_regression(2, 10),
                #     choose_count_occurrence_for_regression(3, 32),  # CHECK this
                #     choose_count_occurrence_for_regression(4, 46),  # CHECK this
                #     choose_count_occurrence_for_regression(5, 46),
                #     choose_count_occurrence_for_regression(6, 46),
                #     choose_count_occurrence_for_regression(7, 46),
                ], style={'margin': '2px'})
            ], width={'size': 10}, sm=8, md=6, lg=4, xxl=3
            ),
            dbc.Col([
                dcc.Store(id='iror-data'),
                dcc.Store(id='iror-summary-data'),
                dcc.Store(id='fasc-factors-user-data'),
                dcc.Store(id='factor-range_1'),
                dcc.Store(id='factor-range_2'),
                dcc.Store(id='factor-range_3'),
                dcc.Store(id='factor-range_4'),
                dcc.Store(id='factor-range_5'),
                dcc.Store(id='factor-range_6'),
                dcc.Store(id='factor-range_7'),
                dcc.Store(id='factor-user_1'),
                dcc.Store(id='factor-user_2'),
                dcc.Store(id='factor-user_3'),
                dcc.Store(id='factor-user_4'),
                dcc.Store(id='factor-user_5'),
                dcc.Store(id='factor-user_6'),
                dcc.Store(id='factor-user_7'),
                dcc.Store(id='factor-user-temp_1', storage_type='memory'),
                dcc.Store(id='factor-user-temp_2'),
                dcc.Store(id='factor-user-temp_3'),
                dcc.Store(id='factor-user-temp_4'),
                dcc.Store(id='factor-user-temp_5'),
                dcc.Store(id='factor-user-temp_6'),
                dcc.Store(id='factor-user-temp_7'),
                dcc.Store(id='regression-corrected'),
                dcc.Store(id='intervals_1-data'),
                dcc.Store(id='intervals_2-data'),
                dcc.Store(id='intervals_3-data'),
                dcc.Store(id='intervals_4-data'),
                dcc.Store(id='intervals_5-data'),
                dcc.Store(id='intervals_6-data'),
                dcc.Store(id='intervals_7-data'),
                dcc.Store(id='intervals_1-user-regression'),
                # dcc.Store(id='data-adjust-aftershocks_1'),
                # dcc.Store(id='data-adjust-aftershocks_2'),
                # dcc.Store(id='data-adjust-aftershocks_3'),
                # dcc.Store(id='data-adjust-aftershocks_4'),
                # dcc.Store(id='data-adjust-aftershocks_5'),
                # dcc.Store(id='data-adjust-aftershocks_6'),
                # dcc.Store(id='data-adjust-aftershocks_7'),
                # dcc.Store(id='data-summary'),
                # dcc.Store(id='data-estimation'),
                html.Br(),
                html.H5("Intensity-Rate of Occurrence"),
                # html.Div(id='data-summary-table'),
                html.Div([
                    html.Div([
                        html.Div(id='fasc-factor-datatable'),
                        # html.Br(),
                        html.Br(),
                        html.Br(),
                    ], style={
                        'width':'312px', 'margin':'2px',
                        'display':'inline-block',
                        'padding-right': '24px', 
                        'vertical-align': 'top'},
                    ),
                    html.Div([
                        html.Div(id='iror-figure'),
                        # html.Br(),
                        html.Br(),
                        html.Br(),
                    ], style={'display': 'inline-block', 'vertical-align':'top'})
                ]),      
                html.H5("Intervals"),
                html.Div([
                    html.Div([
                    html.Div(id='intervals_1-figure', style={'display': 'inline-block', 'width': '316px'}),
                    ], style={'display': 'inline-block', 'width': '316px'}),
                    html.Div(id='factor-user-display-temp_1'),
                    html.Div(id='intervals_2-figure', style={'display': 'inline-block', 'width': '316px'}),
                    html.Div(id='intervals_3-figure', style={'display': 'inline-block', 'width': '316px'}),
                    html.Div(id='intervals_4-figure', style={'display': 'inline-block', 'width': '316px'}),
                    html.Div(id='intervals_5-figure', style={'display': 'inline-block', 'width': '316px'}),
                    html.Div(id='intervals_6-figure', style={'display': 'inline-block', 'width': '316px'}),
                    html.Div(id='intervals_7-figure', style={'display': 'inline-block', 'width': '316px'}),
                ], style={'display': 'block'}),
                
            # html.Div(id='data-summary-table'),
            #     html.Div(id='data-estimation-table'),
            #     html.Div(id='range-regression-intensity-occurrence'),
            #     html.H3("Occurrence of earthquakes of intensity gteq"),
            #     html.Div(id='fig-summary'),
            #     html.Div(
            #         id='graph-intensity-occurrence',
            #         style={'display': 'inline-block'}),
            #     html.H3('Intervals'),
            #     dbc.Container([
            #         html.Div(id='conditions'),
            #         html.Div([
            #             html.Div(id='two-values_' + str(1),
            #                      style={'display': 'inline'}),
            #             html.Div(),
            #             html.Div(id='two-values_' + str(2),
            #                      style={'display': 'inline'}),
            #             html.Div(id='two-values_' + str(3),
            #                      style={'display': 'inline'}),
            #             html.Div(id='two-values_' + str(4),
            #                      style={'display': 'inline'}),
            #             html.Div(id='two-values_' + str(5),
            #                      style={'display': 'inline'}),
            #         ], style={'display': 'inline'}),
            #         html.Br(),
            #         html.Div(id='graphs', style={'display': 'inline-block'}),
            #     ], style={'display': 'block'})
            ], width={'size': 12}, lg=8, xxl=9)
        ]),
    ], fluid=False)
], style=cfd.global_style, fluid=True)


################################################################################
#   Callbacks
################################################################################

@app.callback(
    Output('station-prime', 'data'),
    Output('available-period_dict', 'data'),
    Output('available-period', 'data'),
    Output('available-period', 'columns'),
    Output('station-data-msg', 'children'),
    Input('select-station-submit-button-state', 'n_clicks'),
    State('station', 'value')
)
def check_station_is_in_the_database_and_get_available_period(_, str_code):
    station = int(str_code)
    df_org = pd.read_csv(FILE2READ_ORG)
    try:
        res = eqa.find_available_periods_ts(df_org, station)
    except Exception as ex:
        msg = str_code + ' is NOT in the database.'
        data = None
        columns = None
    else:
        available = res
        msg = html.P([
            str_code + ' is in the database.', html.Br(),
            "Records in the database are during", html.Br(),
        ])
        data=available.to_dict('records')
        n = len(data)
        for i in range(n):
            data[i]['from'] = data[i]['from'][:10]
            data[i]['to'] = data[i]['to'][:10]
        columns = columns=[{"name": i, "id": i} for i in available.columns]    
    return station, data, data, columns, msg 


@app.callback(
    Output('set-period', 'data'),
    Input('set-period-submit-button-state', 'n_clicks'),
    State('set-datetime_0', 'data'),
    State('set-datetime_0', 'columns')
)
def set_analysis_period(_, data, columns):
    dt_from = datetime.datetime(
        int(data[0]['yr']), int(data[0]['mo']), int(data[0]['day']),
        int(data[0]['hr']), int(data[0]['min']), int(data[0]['sec'])
    )
    dt_to = datetime.datetime(
        int(data[1]['yr']), int(data[1]['mo']), int(data[1]['day']),
        int(data[1]['hr']), int(data[1]['min']), int(data[1]['sec'])
    )
    set_to = {
        "set_from": datetime.datetime.strftime(dt_from, "%Y-%m-%d %H:%M:%S"),
        "set_to": datetime.datetime.strftime(dt_to, "%Y-%m-%d %H:%M:%S")
    }
    return set_to

# @app.callback(
#     Output('fasc-factors-data', 'data'),
#     Input('iror-data', 'data')
# )
# def create_table_of_correction_factors(iror_dict):
#     iror = pd.DataFrame.from_dict(iror_dict)
#     print(iror)
#     fasc_factors = iror[['intensity', 'factor']]
#     print(fasc_factors)
#     fascf_dict = fasc_factors.to_dict('records')
#     fascf_columns =[{"name": i, "id": i} for i in fasc_factors.columns]    
#     return fascf_dict, fascf_columns

@app.callback(
    Output('fasc-factor-datatable', 'children'),
    Input('iror-data', 'data'),
    # Input('fasc-factors-user-data', 'data'),
    Input('factor-user_1', 'data'),
    Input('factor-user_2', 'data'),
    Input('factor-user_3', 'data'),
    Input('factor-user_4', 'data'),
    Input('factor-user_5', 'data'),
    Input('factor-user_6', 'data'),
    Input('factor-user_7', 'data'),
)
def refresh_fasc_factors_table(
    iror_dict, fu_1, fu_2, fu_3, fu_4, fu_5, fu_6, fu_7):
    iror = pd.DataFrame.from_dict(iror_dict)
    df_factors = iror[['intensity', 'factor']]
    df_factors.loc[:, 'factor_user'] = np.nan
    if fu_1 is not None:
        df_factors.at[0, 'factor_user'] = fu_1['factor_user_temp']
    if fu_2 is not None:
        df_factors.at[1, 'factor_user'] = fu_2['factor_user_temp']
    if fu_3 is not None:
        df_factors.at[2, 'factor_user'] = fu_3['factor_user_temp']
    if fu_4 is not None:
        df_factors.at[3, 'factor_user'] = fu_4['factor_user_temp']
    if fu_5 is not None:
        df_factors.at[4, 'factor_user'] = fu_5['factor_user_temp']
    if fu_6 is not None:
        df_factors.at[5, 'factor_user'] = fu_6['factor_user_temp']
    if fu_7 is not None:
        df_factors.at[6, 'factor_user'] = fu_7['factor_user_temp']

    output = html.Div([
        html.H6(['FAS Correction Factors']),
        dash_table.DataTable(
            editable=False,
            data=df_factors.to_dict("records"),
            columns=[
                dict(id='intensity', name='intensity', type='numeric',
                     format=Format(precision=0)),
                dict(id='factor', name='factor', type='numeric',
                     format=Format(precision=3)),
                dict(id='factor_user', name='factor_user', type='numeric',
                     format=Format(precision=3)),                
            ],
            # persistence=True,
            # persistence_type='memory',
            # persisted_props = ['columns.name', 'data'],
            style_cell_conditional=[
                {'if': {'column_id': 'intensity'}, 'width': '30%'},
                {'if': {'column_id': 'factor'},'width': '35%'},
                {'if': {'column_id': 'factor_user'},'width': '35%'},
            ]
        ),    
    ])
    return output


@app.callback(
    Output('iror-data', 'data'),
    Output('iror-summary-data', 'data'),
    Output('intervals_1-data', 'data'),
    Output('intervals_2-data', 'data'),
    Output('intervals_3-data', 'data'),
    Output('intervals_4-data', 'data'),
    Output('intervals_5-data', 'data'),
    Output('intervals_6-data', 'data'),
    Output('intervals_7-data', 'data'),
    Input('station-prime', 'data'),
    Input('set-period', 'data')
)
def calculate_summary(station_prime, set_dict):
    df_org = pd.read_csv(FILE2READ_ORG)
    dfs_intervals, df_corrected, summary_corrected = \
        eqa.do_aftershock_correction(
            df_org, station_prime, set_dict, DIR_DATA 
    )
    dicts_intervals = []
    for i_int, df_intervals in enumerate(dfs_intervals):
        # print("Length of intervals = {}".format(len(df_intervals)))
        if len(df_intervals) != 0:
            # print(df_intervals)
            dicts_intervals.append(df_intervals.to_dict('records'))
        else:
            dicts_intervals.append(None)

    summary = pd.DataFrame(summary_corrected).transpose()
    summary_dict = summary.to_dict('records')
    corrected_dict = df_corrected.to_dict('records')
    return corrected_dict, summary_dict, dicts_intervals[0],\
        dicts_intervals[1], dicts_intervals[2], dicts_intervals[3],\
        dicts_intervals[4], dicts_intervals[5], dicts_intervals[6]


@app.callback(
    Output('regression-corrected-params', 'data'),
    Input('button-select-fit-intensity', 'n_clicks'),
    State('draw-or-not-reg-corrected', 'value'),
    State('seleft-fit-intensity-low', 'value'),
)
def select_fitting_intensity_lower_bound(_, draw_correct, value):
    dict = {"Draw": draw_correct, "lowestint": int(value)}
    return dict


@app.callback(
    Output('regression-corrected', 'data'),
    Input('regression-corrected-params', 'data'),
    Input('iror-data', 'data'),
)
def regression_lines(corrected_params, corrected_data):
    if corrected_params["Draw"] == "No":
        return None
    else:
        df_corrected = pd.DataFrame.from_dict(corrected_data)
        corrected = df_corrected['corrected'].values
        corrected = corrected[corrected > 0]
        iror = eqa.IROR(corrected)
        df = pd.DataFrame()
        li = corrected_params["lowestint"]
        res = iror.find_iror(li)
        if res is not None:
            df.at[0, 'attribute'] = 'corrected'
            df.at[0, 'leastint'] = li
            df.at[0, 'slope'] = res.slope
            df.at[0, 'intercept'] = res.intercept
            df.at[0, 'rvalue'] = res.rvalue
            df.at[0, 'pvalue'] = res.pvalue
    return df.to_dict('records')


@app.callback(
    Output('iror-figure', 'children'),
    Input('iror-data', 'data'),
    Input('regression-corrected-params', 'data'),
    Input('regression-corrected', 'data')
)
def draw_iror(corrected_data, reg_cor_params, reg_corrected):
    df = pd.DataFrame.from_dict(corrected_data)
    df_reg_corrected = pd.DataFrame.from_dict(reg_corrected)
    regression = reg_cor_params["Draw"]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['intensity'], y=df['ro'], mode="markers",
        name="Raw",
        marker=dict(size=10, symbol="square", color=cud_skyblue)
    ))
    fig.add_trace(go.Scatter(
        x=df['intensity'], y=df['corrected'], mode="markers",
        name="Corrected",
        marker=dict(size=10, symbol="circle", color="black")
    ))
    if regression == "Yes":
        li = reg_cor_params["lowestint"]
        xrs = np.linspace(li - .2, 7.2)
        yrs = 10 ** (
            df_reg_corrected.at[0, 'intercept'] + \
                df_reg_corrected.at[0, 'slope'] * xrs
        )
        fig.add_traces(go.Scatter(
            x=xrs, y=yrs, name="Reg. corrected",
            mode="lines",
            line=dict(width=.5, color="black")
        ))

    # 15 + 54 + 3 = 72
    # 12 + 54 + 3 = 69
    mlt = 13/3
    fig.update_layout(
        autosize=False,
        width=72 * mlt,
        height=69 * mlt,
        margin=dict(
            l=15 * mlt, r=3 * mlt, t=3 * mlt, b=12 * mlt, pad=0
        ),
        legend=dict(
            x=1, y=56/54, xanchor='right', yanchor='top',
            font=dict(family="Helvetica", size=10, color="black"),
            itemsizing='trace',
            tracegroupgap=0,
        ),
        # legend_tracegroupgap=20,
        xaxis_title="Intensities",
        yaxis_title="Rate of occurrence [1/year]"
    )
    fig.update_yaxes(type="log")
    fig.update_layout(legend_tracegroupgap=0)
    output = html.Div([
        dcc.Graph(figure=fig, style={'margin':'auto'})
    ], style={'width': '312px', 'margin': '2`px'})
    return output


# @app.callback(
#     Output('user-defined-factor_1', 'data'),
#     Input('apply-user-defined-factor_1', 'value'),
#     State('intervals_1-user-regression', 'data')
# )
# def use_user_defined_correction_factor_1(app, reg_dict):
#     reg_user = pd.Series(reg_dict)
#     print(reg_user)
#     return reg_dict


# @app.callback(
#     Output('intervals_1-control', 'children'),
#     Output('intervals_1-user-regression', 'data'),
#     Output('factor-user_1', 'data'),
#     Input('button-interval-fit-range_1', 'n_clicks'),
#     State('station-prime', 'data'),
#     # State('iror-summary-data', 'data'),
#     State('intervals_1-data', 'data'),
#     State('interval-fit-range_1', 'data')
# )
# def interval_1_custom_factor(
#     _, station_prime, intervals_1, range_1):
#     # df_corrected = pd.DataFrame.from_dict(summary_dict)
#     # print(df_corrected)
#     df_intervals = pd.DataFrame.from_dict(intervals_1)
#     df_range = pd.DataFrame.from_dict(range_1)
#     low = int(df_range.at[0, 'low'])
#     upp = int(df_range.at[0, 'upp'])
#     reg = pd.Series()
#     reg['station'] = station_prime
#     reg['slope_1-user'] = np.nan
#     reg['intercept_1-user'] = np.nan
#     reg['rvalue_1-user'] = np.nan
#     reg['pvalue_1-user'] = np.nan
#     res = None
#     factor = None
#     if len(df_intervals) > 0:
#         df_intervals = df_intervals[df_intervals['interval'] > low]
#         df_intervals = df_intervals[df_intervals['interval'] < upp]
#         try:
#             res = scipy.stats.linregress(
#                 df_intervals['interval'], np.log10(df_intervals['suvf']))
#         except Exception as ex:
#             print(ex)
#         else:
#             factor = 10 ** res.intercept
#             reg['slope_1-user'] = res.slope
#             reg['intercept_1-user'] = res.intercept
#             reg['rvalue_1-user'] = res.rvalue
#             reg['pvalue_1-user'] = res.pvalue
#     if factor is not None:
#         output = html.P("Factor = {:.3f}".format(factor))
#     else:
#         output = html.P("")
#     reg_dict = reg.to_dict()
#     # print(reg)
#     # print("reg_dict", reg_dict)
#     # print(output)
#     return output, reg_dict, factor


################################################################################
# For initial fitting range
################################################################################

# @app.callback(
#     Output('factor-range_1', 'data'),
#     Input('iror-data', 'data')
# )
# def find_initial_fitting_range(iror_dict):
#     df_corrected = pd.DataFrame.from_dict(iror_dict)
#     print('df_corrected at find_initial_fitting_range')
#     print(df_corrected)
#     print(data_1)
#     print(df_range_1)
#     data_1 = [["Range (days)", 4,
#                int(df_corrected.at[0, 'interval_1st_fit_upp'])]]
#     df_range_1 = pd.DataFrame(data_1, columns=["Your fitting" 'low', 'upp'])
#     df_dict_1 = df_range_1.to_dict('records')

#     data_2 = [["Range (days)", 8,
#                int(df_corrected.at[0, 'interval_2st_fit_upp'])]]
#     df_range_2 = pd.DataFrame(data_2, columns=["Your fitting" 'low', 'upp'])
#     df_dict_2 = df_range_2.to_dict('records')

#     data_3 = [["Range (days)", 16, 
#                int(df_corrected.at[0, 'interval_3st_fit_upp'])]]
#     df_range_3 = pd.DataFrame(data_3, columns=["Your fitting" 'low', 'upp'])
#     df_dict_3 = df_range_3.to_dict('records')

#     data_4 = [["Range (days)", 32, 
#                int(df_corrected.at[0, 'interval_4st_fit_upp'])]]
#     df_range_4 = pd.DataFrame(data_4, columns=["Your fitting" 'low', 'upp'])
#     df_dict_4 = df_range_4.to_dict('records')

#     data_5 = [["Range (days)", 64, 
#                int(df_corrected.at[0, 'interval_5st_fit_upp'])]]
#     df_range_5 = pd.DataFrame(data_5, columns=["Your fitting" 'low', 'upp'])
#     df_dict_5 = df_range_5.to_dict('records')

#     data_6 = [["Range (days)", 128, 
#                int(df_corrected.at[0, 'interval_6st_fit_upp'])]]
#     df_range_6 = pd.DataFrame(data_6, columns=["Your fitting" 'low', 'upp'])
#     df_dict_6 = df_range_6.to_dict('records')

#     data_7 = [["Range (days)", 256, 
#                int(df_corrected.at[0, 'interval_7st_fit_upp'])]]
#     df_range_7 = pd.DataFrame(data_7, columns=["Your fitting" 'low', 'upp'])
#     df_dict_7 = df_range_7.to_dict('records')

#     return df_dict_1, df_dict_2, df_dict_3, df_dict_4, df_dict_5, df_dict_6, \
#         df_dict_7


def draw_interval_survival(df_intervals, df_corrected, i_int):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_intervals['interval'], y=df_intervals['suvf'], mode='markers',
        marker=dict(size=8, symbol='circle', color=cud_blue),
        name='intensity ' + str(i_int + 1),
        showlegend=False))
    xrs = np.linspace(0, df_corrected.at[i_int, 'interval_1st_fit_upp'])
    slope = df_corrected.at[i_int, 'slope']
    intercept = df_corrected.at[i_int, 'intercept']
    factor = df_corrected.at[i_int, 'factor']
    if not np.isnan(slope):
        yrs = 10 ** (intercept + slope * xrs)
        fig.add_trace(go.Scatter(
            x=xrs, y=yrs, mode='lines',
            line=dict(width=2, color=cud_orange),
            name="Fit",
            showlegend=False,
        ))
    if np.isnan(slope):
        fig.add_traces(go.Scatter(
            x=[0, df_intervals['interval'].max() * .2],
            y=[factor,factor], mode='lines',
            line=dict(width=2, color=cud_orange),
            showlegend=False,))
    mlt = 13/3
    fig.update_layout(
        autosize=False,
        width=mlt * 72,
        height=mlt * 51,
        margin=dict(
            l=15 * mlt, r=3 * mlt, t=3 * mlt, b=12 * mlt, pad=0),
        yaxis_title=r'$(1 - F)^{\wedge}$',
        xaxis_title='intervals [days]')
    fig.add_annotation(text="Intensity " + str(i_int + 1),
        xref="x domain", yref="y domain",
        x=0.98, y=0.98, showarrow=False, xanchor='right',
        yanchor='top')
    fig.add_annotation(text="Factor = {:.3f}".format(factor),
        xref="x domain", yref="y domain",
        x=0.98, y=0.88, showarrow=False, xanchor='right',
        yanchor='top')
    fig.update_yaxes(type="log")
    return fig


@app.callback(
    Output('intervals_1-figure', 'children'),
    Output('intervals_2-figure', 'children'),
    Output('intervals_3-figure', 'children'),
    Output('intervals_4-figure', 'children'),
    Output('intervals_5-figure', 'children'),
    Output('intervals_6-figure', 'children'),
    Output('intervals_7-figure', 'children'),
    Input('iror-data', 'data'),
    Input('intervals_1-data', 'data'),
    Input('intervals_2-data', 'data'),
    Input('intervals_3-data', 'data'),
    Input('intervals_4-data', 'data'),
    Input('intervals_5-data', 'data'),
    Input('intervals_6-data', 'data'),
    Input('intervals_7-data', 'data'),
    Input('factor-user-temp_1', 'data'),
    Input('factor-user-temp_2', 'data'),
    Input('factor-user-temp_3', 'data'),
    Input('factor-user-temp_4', 'data'),
    Input('factor-user-temp_5', 'data'),
    Input('factor-user-temp_6', 'data'),
    Input('factor-user-temp_7', 'data'),
)
def draw_intervals(
    corrected_dict, intervals_1_dict, intervals_2_dict, intervals_3_dict,
    intervals_4_dict, intervals_5_dict, intervals_6_dict, intervals_7_dict,
    fut_1, fut_2, fut_3, fut_4, fut_5, fut_6, fut_7):

    futs = [fut_1, fut_2, fut_3, fut_4, fut_5, fut_6, fut_7]
    df_corrected = pd.DataFrame.from_dict(corrected_dict)
    print(df_corrected)
    dfs_intervals = [
        pd.DataFrame.from_dict(intervals_1_dict),
        pd.DataFrame.from_dict(intervals_2_dict),
        pd.DataFrame.from_dict(intervals_3_dict),
        pd.DataFrame.from_dict(intervals_4_dict),
        pd.DataFrame.from_dict(intervals_5_dict),
        pd.DataFrame.from_dict(intervals_6_dict),
        pd.DataFrame.from_dict(intervals_7_dict),
    ]
    figs = [None, None, None, None, None, None, None]
    for i_int, df_intervals in enumerate(dfs_intervals):
        if len(df_intervals) != 0:
            fu_dict = futs[i_int]
            if fu_dict is not None:
                print('fu_dict in draw_intervals')
                print(fu_dict)
                fu = fu_dict['factor_user_temp']
                fu = np.round(fu, 3)
                print(fu)
            else:
                fu = np.nan
            fig = draw_interval_survival(df_intervals, df_corrected, i_int) 
            figs[i_int] = html.Div([
                html.Div([
                    set_range_fit_intervals(
                        i_int + 1, 2 ** (i_int + 2), 
                        df_corrected.at[i_int, 'interval_1st_fit_upp'], fu)
                ]),
                html.Div([
                    dcc.Graph(figure=fig, style={'margin':'auto'},
                        mathjax=True)
                ], style={'display': 'inline-block', 'vertical-align': 'bottom'}),
                html.Br(),
                html.Br(),
                html.Br()
            ])
    return figs[0], figs[1], figs[2], figs[3], figs[4], figs[5], figs[6]


def fit_intervals_find_factor(df_intervals, range_dict):
    df_range = pd.DataFrame.from_dict(range_dict)
    low = df_range.at[0, 'low']
    upp = df_range.at[0, 'upp']
    df_intervals = df_intervals[df_intervals['interval'] > low]
    df_intervals = df_intervals[df_intervals['interval'] < upp]
    factor = np.nan
    if len(df_intervals) > 0:
        res = scipy.stats.linregress(
            df_intervals['interval'], np.log10(df_intervals['suvf']))
        factor = 10 ** (res.intercept)
    print("factor = ", factor)
    return factor


@app.callback(
    Output('factor-user-temp_1', 'data'),
    Input('button-interval-fit-range_1', 'n_clicks'),
    State('interval-fit-range_1', 'data'),
    State('intervals_1-data', 'data')
)
def find_factor_user_1(n_clicks_1, range_dict, intervals_dict):
    df_intervals = pd.DataFrame.from_dict(intervals_dict)
    factor_1 = fit_intervals_find_factor(df_intervals, range_dict)
    fu_dict = {'factor_user_temp': factor_1}
    print("fu_dict in find_factor_user_1")
    print(fu_dict)
    return fu_dict


@app.callback(
    Output('factor-user_1', 'data'),
    Input('button-use-factor-user_1', 'n_clicks'),
    Input('factor-user-temp_1', 'data')
)
def put_factor_user_1_to_user_factors(_, fu_dict):
    return fu_dict


@app.callback(
    Output('factor-user-display-temp_1', 'children'),
    Input('interval-fit-range_1', 'data'),
    Input('factor-user-temp_1', 'data')
)
def display_factor_user_1(range_dict, fu_1):
    df_range = pd.DataFrame.from_dict(range_dict)
    df_range.at[0, 'fu_1'] = fu_1['factor_user_temp']
    columns = columns=[{"name": i, "id": i} for i in df_range.columns]
    output = html.Div([
        dash_table.DataTable(
            # editable=True,
            id="factor-user_display-temp-table_1",
            columns=columns,
            data=df_range.to_dict("records"),
            persistence=True,
            persistence_type='memory',
            persisted_props = ['columns.name', 'data'],
            # style_cell={
            #     'width': '12%'.format(len(df.columns)),
            # },
            # style_cell_conditional=[
            #     {'if': {'column_id': 'attrib'},'width': '15%'},
            #     {'if': {'column_id': 'yr'},'width': '15%'},
            # ],            
        ),    
    ]),
    return output





@app.callback(
    Output('factor-user-temp_2', 'data'),
    Input('button-interval-fit-range_2', 'n_clicks'),
    State('interval-fit-range_2', 'data'),
    State('intervals_2-data', 'data')
)
def find_factor_user_2(n_clicks_2, range_dict, intervals_dict):
    df_intervals_2 = pd.DataFrame.from_dict(intervals_dict)
    return fit_intervals_find_factor(df_intervals_2, range_dict)


@app.callback(
    Output('factor-user-temp_3', 'data'),
    Input('button-interval-fit-range_3', 'n_clicks'),
    State('interval-fit-range_3', 'data'),
    State('intervals_3-data', 'data')
)
def find_factor_user_3(n_clicks_3, range_dict, intervals_dict):
    df_intervals_3 = pd.DataFrame.from_dict(intervals_dict)
    return fit_intervals_find_factor(df_intervals_3, range_dict)


@app.callback(
    Output('factor-user-temp_4', 'data'),
    Input('button-interval-fit-range_4', 'n_clicks'),
    State('interval-fit-range_4', 'data'),
    State('intervals_4-data', 'data')
)
def find_factor_user_4(n_clicks_4, range_dict, intervals_dict):
    df_intervals_4 = pd.DataFrame.from_dict(intervals_dict)
    return fit_intervals_find_factor(df_intervals_4, range_dict)


@app.callback(
    Output('factor-user-temp_5', 'data'),
    Input('button-interval-fit-range_5', 'n_clicks'),
    State('interval-fit-range_5', 'data'),
    State('intervals_5-data', 'data')
)
def find_factor_user_5(n_clicks_5, range_dict, intervals_dict):
    df_intervals_5 = pd.DataFrame.from_dict(intervals_dict)
    return fit_intervals_find_factor(df_intervals_5, range_dict)


@app.callback(
    Output('factor-user-temp_6', 'data'),
    Input('button-interval-fit-range_6', 'n_clicks'),
    State('interval-fit-range_6', 'data'),
    State('intervals_6-data', 'data')
)
def find_factor_user_6(n_clicks_6, range_dict, intervals_dict):
    df_intervals_6 = pd.DataFrame.from_dict(intervals_dict)
    return fit_intervals_find_factor(df_intervals_6, range_dict)


@app.callback(
    Output('factor-user-temp_7', 'data'),
    Input('button-interval-fit-range_7', 'n_clicks'),
    State('interval-fit-range_7', 'data'),
    State('intervals_7-data', 'data')
)
def find_factor_user_7(n_clicks_7, range_dict, intervals_dict):
    df_intervals_7 = pd.DataFrame.from_dict(intervals_dict)
    return fit_intervals_find_factor(df_intervals_7, range_dict)

# @app.callback(
#     Output('factor-user_2', 'data'),
#     Input('button-use-factor-user_2', 'n_clicks'),
#     State('factor-user-temp_2', 'data')
# )
# def put_factor_user_2_to_user_factors(_, fu):
#     return fu


# # @app.callback(
#     Output('conditions-period', 'children'),
#     Output('station-meta-period', 'data'),
#     Input('available-period', 'data'),
#     Input('start-year', 'value'),
#     Input('start-month', 'value'),
#     Input('start-day', 'value'),
#     Input('end-year', 'value'),
#     Input('end-month', 'value'),
#     Input('end-day', 'value')
# )
# def set_the_period(meta_1_dict, sy, sm, sd, ey, em, ed):
#     meta_1p = pd.DataFrame.from_dict(meta_1_dict)
#     date_from = meta_1p.at[0, 'date_from']
#     date_to = meta_1p.at[0, 'date_to']
#     analysis_from = str(sy) + '-' + str(sm).zfill(2) + '-' + str(sd).zfill(2)
#     analysis_to = str(ey) + '-' + str(em).zfill(2) + '-' + str(ed).zfill(2)

#     date_from_date = datetime.datetime.strptime(date_from, "%Y-%m-%d")
#     date_to_date = datetime.datetime.strptime(date_to, "%Y-%m-%d")
#     analysis_from_date = datetime.datetime.strptime(analysis_from, "%Y-%m-%d")
#     analysis_to_date = datetime.datetime.strptime(analysis_to, "%Y-%m-%d")

#     if analysis_from_date < date_from_date:
#         analysis_from_date = date_from_date
#     if analysis_to_date > date_to_date:
#         analysis_to_date = date_to_date

#     analysis_from = datetime.datetime.strftime(analysis_from_date, "%Y-%m-%d")
#     analysis_to = datetime.datetime.strftime(analysis_to_date, "%Y-%m-%d")
#     meta_1p.at[0, 'analysis_from'] = analysis_from
#     meta_1p.at[0, 'analysis_to'] = analysis_to
#     meta_1p_dict = (pd.DataFrame(meta_1p)).to_dict('records')
#     return html.Div(
#         [html.P("Analyse the period from {} to {}.". \
#                 format(analysis_from, analysis_to))
#          ]), meta_1p_dict


# @app.callback(
#     Output('intensity-gteq_1', 'data'),
#     Output('intensity-gteq_2', 'data'),
#     Output('intensity-gteq_3', 'data'),
#     Output('intensity-gteq_4', 'data'),
#     Output('intensity-gteq_5', 'data'),
#     Output('intensity-gteq_6', 'data'),
#     Output('intensity-gteq_7', 'data'),
#     Output('n-raw-counts', 'data'),
#     Input('station-meta-period', 'data')
# )
# def get_intensity_wise_dataframes(station_meta_period):
#     meta_1p = pd.DataFrame.from_dict(station_meta_period)
#     print("meta_1p", meta_1p)
#     code = meta_1p.at[0, 'code']
#     analysis_from = meta_1p.at[0, 'analysis_from']
#     analysis_to = meta_1p.at[0, 'analysis_to']
#     dfis, n_raws = eqa.calc_intervals_n_raw_counts(
#         DIR_DATA, code, beginning=analysis_from, end=analysis_to)
#     dfi_dicts = []
#     for dfi in dfis:
#         dfi_dicts.append(dfi.to_dict())
#     # print(dfi_dicts)
#     df_n_raws = pd.Series(index=['1', '2', '3', '4', '5', '6', '7'])
#     for i in range(7):
#         df_n_raws.at[str(i+1)] = n_raws[i]
#     n_raws_dict = df_n_raws.to_dict()
#     return dfi_dicts[0], dfi_dicts[1], dfi_dicts[2], dfi_dicts[3], \
#            dfi_dicts[4], dfi_dicts[5], dfi_dicts[6], n_raws_dict

# #
# #  CONSIDER remove data-range-reg-int-occ
# #     these data are in Settings or cfs
# #

# @app.callback(
#     Output('range-regression-intensity-occurrence', 'children'),
#     Output('data-range-reg-int-occ', 'data'),
#     Input('intensity-from', 'value'),
#     Input('intensity-to', 'value')
# )
# def set_range_intensity_for_regression_vs_occurrence(intensity_0, intensity_1):
#     intensity_range_dict = {
#         'from': intensity_0, 'to': intensity_1}
#     cfs.reg_int_occ_low = intensity_0
#     cfs.reg_int_occ_upp = intensity_1
#     return html.P([
#         "Range of intensity in regression is from {} to {}".format(
#             intensity_0, intensity_1)]), intensity_range_dict


# def adjust_aftershocks(
#         idx, dfi_dict, limit_low, limit_upp, interval_cutoff, select,
#         n_raw_counts):
#     try:
#         dfi = pd.DataFrame.from_dict(dfi_dict)
#     except Exception as ex:
#         print(ex)
#         dfi = None
#         pass
#     n_raw = n_raw_counts[str(idx)]
#     intercept = np.nan
#     slope = np.nan
#     rvalue = np.nan
#     n_by_fit = np.nan
#     if n_raw > 2:
#         try:
#             res = fit_intervals_to_exponential(dfi, limit_low, limit_upp)
#             intercept = round_to_k(10 ** res.intercept, 4)
#             slope = round_to_k(res.slope, 4)
#             rvalue = round_to_k(res.rvalue, 4)
#             n_by_fit = np.round(intercept, 1)
#         except ValueError as ve:
#             print("Regression exp failed, ", ve)
#             pass
#     else:
#         n_by_fit = n_raw

#     if n_raw <= 1:
#         n_by_cut = n_raw
#     else:
#         n_by_cut = len(dfi[dfi['interval'] >= interval_cutoff]) + 1
#     if select == "Raw n":
#         n_to_use = n_raw
#     elif select == "n by fit":
#         n_to_use = n_by_fit
#     elif select == "n by cut":
#         n_to_use = n_by_cut
#     fit_dict = {
#         'intensity': idx, 'efl': limit_low, 'efu': limit_upp,
#         'cutoff': interval_cutoff, 'ef_intercept': intercept,
#         'ef_slope': slope, 'ef_r': rvalue, 'which': select,
#         'n_raw': n_raw, 'n_by_fit': n_by_fit, 'n_by_cut': n_by_cut,
#         'n_to_use': n_to_use
#     }
#     print(fit_dict)
#     return n_raw, n_by_fit, n_by_cut, n_to_use, fit_dict


# # @app.callback(
# #     Output('intervals-linear-or-log-out', 'data'),
# #     Input('intervals-linear-or-log', 'value'),
# # )


# @app.callback(
#     Output('count-raw_1', 'children'),
#     Output('n-by-fit_1', 'children'),
#     Output('n-by-cut_1', 'children'),
#     Output('n-to-use_1', 'children'),
#     Output('data-adjust-aftershocks_1', 'data'),
#     Input('intensity-gteq_1', 'data'),
#     Input('Input-ef-range-low_1', 'value'),
#     Input('Input-ef-range-upp_1', 'value'),
#     Input('Input-interval-threshold_1', 'value'),
#     Input('select-one-of-raw-fit-cut_1', 'value'),
#     Input('n-raw-counts', 'data'),
# )
# def set_threshold_regression_1(
#         dfi_dict, limit_low, limit_upp, interval_cutoff, select,
#         n_raw_counts):
#     n_raw, n_by_fit, n_by_cut, n_to_use, fit_dict = adjust_aftershocks(
#         1, dfi_dict, limit_low, limit_upp, interval_cutoff, select,
#         n_raw_counts)
#     return [n_raw], [n_by_fit], [n_by_cut], [n_to_use], fit_dict


# @app.callback(
#     Output('count-raw_2', 'children'),
#     Output('n-by-fit_2', 'children'),
#     Output('n-by-cut_2', 'children'),
#     Output('n-to-use_2', 'children'),
#     Output('data-adjust-aftershocks_2', 'data'),
#     Input('intensity-gteq_2', 'data'),
#     Input('Input-ef-range-low_2', 'value'),
#     Input('Input-ef-range-upp_2', 'value'),
#     Input('Input-interval-threshold_2', 'value'),
#     Input('select-one-of-raw-fit-cut_2', 'value'),
#     Input('n-raw-counts', 'data')
# )
# def set_threshold_regression_2(
#         dfi_dict, limit_low, limit_upp, interval_cutoff, select,
#         n_raw_counts):
#     n_raw, n_by_fit, n_by_cut, n_to_use, fit_dict = adjust_aftershocks(
#         2, dfi_dict, limit_low, limit_upp, interval_cutoff, select,
#         n_raw_counts)
#     return [n_raw], [n_by_fit], [n_by_cut], [n_to_use], fit_dict


# @app.callback(
#     Output('count-raw_3', 'children'),
#     Output('n-by-fit_3', 'children'),
#     Output('n-by-cut_3', 'children'),
#     Output('n-to-use_3', 'children'),
#     Output('data-adjust-aftershocks_3', 'data'),
#     Input('intensity-gteq_3', 'data'),
#     Input('Input-ef-range-low_3', 'value'),
#     Input('Input-ef-range-upp_3', 'value'),
#     Input('Input-interval-threshold_3', 'value'),
#     Input('select-one-of-raw-fit-cut_3', 'value'),
#     Input('n-raw-counts', 'data')
# )
# def set_threshold_regression_3(
#         dfi_dict, limit_low, limit_upp, interval_cutoff, select,
#         n_raw_counts):
#     n_raw, n_by_fit, n_by_cut, n_to_use, fit_dict = adjust_aftershocks(
#         3, dfi_dict, limit_low, limit_upp, interval_cutoff, select,
#         n_raw_counts)
#     return [n_raw], [n_by_fit], [n_by_cut], [n_to_use], fit_dict


# @app.callback(
#     Output('count-raw_4', 'children'),
#     Output('n-by-fit_4', 'children'),
#     Output('n-by-cut_4', 'children'),
#     Output('n-to-use_4', 'children'),
#     Output('data-adjust-aftershocks_4', 'data'),
#     Input('intensity-gteq_4', 'data'),
#     Input('Input-ef-range-low_4', 'value'),
#     Input('Input-ef-range-upp_4', 'value'),
#     Input('Input-interval-threshold_4', 'value'),
#     Input('select-one-of-raw-fit-cut_4', 'value'),
#     Input('n-raw-counts', 'data')
# )
# def set_threshold_regression_4(
#         dfi_dict, limit_low, limit_upp, interval_cutoff, select,
#         n_raw_counts):
#     n_raw, n_by_fit, n_by_cut, n_to_use, fit_dict = adjust_aftershocks(
#         4, dfi_dict, limit_low, limit_upp, interval_cutoff, select,
#         n_raw_counts)
#     return [n_raw], [n_by_fit], [n_by_cut], [n_to_use], fit_dict


# @app.callback(
#     Output('count-raw_5', 'children'),
#     Output('n-by-fit_5', 'children'),
#     Output('n-by-cut_5', 'children'),
#     Output('n-to-use_5', 'children'),
#     Output('data-adjust-aftershocks_5', 'data'),
#     Input('intensity-gteq_5', 'data'),
#     Input('Input-ef-range-low_5', 'value'),
#     Input('Input-ef-range-upp_5', 'value'),
#     Input('Input-interval-threshold_5', 'value'),
#     Input('select-one-of-raw-fit-cut_5', 'value'),
#     Input('n-raw-counts', 'data')
# )
# def set_threshold_regression_5(
#         dfi_dict, limit_low, limit_upp, interval_cutoff, select,
#         n_raw_counts):
#     n_raw, n_by_fit, n_by_cut, n_to_use, fit_dict = adjust_aftershocks(
#         5, dfi_dict, limit_low, limit_upp, interval_cutoff, select,
#         n_raw_counts)
#     return [n_raw], [n_by_fit], [n_by_cut], [n_to_use], fit_dict


# @app.callback(
#     Output('count-raw_6', 'children'),
#     Output('n-by-fit_6', 'children'),
#     Output('n-by-cut_6', 'children'),
#     Output('n-to-use_6', 'children'),
#     Output('data-adjust-aftershocks_6', 'data'),
#     Input('intensity-gteq_6', 'data'),
#     Input('Input-ef-range-low_6', 'value'),
#     Input('Input-ef-range-upp_6', 'value'),
#     Input('Input-interval-threshold_6', 'value'),
#     Input('select-one-of-raw-fit-cut_6', 'value'),
#     Input('n-raw-counts', 'data')
# )
# def set_threshold_regression_6(
#         dfi_dict, limit_low, limit_upp, interval_cutoff, select,
#         n_raw_counts):
#     n_raw, n_by_fit, n_by_cut, n_to_use, fit_dict = adjust_aftershocks(
#         6, dfi_dict, limit_low, limit_upp, interval_cutoff, select,
#         n_raw_counts)
#     return [n_raw], [n_by_fit], [n_by_cut], [n_to_use], fit_dict


# @app.callback(
#     Output('count-raw_7', 'children'),
#     Output('n-by-fit_7', 'children'),
#     Output('n-by-cut_7', 'children'),
#     Output('n-to-use_7', 'children'),
#     Output('data-adjust-aftershocks_7', 'data'),
#     Input('intensity-gteq_7', 'data'),
#     Input('Input-ef-range-low_7', 'value'),
#     Input('Input-ef-range-upp_7', 'value'),
#     Input('Input-interval-threshold_7', 'value'),
#     Input('select-one-of-raw-fit-cut_7', 'value'),
#     Input('n-raw-counts', 'data'),
# )
# def set_threshold_regression_7(
#         dfi_dict, limit_low, limit_upp, interval_cutoff, select,
#         n_raw_counts):
#     n_raw, n_by_fit, n_by_cut, n_to_use, fit_dict = adjust_aftershocks(
#         7, dfi_dict, limit_low, limit_upp, interval_cutoff, select,
#         n_raw_counts)
#     return [n_raw], [n_by_fit], [n_by_cut], [n_to_use], fit_dict


# @app.callback(
#     Output('conditions', 'children'),
#     Output('graphs', 'children'),
#     Output('graph-intensity-occurrence', 'children'),
#     Output('data-summary', 'data'),
#     Output('data-summary-table', 'children'),
#     Output('data-estimation', 'data'),
#     Output('data-estimation-table', 'children'),
#     Input('submit-button-state-all', 'n_clicks'),
#     Input('intensity-gteq_1', 'data'),
#     Input('intensity-gteq_2', 'data'),
#     Input('intensity-gteq_3', 'data'),
#     Input('intensity-gteq_4', 'data'),
#     Input('intensity-gteq_5', 'data'),
#     Input('intensity-gteq_6', 'data'),
#     Input('intensity-gteq_7', 'data'),
#     Input('data-adjust-aftershocks_1', 'data'),
#     Input('data-adjust-aftershocks_2', 'data'),
#     Input('data-adjust-aftershocks_3', 'data'),
#     Input('data-adjust-aftershocks_4', 'data'),
#     Input('data-adjust-aftershocks_5', 'data'),
#     Input('data-adjust-aftershocks_6', 'data'),
#     Input('data-adjust-aftershocks_7', 'data'),
#     Input('data-range-reg-int-occ', 'data'),
#     Input('station-meta-period', 'data'),
#     Input('intervals-linear-or-log', 'value')
# )
# def set_conditions(_, dfi_dict_1, dfi_dict_2, dfi_dict_3, dfi_dict_4,
#                    dfi_dict_5, dfi_dict_6, dfi_dict_7,
#                    df_aas_dict_1, df_aas_dict_2, df_aas_dict_3, df_aas_dict_4,
#                    df_aas_dict_5, df_aas_dict_6, df_aas_dict_7,
#                    range_reg_int_occ, station_meta_period_dict,
#                    interval_scale):
#     df_summary = pd.DataFrame()
#     for i in range(7):
#         df_ass_dict = eval('df_aas_dict_' + str(i + 1))
#         ser_to_add = pd.DataFrame.from_dict(df_ass_dict, orient='index')
#         df_to_add = pd.DataFrame(ser_to_add).transpose()
#         df_summary = pd.concat([df_summary, df_to_add])
#     df_summary = df_summary.reset_index(drop=True)
#     df_summary_dict = df_summary.to_dict()
#     summary_table = [html.Div([
#         dash_table.DataTable(
#             data=df_summary.to_dict('records'),
#             columns=[{'name': i, 'id': i} for i in df_summary.columns]
#         )
#     ])]
#     dfis = []
#     for i in range(7):
#         idx = i + 1
#         dfis.append(pd.DataFrame.from_dict(eval('dfi_dict_' + str(idx))))
#     msg = []
#     figs = []
#     fig1s = []
#     for i_int, intensity in enumerate([1, 2, 3, 4, 5, 6, 7]):
#         dfi = dfis[i_int]
#         fig = go.Figure()
#         fig.add_trace(go.Scatter(
#             x=dfi['interval'], y=dfi['suvf'], mode='markers',
#             marker=dict(color=px.colors.qualitative.T10[0]),
#             name="I >= " + str(intensity)
#         ))
#         slope = df_summary.at[i_int, 'ef_slope']
#         if slope is not None:
#             intercept_suvf = df_summary.at[i_int, 'ef_intercept'] / \
#                 df_summary.at[i_int, 'n_raw']
#             log10_intercept_suvf = np.log10(intercept_suvf)
#             xls = np.linspace(0, dfi['interval'].max())
#             yls = 10 ** (log10_intercept_suvf + slope * xls)
#             fig.add_trace(go.Scatter(
#                 x=xls, y=yls, mode='lines',
#                 line=dict(color=px.colors.qualitative.T10[1]),
#                 name="Fitted"
#             ))
#         fig.update_layout(
#             paper_bgcolor=cff.screen_background_color,
#             xaxis_title="Intervals [days]",
#             yaxis_title="1 - F",
#             autosize=False,
#             width=cff.fig_width,
#             height=240,
#             margin=dict(l=4/25 * cff.fig_width, b=4 / 25 * 240,
#                         r=1/25 * cff.fig_width, t=1 / 25 * 240),
#             legend=dict(x=.66, y=.98, font=dict(size=12)),
#         )
#         fig.update_yaxes(type='log')
#         if interval_scale == 'log':
#             fig.update_xaxes(type='log')
#         figs.append(dcc.Graph(figure=fig, style={'display': 'inline-block'}))

#     print(range_reg_int_occ)

#     df_to_use = df_summary.loc[:, ['intensity', 'n_to_use']]
#     df_to_use = df_to_use[df_to_use['intensity'] >= range_reg_int_occ['from']]
#     df_to_use = df_to_use[df_to_use['intensity'] <= range_reg_int_occ['to']]
#     y = np.array(df_to_use['n_to_use']).astype(np.float64)
#     log10y = np.log10(y)
#     x = np.array(df_to_use['intensity']).astype(np.float64)
#     res = scipy.stats.linregress((x, log10y))
#     xls = np.linspace(1, 7)
#     yls = 10 ** (res.intercept + res.slope * xls)
#     print(station_meta_period_dict[0])
#     analysis_from = datetime.datetime.strptime(
#         station_meta_period_dict[0]['analysis_from'], "%Y-%m-%d")
#     analysis_to = datetime.datetime.strptime(
#         station_meta_period_dict[0]['analysis_to'], "%Y-%m-%d")
#     duration = relativedelta(analysis_to, analysis_from).years
#     # duration = 1
#     print(duration)
#     est_5 = 10 ** (res.intercept + res.slope * 5) / duration
#     est_6 = 10 ** (res.intercept + res.slope * 6) / duration
#     est_7 = 10 ** (res.intercept + res.slope * 7) / duration
#     df_est = pd.DataFrame()
#     int_s = list(df_to_use['intensity'])
#     for i, intensity in enumerate(int_s):
#         idx_efl = 'efl_' + str(intensity)
#         idx_efu = 'efu_' + str(intensity)
#         idx_cut = 'cutoff_' + str(intensity)
#         idx_which = 'which' + str(intensity)
#         df_summary_sel = df_summary[df_summary['intensity'] == intensity]
#         df_summary_sel = df_summary_sel.reset_index(drop=True)
#         df_est.at[0, idx_efl] = df_summary.at[0, 'efl']
#         df_est.at[0, idx_efu] = df_summary.at[0, 'efu']
#         df_est.at[0, idx_cut] = df_summary.at[0, 'cutoff']
#         df_est.at[0, idx_cut] = df_summary.at[0, 'which']
#     df_est.at[0, 'intercept'] = round_to_k(res.intercept, 4)
#     df_est.at[0, 'slope'] = round_to_k(res.slope, 4)
#     df_est.at[0, 'rvalue'] = round_to_k(res.rvalue, 4)
#     df_est.at[0, 'est_5'] = round_to_k(est_5, 3)
#     df_est.at[0, 'est_6'] = round_to_k(est_6, 3)
#     df_est.at[0, 'est_7'] = round_to_k(est_7, 3)
#     df_est_dict = df_est.to_dict()
#     est_table = [html.Div([
#         dash_table.DataTable(
#             data=df_est.to_dict('records'),
#             columns=[{'name': i, 'id': i} for i in df_est.columns])
#     ])]
#     print(df_est)
#     fig1 = go.Figure()
#     fig1.add_trace(go.Scatter(
#         x=df_summary['intensity'], y=df_summary['n_raw'], mode='markers',
#         marker=dict(
#             symbol='square',
#             color=px.colors.qualitative.T10[0], size=10)
#     ))
#     fig1.add_trace(go.Scatter(
#         x=df_summary['intensity'], y=df_summary['n_by_cut'], mode='markers',
#         marker=dict(
#             symbol='cross', color=px.colors.qualitative.T10[3], size=10)
#     ))
#     fig1.add_trace(go.Scatter(
#         x=df_summary['intensity'], y=df_summary['n_by_fit'], mode='markers',
#         marker=dict(
#             symbol='circle', color=px.colors.qualitative.T10[2], size=10)
#     ))
#     fig1.add_trace(go.Scatter(
#         x=df_summary['intensity'], y=df_summary['n_to_use'], mode='markers',
#         marker=dict(
#             symbol='cross-thin', size=10, line=dict(width=2))
#     ))

#     fig1.add_trace(go.Scatter(
#         x=xls, y=yls, mode='lines',
#         line=dict(color=px.colors.qualitative.T10[1])
#     ))
#     fig1.update_layout(
#         paper_bgcolor=cff.screen_background_color,
#         xaxis_title="Intensity",
#         yaxis_title="Occurrence",
#         autosize=False,
#         width=cff.fig_width,
#         height=cff.fig_height,
#         margin=dict(l=4 / 25 * cff.fig_width, b=4 / 25 * 240,
#                     r=1 / 25 * cff.fig_width, t=1 / 25 * 240),
#         legend=dict(x=.66, y=.98, font=dict(size=12)),
#     )
#     fig1.update_yaxes(type='log')
#     fig1s.append(dcc.Graph(figure=fig1, style={'display': 'inline-block'}))

#     return msg, figs, fig1s, df_summary_dict, summary_table, df_est_dict, \
#            est_table
# # 
# # 


if __name__ == '__main__':
    app.run_server(debug=True)
