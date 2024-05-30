import datetime
# from dateutil.relativedelta import relativedelta
from dash import Dash, dcc, dash_table, html, Input, Output, State
from dash.dash_table.Format import Format, Scheme, Trim
# from collections import OrderedDict
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pandas as pd
import scipy.stats
import sys
sys.path.append("./")
sys.path.append("../")
sys.path.append("../../")
sys.path.append("../../../")
sys.path.append("../../../../")
import eqanalysis.src.eqa_takuyakawanishi.eqa as eqa
import eqanalysis.dashfiles.layouts.fig_template as fig_template


################################################################################
#  Global Constants and Variables
################################################################################

# DATABASE_START_DATE = '19190101'
# DATABASE_END_DATE = '20191231'
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
tcbf10_1= '#1170aa'	 # Cerulean/Blue
tcbf10_2 = '#fc7d0b'  # Pumpkin/Orange
tcbf10_3 = '#a3acb9'	# Dark Gray/Gray
tcbf10_4 = '#57606c'	# Mortar/Grey
tcbf10_5 = '#5Fa2ce'  # Picton Blue/Blue
tcbf10_6 = '#c85200'  # Tenne (Tawny)/Orange
tcbf10_7 = '#7b848f'  # Suva Grey/Grey
tcbf10_8 = '#a3cce9'  # Sail/Blue
tcbf10_9 = '#ffbc79'  # Macaroni And Cheese/Orange
tcbf10_10 = '#c8d0d9'  # Very Light Grey/Grey

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


def select_station(init_station):
    str_init_station = str(init_station)
    output = html.Div([
        html.H6(['Station Code']),
        dcc.Input(id='station', type='text', value=str_init_station,
                  style={'width': '40%', 
                         'background-color': cff.screen_background_color}),
        html.Button(id='select-station-submit-button-state', n_clicks=0,
                    children='Submit'),
        html.Div(id='station-data-msg'),
        html.Div([
            dash_table.DataTable(
                id="available-period",
                style_data={'backgroundColor':cff.screen_background_color},
            ),
        ], style={"margin-top": "-.5rem", "margin-bottom":".5rem",
                  "padding-right": '12px'})
    ])
    return output


def set_datetime(idx):
    data_init = [["From", 1996, 4, 1, 12, 0, 0],
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
                style_data={'backgroundColor':cff.screen_background_color},            
            ),    
        ], style={'padding-right': '12px'}),
        html.Button(id='set-period-submit-button-state', n_clicks=0,
            children='Submit'),
    ])
    return output


def select_fitting_intensities(init_label, value):
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
            dcc.Dropdown(
                [1, 2, 3], value, id='seleft-fit-intensity-low',
                style={'background-color': cff.screen_background_color}
            ),
            html.Button(id='button-select-fit-intensity', n_clicks=0,
                children='Submit', style={'width': '40%'}),
        ], style={'display': 'flex', 'margin-top': '-.5rem',
                  'margin-bottom': '.5rem'})
    ])
    return output


def set_range_fit_intervals(idx, low, upp, factor_user):
    factor_user = np.round(factor_user, 3)
    data = [['Range', low, upp]]
    df = pd.DataFrame(data, columns=['Your fit', 'low', 'upp'])
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
                        dict(id='Your fit', name='Your fit'),
                        dict(id='low', name='low', type='numeric', 
                            format=Format(precision=0, scheme=Scheme.fixed)),
                        dict(id='upp', name='upp', type='numeric', 
                            format=Format(precision=0, scheme=Scheme.fixed))
                    ],
                    data=df.to_dict("records"),
                    persistence=True,
                    persistence_type='memory',
                    persisted_props = ['columns.name', 'data'],
                    # style_cell_conditional=[
                    #     {'if': {'column_id': 'Your fitting'},'width': '35%'},
                    # ]
                    style_data={'backgroundColor':cff.screen_background_color},
                ),
            ], style={
                'display': 'inline-block', 'width': '80%', 
                'vertical-align': 'bottom'}
            ),
            html.Div([
                html.Button(id='button-interval-fit-reset_' + str(idx), n_clicks=0,
                    children='Reset', 
                    style={
                        'width':'100%', 'display': 'inline-block',
                        'vertical-align': 'top'}
                ),
                html.Button(id='button-interval-fit-range_' + str(idx), n_clicks=0,
                    children='Fit', 
                    style={
                        'width':'100%', 'display': 'inline-block',
                        'vertical-align': 'bottom'}
                ),
            ], style={'display': 'inline-block', 'width': '20%'})
        ]),
        html.Div([
            html.Div(
                "Your Factor", 
                style={'display': 'inline-block', 'width':'35%',
                    'vertical-align': 'bottom'}
            ),
            dcc.Input(id='factor-user-temp_' + str(idx), type='number', 
                      value=factor_user,
                    style={'width': '45%', 'display': 'inline-block',
                           'background-color': cff.screen_background_color},
                    debounce=True,
            ),
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


def raw_and_corrected_riro_table(dict_tccf):
    abbrs = [
        "INTST: Intensity",
        "RRO: Raw rates of occurrences (RO)",
        "PF: Factor by predefined process",
        "PFCRO: Corrected RO with PF",
        "UF: User detfined correction factor",
        "UFCRO: Corrected RO with UF" 
    ]
    output = html.Div([
        dash_table.DataTable(
            editable=False,
            data=dict_tccf,
            columns=[
                dict(id='INTST', name='INTST', type='numeric',
                     format=Format(precision=0)),
                dict(id='RRO', name='RRO', type='numeric',
                     format=Format(precision=3)),
                dict(id='PF', name='PF', type='numeric',
                     format=Format(precision=3)),                
                dict(id='PFCRO', name='PFCRO', type='numeric',
                     format=Format(precision=3)),                
                dict(id='UF', name='UF', type='numeric',
                     format=Format(precision=3)),                
                dict(id='UFCRO', name='UFCRO', type='numeric',
                     format=Format(precision=3)),                
            ],
            style_data={'backgroundColor':cff.screen_background_color},
        ),
        html.Div([
            "INTST: Intensity", html.Br(),
            "RRO: Raw rate of occurrence (RO)", html.Br(),
            "PF: Correction factor by predefined process", html.Br(),
            "PFCRO: Corrected RO with PF", html.Br(),
            "UF: Correction factor defined by user", html.Br(),
            "UFCRO: Corrected RO with UF"
        ], style={'font-size': '0.8em'})
    ])
    return output


def show_user_defined_fittings(dict_fittings_user):
    output = html.Div([
        dash_table.DataTable(
            editable=False,
            data=dict_fittings_user,
            columns=[
                dict(id='intensity', name='intensity', type='numeric',
                     format=Format(precision=1)),
                dict(id='ro', name='ro', type='numeric',
                     format=Format(precision=3)),
                dict(id='factor', name='factor', type='numeric',
                     format=Format(precision=3)),                
                dict(id='corrected', name='corrected', type='numeric',
                     format=Format(precision=3)),                
                dict(id='fit_low', name='fit_low', type='numeric',
                     format=Format(precision=3)),                
                dict(id='fit_upp', name='fit_upp', type='numeric',
                     format=Format(precision=3)),                
                dict(id='intercept', name='intercept', type='numeric',
                     format=Format(precision=3)),                
                dict(id='slope', name='slope', type='numeric',
                     format=Format(precision=3)),                
                dict(id='rvalue', name='rvalue', type='numeric',
                     format=Format(precision=3)),                
            ],
            style_data={'backgroundColor':cff.screen_background_color},
        ),
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


################################################################################
#   Preparation and Layout
################################################################################


meta = pd.read_csv(FILE2READ_META)
cff = fig_template.FigSettings()
cfd = fig_template.DashSettings()
cfe = eqa.Settings()
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
                    select_station(3900130),
                    html.Br(),
                    set_datetime(0),                    
                    dcc.Store(id='station-prime'),
                    dcc.Store(id='available-period_dict'),
                    dcc.Store(id='set-period'),
                    html.Br(),
                    select_fitting_intensities("Yes", 2),
                    dcc.Store(id='intensity-lowest-fit'),
                    dcc.Store(id='regression-corrected-params')
                ], style={'margin': '2px'})
            ], width={'size': 10}, sm=8, md=6, lg=4, xxl=3
            ),
            dbc.Col([
                dcc.Store(id='temporal-clustering-correction-factors'),
                dcc.Store(id='riro-data'),
                # dcc.Store(id='riro-summary-data'),
                dcc.Store(id='riro-regress'),
                dcc.Store(id='fittings'),
                dcc.Store(id='fittings-user'),
                dcc.Store(id='preset-and-user-defined-riro'),
                dcc.Store(id='regression-corrected'),
                dcc.Store(id='intervals_1-data'),
                dcc.Store(id='intervals_2-data'),
                dcc.Store(id='intervals_3-data'),
                dcc.Store(id='intervals_4-data'),
                dcc.Store(id='intervals_5-data'),
                dcc.Store(id='intervals_6-data'),
                dcc.Store(id='intervals_7-data'),
                dcc.Store(id='fittings_1-data'),
                dcc.Store(id='fittings_2-data'),
                dcc.Store(id='fittings_3-data'),
                dcc.Store(id='fittings_4-data'),
                dcc.Store(id='fittings_5-data'),
                dcc.Store(id='fittings_6-data'),
                dcc.Store(id='fittings_7-data'),
                # html.Br(),
                # html.Div(id='user-defined-fittings'),
                html.Br(),
                html.H5("Relationship between Intensities and Rates of Occurrences (RIRO)"),
                html.Div([
                    html.Div([
                        html.H6("Raw and corrected RIRO"),
                        html.Div(id='raw-corrected-riro-datatable'),
                        html.Br(),
                        html.Br(),
                    ], style={
                        'width':'312px', 'margin':'2px',
                        'display':'inline-block',
                        'padding-right': '24px', 
                        'vertical-align': 'top'},
                    ),
                    html.Div([
                        html.H6("RIRO and ERO6+"),
                        html.Div(id='riro-figure'),
                        # html.Br(),
                        html.Br(),
                        html.Br(),
                    ], style={'display': 'inline-block', 'vertical-align':'top'}),
                    html.Div([
                        html.H6("Fitting lines and ERO6+"),
                        html.Div(id='regression-riro-table'),
                        html.Br(),
                        html.Br(),
                    ], style={
                        'width':'312px', 'margin':'2px',
                        'display':'inline-block',
                        'padding-right': '24px', 
                        'vertical-align': 'top'},
                    ),
                ]),      
                html.H5("Intervals"),
                html.Div([
                    html.Div([
                        html.H6("Intensity >= 1"),
                        html.Div([
                            html.Div(
                                id='setting-range-fittings_1',
                            ),
                        ]),
                        html.Br(),
                        html.Div(id='intervals_1-figure', style={'display': 'inline-block', 'width': '316px'}),
                        html.Br(),
                        html.Br(),
                        html.Br(),
                        ], style={'display': 'inline-block', 'width': '316px'}
                    ),
                    html.Div([
                        html.H6("Intensity >= 2"),
                        html.Div([
                            html.Div(
                                id='setting-range-fittings_2',
                            ),
                        ]),                        
                        html.Br(),
                        html.Div(id='intervals_2-figure', style={'display': 'inline-block', 'width': '316px'}),
                        html.Br(),
                        html.Br(),
                        html.Br(),
                        ], style={'display': 'inline-block', 'width': '316px'}
                    ),
                    html.Div([
                        html.H6("Intensity >= 3"),
                        html.Div([
                            html.Div(
                                id='setting-range-fittings_3',
                            ),
                        ]),                        
                        html.Br(),
                        html.Div(id='intervals_3-figure', style={'display': 'inline-block', 'width': '316px'}),
                        html.Br(),
                        html.Br(),
                        html.Br(),
                        ], style={'display': 'inline-block', 'width': '316px'}
                    ),
                    html.Div([
                        html.H6("Intensity >= 4"),
                        html.Div([
                            html.Div(
                                id='setting-range-fittings_4',
                            ),
                        ]),                        
                        html.Br(),
                        html.Div(id='intervals_4-figure', style={'display': 'inline-block', 'width': '316px'}),
                        html.Br(),
                        html.Br(),
                        html.Br(),
                        ], style={'display': 'inline-block', 'width': '316px'}
                    ),                    
                    html.Div([
                        html.H6("Intensity >= 5"),
                        html.Div([
                            html.Div(
                                id='setting-range-fittings_5',
                            ),
                        ]),                        html.Br(),
                        html.Div(id='intervals_5-figure', style={'display': 'inline-block', 'width': '316px'}),
                        html.Br(),
                        html.Br(),
                        html.Br(),
                        ], style={'display': 'inline-block', 'width': '316px'}
                    ),                    
                    html.Div([
                        html.H6("Intensity >= 6"),
                        html.Div([
                            html.Div(
                                id='setting-range-fittings_6',
                            ),
                        ]),                        
                        html.Br(),
                        html.Div(id='intervals_6-figure', style={'display': 'inline-block', 'width': '316px'}),
                        html.Br(),
                        html.Br(),
                        html.Br(),
                        ], style={'display': 'inline-block', 'width': '316px'}
                    ),
                    html.Div([
                        html.H6("Intensity >= 7"),
                        html.Div([
                            html.Div(
                                id='setting-range-fittings_7',
                            ),
                        ]),                        
                        html.Br(),
                        html.Div(id='intervals_7-figure', style={'display': 'inline-block', 'width': '316px'}),
                        html.Br(),
                        html.Br(),
                        html.Br(),
                        ], style={'display': 'inline-block'}
                    ),
                ]),                    
            ], width={'size': 12}, lg=8, xxl=9)
        ]),
    ], fluid=False)
], style=cfd.global_style, fluid=True)


################################################################################
#
#   Callbacks
#
################################################################################

################################################################################
#  Sidebar items
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
    # print(data)
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


################################################################################
#  Put riro and intervals data to dcc.Stores
################################################################################


@app.callback(
    Output('riro-data', 'data'),
    Output('fittings', 'data'),
    Output('fittings-user', 'data'),
    # Output('riro-summary-data', 'data'),
    Output('intervals_1-data', 'data'),
    Output('intervals_2-data', 'data'),
    Output('intervals_3-data', 'data'),
    Output('intervals_4-data', 'data'),
    Output('intervals_5-data', 'data'),
    Output('intervals_6-data', 'data'),
    Output('intervals_7-data', 'data'),
    Output('fittings_1-data', 'data'),
    Output('fittings_2-data', 'data'),
    Output('fittings_3-data', 'data'),
    Output('fittings_4-data', 'data'),
    Output('fittings_5-data', 'data'),
    Output('fittings_6-data', 'data'),
    Output('fittings_7-data', 'data'),
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
        if df_intervals is not None:
            dicts_intervals.append(df_intervals.to_dict('records'))
        else:
            dicts_intervals.append(None)

    df_fittings = df_corrected.copy()
    df_fittings["fit_low"] = [2 ** (intm1 + 2) for intm1 in range(7)]
    df_fittings = df_fittings.rename(
        columns={"interval_1st_fit_upp": "fit_upp"})
    df_fittings = df_fittings[[
        "intensity", "ro", "factor", "corrected", "fit_low", "fit_upp", 
        "intercept", "slope", "rvalue"]]
    # print("df_fittings")
    # print(df_fittings)
    dicts_fittings = []
    for i_int in range(7):
        df_fittings_i = df_fittings.iloc[i_int, :]
        dict_i = df_fittings_i.to_dict()
        dicts_fittings.append(dict_i)
    summary = pd.DataFrame(summary_corrected).transpose()
    summary_dict = summary.to_dict('records')
    corrected_dict = df_corrected.to_dict('records')
    fittings_dict = df_fittings.to_dict('records')
    return corrected_dict, fittings_dict, fittings_dict,\
        dicts_intervals[0],\
        dicts_intervals[1], dicts_intervals[2], dicts_intervals[3],\
        dicts_intervals[4], dicts_intervals[5], dicts_intervals[6],\
        dicts_fittings[0], dicts_fittings[1], dicts_fittings[2],\
        dicts_fittings[3], dicts_fittings[4], dicts_fittings[5],\
        dicts_fittings[6]
@app.callback(
    Output('regression-corrected-params', 'data'),
    Input('button-select-fit-intensity', 'n_clicks'),
    State('draw-or-not-reg-corrected', 'value'),
    State('seleft-fit-intensity-low', 'value'),
)
def select_fitting_intensity_lower_bound(_, draw_correct, value):
    dict = {"Draw": draw_correct, "lowestint": int(value)}
    return dict


################################################################################
#  Main column items
################################################################################


# @app.callback(
#     Output('user-defined-fittings', 'children'),
#     Input('fittings-user', 'data')
# )
# def display_user_defined_fittings(dict_fittings_user):
#     return show_user_defined_fittings(dict_fittings_user)


@app.callback(
    Output('temporal-clustering-correction-factors', 'data'),
    Input('fittings', 'data'),
    Input('fittings-user', 'data')
)
def prepare_tcc_factors(dict_fittings, dict_fittings_user):
    df_fittings = pd.DataFrame.from_dict(dict_fittings)
    df_fittings_user = pd.DataFrame.from_dict(dict_fittings_user)
    df_tccf = pd.DataFrame()
    df_tccf["INTST"] = df_fittings["intensity"]
    df_tccf["RRO"] = df_fittings["ro"]
    df_tccf["PF"] = df_fittings["factor"]
    df_tccf["PFCRO"] = df_fittings["factor"] * df_fittings["ro"]
    df_tccf["UF"] = df_fittings_user["factor"]
    df_tccf["UFCRO"] = df_fittings_user["corrected"]
    dict_tccf = df_tccf.to_dict('records')
    return dict_tccf


@app.callback(
    Output('raw-corrected-riro-datatable', 'children'),
    Input('temporal-clustering-correction-factors', 'data')
)
def display_rcriro_dttbl(dict_tccf):
    return raw_and_corrected_riro_table(dict_tccf)


@app.callback(
    Output('regression-riro-table', 'children'),
    Input('riro-regress', 'data')
)
def estimate_ero6plus(dict_reg):
    df_reg = pd.DataFrame.from_dict(dict_reg)
    output = html.Div([
        dash_table.DataTable(
            editable=False,
            data=dict_reg,
            columns=[
                dict(id='version', name='RO', type='numeric',
                     format=Format(precision=0)),
                dict(id='intercept', name='INTCP', type='numeric',
                     format=Format(precision=3)),
                dict(id='slope', name='Slope', type='numeric',
                     format=Format(precision=3)),                
                dict(id='rvalue', name='rvalue', type='numeric',
                     format=Format(precision=3)),                
                dict(id='ERO6+', name='ERO6+', type='numeric',
                     format=Format(precision=3)),                
            ],
            style_data={'backgroundColor':cff.screen_background_color},
        ),
        html.Div([
            "INTCP: Intercept", html.Br(),
            "ERO6+: Estimated rates of cccurrences of ", html.Br(),
            "       intensity 6 plus earthquakes", html.Br(),
        ], style={'font-size': '0.8em'})

    ])
    return output
#
# TODO, following looks like redandant, check if we can delete it.
#
# @app.callback(
#     Output('regression-corrected', 'data'),
#     Input('regression-corrected-params', 'data'),
#     Input('riro-data', 'data'),
# )
# def regression_lines(corrected_params, corrected_data):
#     if corrected_params["Draw"] == "No":
#         return None
#     else:
#         df_corrected = pd.DataFrame.from_dict(corrected_data)
#         corrected = df_corrected['corrected'].values
#         corrected = corrected[corrected > 0]
#         riro = eqa.IROR(corrected)
#         df = pd.DataFrame()
#         li = corrected_params["lowestint"]
#         res = riro.find_iror(li)
#         if res is not None:
#             df.at[0, 'attribute'] = 'corrected'
#             df.at[0, 'leastint'] = li
#             df.at[0, 'slope'] = res.slope
#             df.at[0, 'intercept'] = res.intercept
#             df.at[0, 'rvalue'] = res.rvalue
#             df.at[0, 'pvalue'] = res.pvalue
#     return df.to_dict('records')


################################################################################
#  Figures
################################################################################
#
# Can be organized.
#
@app.callback(
    Output('riro-regress', 'data'),
    Input('temporal-clustering-correction-factors', 'data'),
    Input('regression-corrected-params', 'data'),
)
def find_regression_lines_ro(dict_tccf, reg_cor_params):
    df = pd.DataFrame.from_dict(dict_tccf)
    # print(df)
    dfsel_raw = df[df["RRO"] > 0]
    dfsel_pf = df[df["PFCRO"] > 0]
    dfsel_uf = df[df["UFCRO"] > 0]
    # print(dfsel_uf)
    li = reg_cor_params["lowestint"]
    dfsel_raw = dfsel_raw.loc[li - 1:]
    dfsel_pf = dfsel_pf.loc[li - 1:]
    dfsel_uf = dfsel_uf.loc[li - 1:]
    reg_raw = scipy.stats.linregress(
        dfsel_raw["INTST"],
        np.log10(dfsel_raw["RRO"]))
    reg_pf = scipy.stats.linregress(
        dfsel_pf["INTST"],
        np.log10(dfsel_pf["PFCRO"]))
    reg_uf = scipy.stats.linregress(
        dfsel_uf["INTST"], 
        np.log10(dfsel_uf["UFCRO"]))
    df_regs = pd.DataFrame()
    df_regs["version"] = ["RRO", "PFCRO", "UFCRO"]
    df_regs["intercept"] = [
        reg_raw.intercept, reg_pf.intercept, reg_uf.intercept]
    df_regs["slope"] = [
        reg_raw.slope, reg_pf.slope, reg_uf.slope]
    df_regs["rvalue"] = [
        reg_raw.rvalue, reg_pf.rvalue, reg_uf.rvalue]
    df_regs["ERO6+"] = [
        10 ** (reg_raw.intercept + reg_raw.slope * 6.5),
        10 ** (reg_pf.intercept + reg_pf.slope * 6.5),
        10 ** (reg_uf.intercept + reg_uf.slope * 6.5)
    ]
    dict_regs = df_regs.to_dict('records')
    return dict_regs


@app.callback(
    Output('riro-figure', 'children'),
    Input('temporal-clustering-correction-factors', 'data'),
    Input('regression-corrected-params', 'data'),
    Input('riro-regress', 'data')
    # Input('regression-corrected', 'data')
)
def draw_riro(dict_tccf, reg_cor_params, dict_regs):
    df = pd.DataFrame.from_dict(dict_tccf)
    df_regs = pd.DataFrame.from_dict(dict_regs)
    print(df_regs)
    df_sel = df[df["UFCRO"] > 0]

    reg_uf = scipy.stats.linregress(
        df_sel["INTST"], np.log10(df_sel["UFCRO"]))
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['INTST'], y=df['RRO'], mode="markers",
        name="Raw",
        marker=dict(size=10, symbol="square", color=tcbf10_1)
    ))
    # fig.add_trace(go.Scatter(
    #     x=df['INTST'], y=df['PFCRO'], mode="markers",
    #     name="Corrected PF",
    #     marker=dict(size=10, symbol="diamond", color=tcbf10_2)
    # ))
    fig.add_trace(go.Scatter(
        x=df['INTST'], y=df['UFCRO'], mode="markers",
        name="Corrected UF",
        marker=dict(size=10, symbol="circle", color="black")
    ))
    if reg_cor_params["Draw"] == "Yes":    
        li = reg_cor_params["lowestint"]
        intercept = df_regs.at[2, "intercept"]
        slope = df_regs.at[2, "slope"]
        xrs = np.linspace(li - .2, 7.2)
        yrs = 10 ** (intercept + slope * xrs)
        fig.add_traces(go.Scatter(
            x=xrs, y=yrs, name="Reg. corrected UF",
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
        yaxis_title="Rates of occurrences [1/year]"
    )
    fig.update_yaxes(type="log")
    fig.update_layout(legend_tracegroupgap=0)
    fig.update_layout(paper_bgcolor=cff.screen_background_color)
    output = html.Div([
        dcc.Graph(figure=fig, style={'margin':'auto'})
    ], style={'width': '312px', 'margin': '2`px'})
    return output


# @app.callback(
#     Output('riro-figure', 'children'),
#     Input('riro-data', 'data'),
#     Input('regression-corrected-params', 'data'),
#     Input('regression-corrected', 'data')
# )
# def draw_riro(corrected_data, reg_cor_params, reg_corrected):
#     df = pd.DataFrame.from_dict(corrected_data)
#     df_reg_corrected = pd.DataFrame.from_dict(reg_corrected)
#     regression = reg_cor_params["Draw"]
#     fig = go.Figure()
#     fig.add_trace(go.Scatter(
#         x=df['intensity'], y=df['ro'], mode="markers",
#         name="Raw",
#         marker=dict(size=10, symbol="square", color=cud_skyblue)
#     ))
#     fig.add_trace(go.Scatter(
#         x=df['intensity'], y=df['corrected'], mode="markers",
#         name="Corrected",
#         marker=dict(size=10, symbol="circle", color="black")
#     ))
#     if regression == "Yes":
#         li = reg_cor_params["lowestint"]
#         xrs = np.linspace(li - .2, 7.2)
#         yrs = 10 ** (
#             df_reg_corrected.at[0, 'intercept'] + \
#                 df_reg_corrected.at[0, 'slope'] * xrs
#         )
#         fig.add_traces(go.Scatter(
#             x=xrs, y=yrs, name="Reg. corrected",
#             mode="lines",
#             line=dict(width=.5, color="black")
#         ))

#     # 15 + 54 + 3 = 72
#     # 12 + 54 + 3 = 69
#     mlt = 13/3
#     fig.update_layout(
#         autosize=False,
#         width=72 * mlt,
#         height=69 * mlt,
#         margin=dict(
#             l=15 * mlt, r=3 * mlt, t=3 * mlt, b=12 * mlt, pad=0
#         ),
#         legend=dict(
#             x=1, y=56/54, xanchor='right', yanchor='top',
#             font=dict(family="Helvetica", size=10, color="black"),
#             itemsizing='trace',
#             tracegroupgap=0,
#         ),
#         # legend_tracegroupgap=20,
#         xaxis_title="Intensities",
#         yaxis_title="Rates of occurrences [1/year]"
#     )
#     fig.update_yaxes(type="log")
#     fig.update_layout(legend_tracegroupgap=0)
#     fig.update_layout(paper_bgcolor=cff.screen_background_color)
#     output = html.Div([
#         dcc.Graph(figure=fig, style={'margin':'auto'})
#     ], style={'width': '312px', 'margin': '2`px'})
#     return output


def draw_interval_survival_regress(
        df_intervals, fit_upp, intercept, slope, factor, i_int):
    xrs = np.linspace(0, fit_upp)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_intervals['interval'], y=df_intervals['suvf'], mode='markers',
        marker=dict(size=8, symbol='circle', color=cud_blue),
        name='intensity ' + str(i_int + 1),
        showlegend=False))
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
        yaxis_title=r"$(1 - F)^{\wedge}$",
        xaxis_title='intervals [days]')
    fig.add_annotation(text="Intensity >= " + str(i_int + 1),
        xref="x domain", yref="y domain",
        x=0.98, y=0.98, showarrow=False, xanchor='right',
        yanchor='top')
    fig.add_annotation(text="Factor = {:.3f}".format(factor),
        xref="x domain", yref="y domain",
        x=0.98, y=0.88, showarrow=False, xanchor='right',
        yanchor='top')
    fig.update_yaxes(type="log")
    fig.update_layout(paper_bgcolor=cff.screen_background_color)
    return fig


################################################################################
#   Functions manipulating fitting for various intensities
################################################################################


def show_fitting_range_for_i(dict_fittings, intensity):
    df_fittings = pd.DataFrame.from_dict(dict_fittings)
    ser_fittings_i = df_fittings.iloc[intensity - 1].copy()
    low = ser_fittings_i["fit_low"]
    upp = ser_fittings_i["fit_upp"]
    factor = ser_fittings_i["factor"]
    output = html.Div(
        set_range_fit_intervals(intensity, low, upp, factor)
    )
    factor = np.round(factor, 3)
    return output


def fit_by_usr_i(dict_range, dict_intervals, dict_fittings, intensity):
    df_range = pd.DataFrame.from_dict(dict_range)
    df_intervals = pd.DataFrame.from_dict(dict_intervals)
    df_fittings = pd.DataFrame.from_dict(dict_fittings)
    fit_i = df_fittings.iloc[intensity - 1].copy()    
    # print("fit_i for intensity ", intensity, type(fit_i))
    # print(fit_i)
    low = df_range.at[0, "low"]
    upp = df_range.at[0, "upp"]
    case = 0
    if df_intervals is not None:
        if not df_intervals.empty:
            df_sel = df_intervals[df_intervals["interval"] > low]
            df_sel = df_sel[df_sel["interval"] < upp]
            if len(df_sel) >= 2:
                case = 1
    if case == 1:
        intervals = df_sel["interval"]
        log10suvf = np.log10(df_sel["suvf"])
        res = scipy.stats.linregress(intervals, log10suvf)
        factor = 10 ** res.intercept
        factor = np.round(factor, 3)
        fit_i["factor"] = 10 ** (res.intercept)
        fit_i["corrected"] = fit_i["ro"] * fit_i["factor"]
        fit_i["fit_low"] = low
        fit_i["fit_upp"] = upp
        fit_i["intercept"] = res.intercept
        fit_i["slope"] = res.slope
        fit_i["rvalue"] = res.rvalue
    else:
        factor = fit_i["factor"]
        fit_i["corrected"] = np.nan
        fit_i["fit_low"] = low
        fit_i["fit_upp"] = upp
        fit_i["intercept"] = np.nan
        fit_i["slope"] = np.nan
        fit_i["rvalue"] = np.nan
    
    dict_fittings_i = fit_i.to_dict()
    return dict_fittings_i, factor


def reset_fitting_i(dict_fittings, intensity):
    df_fittings = pd.DataFrame.from_dict(dict_fittings)
    ser_fittings_i = df_fittings.iloc[intensity - 1].copy()
    dict_fittings_i = ser_fittings_i.to_dict()
    low = np.round(ser_fittings_i["fit_low"], 0)
    upp = np.round(ser_fittings_i["fit_upp"], 0)
    factor = np.round(ser_fittings_i["factor"], 3)
    data = [['Range', low, upp]]
    df = pd.DataFrame(data, columns=['Your fit', 'low', 'upp'])
    dict_range = df.to_dict('records')
    return dict_fittings_i, dict_range, factor


def draw_intervals_i(dict_intervals_i, dict_fittings_i, intensity):
    df_intervals_i = pd.DataFrame.from_dict(dict_intervals_i)
    df_fittings_i = pd.Series(dict_fittings_i)
    case = 0
    if df_intervals_i is not None:
        if not df_intervals_i.empty:
            case = 1
    if case == 1:
        # print(df_fittings_i)
        fit_low = df_fittings_i["fit_low"]
        fit_upp = df_fittings_i["fit_upp"]
        slope = df_fittings_i["slope"]
        intercept = df_fittings_i["intercept"]
        factor = df_fittings_i["factor"]
        fig = draw_interval_survival_regress(
            df_intervals_i, fit_upp, intercept, slope, factor, intensity - 1)
        i_int = 0
        fig_output = html.Div([
            html.Div([
                dcc.Graph(figure=fig, style={'margin':'auto'},
                    mathjax=True)
            ], style={'display': 'inline-block', 'vertical-align': 'bottom'}),
            html.Br(),
        ])
    else:
        fig_output = html.Div([
            html.Div([
                html.P(["No intervals to show."])
            ], style={'display': 'inline-block', 'vertical-align': 'bottom'}),
            html.Br(),
        ])

    return fig_output


def use_user_defined_correction_factor_i(
        dict_fittings_user, dict_fittings_i, factor_user_temp_i, intensity):
    df_fittings_user = pd.DataFrame.from_dict(dict_fittings_user)
    ser_fittings_i = pd.Series(dict_fittings_i)
    if not np.isnan(ser_fittings_i["factor"]):
        if factor_user_temp_i is not None:
            if abs(factor_user_temp_i - ser_fittings_i["factor"]) > 1e-3:
                ser_fittings_i["factor"] = factor_user_temp_i    
                ser_fittings_i["corrected"] = ser_fittings_i["ro"] * factor_user_temp_i
                ser_fittings_i["fit_upp"] = np.nan
                ser_fittings_i["intercept"] = np.nan
                ser_fittings_i["slope"] = np.nan
                ser_fittings_i["rvalue"] = np.nan
    df_fittings_user.iloc[intensity - 1, :] = ser_fittings_i.values
    dict_fittings_user = df_fittings_user.to_dict('records')
    return dict_fittings_user


################################################################################
#   Callbacks for each intensity
################################################################################
#
# Intensity 1
#
@app.callback(
    Output('setting-range-fittings_1', 'children'),
    Input('fittings', 'data')
)
def show_fitting_range_1(dict_fittings):
    return show_fitting_range_for_i(dict_fittings, 1)


@app.callback(
    Output('fittings_1-data', 'data', allow_duplicate=True),
    Output('factor-user-temp_1', 'value', allow_duplicate=True),
    Input('button-interval-fit-range_1', 'n_clicks'),
    State('interval-fit-range_1', 'data'),
    State('intervals_1-data', 'data'),
    State('fittings', 'data'),
    prevent_initial_call=True
)
def fit_by_user_1(_, dict_range, dict_intervals, dict_fittings):
    return fit_by_usr_i(dict_range, dict_intervals, dict_fittings, 1)


@app.callback(
    Output('fittings_1-data', 'data', allow_duplicate=True),
    Output('interval-fit-range_1', 'data'),
    Output('factor-user-temp_1', 'value', allow_duplicate=True),
    Input('button-interval-fit-reset_1', 'n_clicks'),
    State('fittings', 'data'),
    prevent_initial_call=True
)
def reset_fitting_1(_, dict_fittings):
    return reset_fitting_i(dict_fittings, 1)


@app.callback(
    Output('intervals_1-figure', 'children'),
    Input('intervals_1-data', 'data'),
    Input('fittings_1-data', 'data'),
)
def draw_intervals_1(dict_intervals_1, dict_fittings_1):
    return draw_intervals_i(dict_intervals_1, dict_fittings_1, 1)


@app.callback(
    Output('fittings-user', 'data', allow_duplicate=True),
    Input('button-use-factor-user_1', 'n_clicks'),
    State('fittings-user', 'data'),
    State('fittings_1-data', 'data'),
    State('factor-user-temp_1', 'value'),
    prevent_initial_call=True
)
def use_user_defined_correction_factor(
    _, dict_fittings_user, dict_fittings_1, factor_user_temp_1):
    return use_user_defined_correction_factor_i(
        dict_fittings_user, dict_fittings_1, factor_user_temp_1, 1)


#
# Intensity 2
#
@app.callback(
    Output('setting-range-fittings_2', 'children'),
    Input('fittings', 'data')
)
def show_fitting_range_2(dict_fittings):
    return show_fitting_range_for_i(dict_fittings, 2)


@app.callback(
    Output('fittings_2-data', 'data', allow_duplicate=True),
    Output('factor-user-temp_2', 'value', allow_duplicate=True),
    Input('button-interval-fit-range_2', 'n_clicks'),
    State('interval-fit-range_2', 'data'),
    State('intervals_2-data', 'data'),
    State('fittings', 'data'),
    prevent_initial_call=True
)
def fit_by_user_2(_, dict_range, dict_intervals, dict_fittings):
    return fit_by_usr_i(dict_range, dict_intervals, dict_fittings, 2)


@app.callback(
    Output('fittings_2-data', 'data', allow_duplicate=True),
    Output('interval-fit-range_2', 'data'),
    Output('factor-user-temp_2', 'value', allow_duplicate=True),
    Input('button-interval-fit-reset_2', 'n_clicks'),
    State('fittings', 'data'),
    prevent_initial_call=True
)
def reset_fitting_2(_, dict_fittings):
    return reset_fitting_i(dict_fittings, 2)


@app.callback(
    Output('intervals_2-figure', 'children'),
    Input('intervals_2-data', 'data'),
    Input('fittings_2-data', 'data'),
)
def draw_intervals_2(dict_intervals_2, dict_fittings_2):
    return draw_intervals_i(dict_intervals_2, dict_fittings_2, 2)


@app.callback(
    Output('fittings-user', 'data', allow_duplicate=True),
    Input('button-use-factor-user_2', 'n_clicks'),
    State('fittings-user', 'data'),
    State('fittings_2-data', 'data'),
    State('factor-user-temp_2', 'value'),
    prevent_initial_call=True
)
def use_user_defined_correction_factor(
    _, dict_fittings_user, dict_fittings_2, factor_user_temp_2):
    return use_user_defined_correction_factor_i(
        dict_fittings_user, dict_fittings_2, factor_user_temp_2, 2)


#
# Intensity 3
#
@app.callback(
    Output('setting-range-fittings_3', 'children'),
    Input('fittings', 'data')
)
def show_fitting_range_3(dict_fittings):
    return show_fitting_range_for_i(dict_fittings, 3)


@app.callback(
    Output('fittings_3-data', 'data', allow_duplicate=True),
    Output('factor-user-temp_3', 'value', allow_duplicate=True),
    Input('button-interval-fit-range_3', 'n_clicks'),
    State('interval-fit-range_3', 'data'),
    State('intervals_3-data', 'data'),
    State('fittings', 'data'),
    prevent_initial_call=True
)
def fit_by_user_3(_, dict_range, dict_intervals, dict_fittings):
    return fit_by_usr_i(dict_range, dict_intervals, dict_fittings, 3)


@app.callback(
    Output('fittings_3-data', 'data', allow_duplicate=True),
    Output('interval-fit-range_3', 'data'),
    Output('factor-user-temp_3', 'value', allow_duplicate=True),
    Input('button-interval-fit-reset_3', 'n_clicks'),
    State('fittings', 'data'),
    prevent_initial_call=True
)
def reset_fitting_3(_, dict_fittings):
    return reset_fitting_i(dict_fittings, 3)


@app.callback(
    Output('intervals_3-figure', 'children'),
    Input('intervals_3-data', 'data'),
    Input('fittings_3-data', 'data'),
)
def draw_intervals_3(dict_intervals_3, dict_fittings_3):
    return draw_intervals_i(dict_intervals_3, dict_fittings_3, 3)


@app.callback(
    Output('fittings-user', 'data', allow_duplicate=True),
    Input('button-use-factor-user_3', 'n_clicks'),
    State('fittings-user', 'data'),
    State('fittings_3-data', 'data'),
    State('factor-user-temp_3', 'value'),
    prevent_initial_call=True
)
def use_user_defined_correction_factor(
    _, dict_fittings_user, dict_fittings_3, factor_user_temp_3):
    return use_user_defined_correction_factor_i(
        dict_fittings_user, dict_fittings_3, factor_user_temp_3, 3)


#
# Intensity 4
#
@app.callback(
    Output('setting-range-fittings_4', 'children'),
    Input('fittings', 'data')
)
def show_fitting_range_4(dict_fittings):
    return show_fitting_range_for_i(dict_fittings, 4)


@app.callback(
    Output('fittings_4-data', 'data', allow_duplicate=True),
    Output('factor-user-temp_4', 'value', allow_duplicate=True),
    Input('button-interval-fit-range_4', 'n_clicks'),
    State('interval-fit-range_4', 'data'),
    State('intervals_4-data', 'data'),
    State('fittings', 'data'),
    prevent_initial_call=True
)
def fit_by_user_4(_, dict_range, dict_intervals, dict_fittings):
    return fit_by_usr_i(dict_range, dict_intervals, dict_fittings, 4)


@app.callback(
    Output('fittings_4-data', 'data', allow_duplicate=True),
    Output('interval-fit-range_4', 'data'),
    Output('factor-user-temp_4', 'value', allow_duplicate=True),
    Input('button-interval-fit-reset_4', 'n_clicks'),
    State('fittings', 'data'),
    prevent_initial_call=True
)
def reset_fitting_4(_, dict_fittings):
    return reset_fitting_i(dict_fittings, 4)


@app.callback(
    Output('intervals_4-figure', 'children'),
    Input('intervals_4-data', 'data'),
    Input('fittings_4-data', 'data'),
)
def draw_intervals_4(dict_intervals_4, dict_fittings_4):
    return draw_intervals_i(dict_intervals_4, dict_fittings_4, 4)


@app.callback(
    Output('fittings-user', 'data', allow_duplicate=True),
    Input('button-use-factor-user_4', 'n_clicks'),
    State('fittings-user', 'data'),
    State('fittings_4-data', 'data'),
    State('factor-user-temp_4', 'value'),
    prevent_initial_call=True
)
def use_user_defined_correction_factor(
    _, dict_fittings_user, dict_fittings_4, factor_user_temp_4):
    return use_user_defined_correction_factor_i(
        dict_fittings_user, dict_fittings_4, factor_user_temp_4, 4)


#
# Intensity 5
#
@app.callback(
    Output('setting-range-fittings_5', 'children'),
    Input('fittings', 'data')
)
def show_fitting_range_5(dict_fittings):
    return show_fitting_range_for_i(dict_fittings, 5)


@app.callback(
    Output('fittings_5-data', 'data', allow_duplicate=True),
    Output('factor-user-temp_5', 'value', allow_duplicate=True),
    Input('button-interval-fit-range_5', 'n_clicks'),
    State('interval-fit-range_5', 'data'),
    State('intervals_5-data', 'data'),
    State('fittings', 'data'),
    prevent_initial_call=True
)
def fit_by_user_5(_, dict_range, dict_intervals, dict_fittings):
    return fit_by_usr_i(dict_range, dict_intervals, dict_fittings, 5)


@app.callback(
    Output('fittings_5-data', 'data', allow_duplicate=True),
    Output('interval-fit-range_5', 'data'),
    Output('factor-user-temp_5', 'value', allow_duplicate=True),
    Input('button-interval-fit-reset_5', 'n_clicks'),
    State('fittings', 'data'),
    prevent_initial_call=True
)
def reset_fitting_5(_, dict_fittings):
    return reset_fitting_i(dict_fittings, 5)


@app.callback(
    Output('intervals_5-figure', 'children'),
    Input('intervals_5-data', 'data'),
    Input('fittings_5-data', 'data'),
)
def draw_intervals_5(dict_intervals_5, dict_fittings_5):
    return draw_intervals_i(dict_intervals_5, dict_fittings_5, 5)


@app.callback(
    Output('fittings-user', 'data', allow_duplicate=True),
    Input('button-use-factor-user_5', 'n_clicks'),
    State('fittings-user', 'data'),
    State('fittings_5-data', 'data'),
    State('factor-user-temp_5', 'value'),
    prevent_initial_call=True
)
def use_user_defined_correction_factor(
    _, dict_fittings_user, dict_fittings_5, factor_user_temp_5):
    return use_user_defined_correction_factor_i(
        dict_fittings_user, dict_fittings_5, factor_user_temp_5, 5)



#
# Intensity 6
#
@app.callback(
    Output('setting-range-fittings_6', 'children'),
    Input('fittings', 'data')
)
def show_fitting_range_6(dict_fittings):
    return show_fitting_range_for_i(dict_fittings, 6)


@app.callback(
    Output('fittings_6-data', 'data', allow_duplicate=True),
    Output('factor-user-temp_6', 'value', allow_duplicate=True),
    Input('button-interval-fit-range_6', 'n_clicks'),
    State('interval-fit-range_6', 'data'),
    State('intervals_6-data', 'data'),
    State('fittings', 'data'),
    prevent_initial_call=True
)
def fit_by_user_6(_, dict_range, dict_intervals, dict_fittings):
    return fit_by_usr_i(dict_range, dict_intervals, dict_fittings, 6)


@app.callback(
    Output('fittings_6-data', 'data', allow_duplicate=True),
    Output('interval-fit-range_6', 'data'),
    Output('factor-user-temp_6', 'value', allow_duplicate=True),
    Input('button-interval-fit-reset_6', 'n_clicks'),
    State('fittings', 'data'),
    prevent_initial_call=True
)
def reset_fitting_6(_, dict_fittings):
    return reset_fitting_i(dict_fittings, 6)


@app.callback(
    Output('intervals_6-figure', 'children'),
    Input('intervals_6-data', 'data'),
    Input('fittings_6-data', 'data'),
)
def draw_intervals_6(dict_intervals_6, dict_fittings_6):
    return draw_intervals_i(dict_intervals_6, dict_fittings_6, 6)


@app.callback(
    Output('fittings-user', 'data', allow_duplicate=True),
    Input('button-use-factor-user_6', 'n_clicks'),
    State('fittings-user', 'data'),
    State('fittings_6-data', 'data'),
    State('factor-user-temp_6', 'value'),
    prevent_initial_call=True
)
def use_user_defined_correction_factor(
    _, dict_fittings_user, dict_fittings_6, factor_user_temp_6):
    return use_user_defined_correction_factor_i(
        dict_fittings_user, dict_fittings_6, factor_user_temp_6, 6)


#
# Intensity 7
#
@app.callback(
    Output('setting-range-fittings_7', 'children'),
    Input('fittings', 'data')
)
def show_fitting_range_7(dict_fittings):
    return show_fitting_range_for_i(dict_fittings, 7)


@app.callback(
    Output('fittings_7-data', 'data', allow_duplicate=True),
    Output('factor-user-temp_7', 'value', allow_duplicate=True),
    Input('button-interval-fit-range_7', 'n_clicks'),
    State('interval-fit-range_7', 'data'),
    State('intervals_7-data', 'data'),
    State('fittings', 'data'),
    prevent_initial_call=True
)
def fit_by_user_7(_, dict_range, dict_intervals, dict_fittings):
    return fit_by_usr_i(dict_range, dict_intervals, dict_fittings, 7)


@app.callback(
    Output('fittings_7-data', 'data', allow_duplicate=True),
    Output('interval-fit-range_7', 'data'),
    Output('factor-user-temp_7', 'value', allow_duplicate=True),
    Input('button-interval-fit-reset_7', 'n_clicks'),
    State('fittings', 'data'),
    prevent_initial_call=True
)
def reset_fitting_7(_, dict_fittings):
    return reset_fitting_i(dict_fittings, 7)


@app.callback(
    Output('intervals_7-figure', 'children'),
    Input('intervals_7-data', 'data'),
    Input('fittings_7-data', 'data'),
)
def draw_intervals_7(dict_intervals_7, dict_fittings_7):
    return draw_intervals_i(dict_intervals_7, dict_fittings_7, 7)


@app.callback(
    Output('fittings-user', 'data', allow_duplicate=True),
    Input('button-use-factor-user_7', 'n_clicks'),
    State('fittings-user', 'data'),
    State('fittings_7-data', 'data'),
    State('factor-user-temp_7', 'value'),
    prevent_initial_call=True
)
def use_user_defined_correction_factor(
    _, dict_fittings_user, dict_fittings_7, factor_user_temp_7):
    return use_user_defined_correction_factor_i(
        dict_fittings_user, dict_fittings_7, factor_user_temp_7, 7)


if __name__ == '__main__':
    app.run_server(debug=True)
