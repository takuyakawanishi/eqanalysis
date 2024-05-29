import datetime
from dateutil.relativedelta import relativedelta
from dash import Dash, dcc, dash_table, html, Input, Output, State
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
#  Global Constants
################################################################################

DATABASE_START_DATE = '19190101'
DATABASE_END_DATE = '20191231'
# DIR_DATA = '../../data/stationwise_fine_old_until_2019/'
# FILE2READ_META = '../../data/code_p_df.csv'
DIR_DATA = 'eqanalysis/data_2024/stationwise_2021/'
FILE2READ_META = 'eqanalysis/data_2024/code_p_20231205_df.csv'


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
        html.H5(['Station Code']),
        dcc.Input(id='station', type='text', value=str_init_station,
                  style={'width': '40%'}),
        # eval(sid),
        html.Button(id='submit-button-state', n_clicks=0,
                    children='Submit'),
        dcc.Store(id='station-data'),
        html.Div(id='station-data-msg'),
    ])
    return output


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
    idstr_0 = 'input-ef-range-low_' + str(idx)
    idstr_1 = 'input-ef-range-upp_' + str(idx)
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
    idstr = 'input-interval-threshold_' + str(idx)
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
                inputStyle={'margin-right': '4px', 'margin-left': '4px',
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
                inputStyle={'margin-right': '4px', 'margin-left': '4px'})
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
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.layout = dbc.Container([
    cfd.navbar,
    dbc.Container([
        dbc.Row([
            dbc.Col([
                html.Br(),
                html.H4("Settings"),

                select_station(3900000),
                cfd.date_from,
                cfd.date_to,
                html.Div([html.Div(id='conditions-period')]),
                dcc.Store(id='station-meta'),
                dcc.Store(id='station-meta-period'),
                dcc.Store(id='data-range-reg-int-occ'),
                dcc.Store(id='intensity-gteq_1'),
                dcc.Store(id='intensity-gteq_2'),
                dcc.Store(id='intensity-gteq_3'),
                dcc.Store(id='intensity-gteq_4'),
                dcc.Store(id='intensity-gteq_5'),
                dcc.Store(id='intensity-gteq_6'),
                dcc.Store(id='intensity-gteq_7'),
                dcc.Store(id='n-raw-counts'),

                html.H5("Regression intensity vs occurrence"),
                set_range_regression_intensity_occurrence(2, 4, 1, 7),
                html.Button(id='submit-button-state-all', n_clicks=0,
                            children='Draw Figures', style={'width': '80%'}),
                html.Br(),
                html.Br(),
                html.Br(),

                html.H5("Adjustment of occurrence"),
                #
                # CONSIDER take the values from eqanalysis.Settings or cfe
                #
                choose_log_or_linear_for_intervals_scale(),
                choose_count_occurrence_for_regression(1, 7),
                choose_count_occurrence_for_regression(2, 10),
                choose_count_occurrence_for_regression(3, 32),  # CHECK this
                choose_count_occurrence_for_regression(4, 46),  # CHECK this
                choose_count_occurrence_for_regression(5, 46),
                choose_count_occurrence_for_regression(6, 46),
                choose_count_occurrence_for_regression(7, 46),

            ], width={'size': 10}, sm=8, md=6, lg=4, xxl=3
            ),
            dbc.Col([
                dcc.Store(id='data-adjust-aftershocks_1'),
                dcc.Store(id='data-adjust-aftershocks_2'),
                dcc.Store(id='data-adjust-aftershocks_3'),
                dcc.Store(id='data-adjust-aftershocks_4'),
                dcc.Store(id='data-adjust-aftershocks_5'),
                dcc.Store(id='data-adjust-aftershocks_6'),
                dcc.Store(id='data-adjust-aftershocks_7'),
                dcc.Store(id='data-summary'),
                dcc.Store(id='data-estimation'),

                html.Br(),
                html.H5("Regression"),
                html.Div(id='data-summary-table'),
                html.Div(id='data-estimation-table'),
                html.Div(id='range-regression-intensity-occurrence'),
                html.H3("Occurrence of earthquakes of intensity gteq"),
                html.Div(id='fig-summary'),
                html.Div(
                    id='graph-intensity-occurrence',
                    style={'display': 'inline-block'}),
                html.H3('Intervals'),
                dbc.Container([
                    html.Div(id='conditions'),
                    html.Div([
                        html.Div(id='two-values_' + str(1),
                                 style={'display': 'inline'}),
                        html.Div(),
                        html.Div(id='two-values_' + str(2),
                                 style={'display': 'inline'}),
                        html.Div(id='two-values_' + str(3),
                                 style={'display': 'inline'}),
                        html.Div(id='two-values_' + str(4),
                                 style={'display': 'inline'}),
                        html.Div(id='two-values_' + str(5),
                                 style={'display': 'inline'}),
                    ], style={'display': 'inline'}),
                    html.Br(),
                    html.Div(id='graphs', style={'display': 'inline-block'}),
                ], style={'display': 'block'})
            ], width={'size': 12}, lg=8, xxl=9)
        ]),
    ], fluid=False)
], style=cfd.global_style, fluid=True)


################################################################################
#   Callbacks
################################################################################

@app.callback(
    Output('station-meta', 'data'),
    Output('station-data-msg', 'children'),
    Input('submit-button-state', 'n_clicks'),
    State('station', 'value')
)
def check_station_is_in_the_database_and_get_available_period(_, str_code):
    code = int(str_code)
    meta = pd.read_csv(FILE2READ_META)
    if code in meta['code'].values:
        meta_1 = meta[meta['code'] == code]
        meta_1 = meta_1.reset_index(drop=True)
        meta_1 = eqa.calc_date_b_date_e_duration(
            meta_1, '1919-01-01', '2019-12-31')
        print(meta_1)
        #
        # date_from = str(meta_1.at[0, 'from'])[:8]
        # if int(date_from) < int(DATABASE_START_DATE):
        #     date_from = DATABASE_START_DATE
        # date_from = datetime.datetime.strptime(date_from, "%Y%m%d").date()
        #
        # date_to = str(meta_1.at[0, 'to'])[:8]
        # try:
        #     date_to = datetime.datetime.strptime(date_to, "%Y%m%d").date()
        # except ValueError as ve:
        #     print('No end date.', ve)
        #     date_to = \
        #         datetime.datetime.strptime(DATABASE_END_DATE, "%Y%m%d").date()
        meta_1.at[0, 'date_from'] = meta_1.at[0, 'date_b'].date()
        meta_1.at[0, 'date_to'] = meta_1.at[0, 'date_e'].date()
        msg = html.P([
            str_code + ' is in the database.', html.Br(),
            "Records in the database are ", html.Br(),
            "from {}".format(meta_1.at[0, 'date_from']), html.Br(),
            "to {}".format(meta_1.at[0, 'date_to'])])
        meta_1_dict = (pd.DataFrame(meta_1)).to_dict('records')
        print(meta_1)
    else:
        msg = str_code + ' is NOT in the database.'
        meta_1_dict = None

    return meta_1_dict, msg


@app.callback(
    Output('conditions-period', 'children'),
    Output('station-meta-period', 'data'),
    Input('station-meta', 'data'),
    Input('start-year', 'value'),
    Input('start-month', 'value'),
    Input('start-day', 'value'),
    Input('end-year', 'value'),
    Input('end-month', 'value'),
    Input('end-day', 'value')
)
def set_the_period(meta_1_dict, sy, sm, sd, ey, em, ed):
    meta_1p = pd.DataFrame.from_dict(meta_1_dict)
    date_from = meta_1p.at[0, 'date_from']
    date_to = meta_1p.at[0, 'date_to']
    analysis_from = str(sy) + '-' + str(sm).zfill(2) + '-' + str(sd).zfill(2)
    analysis_to = str(ey) + '-' + str(em).zfill(2) + '-' + str(ed).zfill(2)

    date_from_date = datetime.datetime.strptime(date_from, "%Y-%m-%d")
    date_to_date = datetime.datetime.strptime(date_to, "%Y-%m-%d")
    analysis_from_date = datetime.datetime.strptime(analysis_from, "%Y-%m-%d")
    analysis_to_date = datetime.datetime.strptime(analysis_to, "%Y-%m-%d")

    if analysis_from_date < date_from_date:
        analysis_from_date = date_from_date
    if analysis_to_date > date_to_date:
        analysis_to_date = date_to_date

    analysis_from = datetime.datetime.strftime(analysis_from_date, "%Y-%m-%d")
    analysis_to = datetime.datetime.strftime(analysis_to_date, "%Y-%m-%d")
    meta_1p.at[0, 'analysis_from'] = analysis_from
    meta_1p.at[0, 'analysis_to'] = analysis_to
    meta_1p_dict = (pd.DataFrame(meta_1p)).to_dict('records')
    return html.Div(
        [html.P("Analyse the period from {} to {}.". \
                format(analysis_from, analysis_to))
         ]), meta_1p_dict


@app.callback(
    Output('intensity-gteq_1', 'data'),
    Output('intensity-gteq_2', 'data'),
    Output('intensity-gteq_3', 'data'),
    Output('intensity-gteq_4', 'data'),
    Output('intensity-gteq_5', 'data'),
    Output('intensity-gteq_6', 'data'),
    Output('intensity-gteq_7', 'data'),
    Output('n-raw-counts', 'data'),
    Input('station-meta-period', 'data')
)
def get_intensity_wise_dataframes(station_meta_period):
    meta_1p = pd.DataFrame.from_dict(station_meta_period)
    print("meta_1p", meta_1p)
    code = meta_1p.at[0, 'code']
    analysis_from = meta_1p.at[0, 'analysis_from']
    analysis_to = meta_1p.at[0, 'analysis_to']
    dfis, n_raws = eqa.calc_intervals_n_raw_counts(
        DIR_DATA, code, beginning=analysis_from, end=analysis_to)
    dfi_dicts = []
    for dfi in dfis:
        dfi_dicts.append(dfi.to_dict())
    # print(dfi_dicts)
    df_n_raws = pd.Series(index=['1', '2', '3', '4', '5', '6', '7'])
    for i in range(7):
        df_n_raws.at[str(i+1)] = n_raws[i]
    n_raws_dict = df_n_raws.to_dict()
    return dfi_dicts[0], dfi_dicts[1], dfi_dicts[2], dfi_dicts[3], \
           dfi_dicts[4], dfi_dicts[5], dfi_dicts[6], n_raws_dict

#
#  CONSIDER remove data-range-reg-int-occ
#     these data are in Settings or cfs
#

@app.callback(
    Output('range-regression-intensity-occurrence', 'children'),
    Output('data-range-reg-int-occ', 'data'),
    Input('intensity-from', 'value'),
    Input('intensity-to', 'value')
)
def set_range_intensity_for_regression_vs_occurrence(intensity_0, intensity_1):
    intensity_range_dict = {
        'from': intensity_0, 'to': intensity_1}
    cfs.reg_int_occ_low = intensity_0
    cfs.reg_int_occ_upp = intensity_1
    return html.P([
        "Range of intensity in regression is from {} to {}".format(
            intensity_0, intensity_1)]), intensity_range_dict


def adjust_aftershocks(
        idx, dfi_dict, limit_low, limit_upp, interval_cutoff, select,
        n_raw_counts):
    try:
        dfi = pd.DataFrame.from_dict(dfi_dict)
    except Exception as ex:
        print(ex)
        dfi = None
        pass
    n_raw = n_raw_counts[str(idx)]
    intercept = np.nan
    slope = np.nan
    rvalue = np.nan
    n_by_fit = np.nan
    if n_raw > 2:
        try:
            res = fit_intervals_to_exponential(dfi, limit_low, limit_upp)
            intercept = round_to_k(10 ** res.intercept, 4)
            slope = round_to_k(res.slope, 4)
            rvalue = round_to_k(res.rvalue, 4)
            n_by_fit = np.round(intercept, 1)
        except ValueError as ve:
            print("Regression exp failed, ", ve)
            pass
    else:
        n_by_fit = n_raw

    if n_raw <= 1:
        n_by_cut = n_raw
    else:
        n_by_cut = len(dfi[dfi['interval'] >= interval_cutoff]) + 1
    if select == "Raw n":
        n_to_use = n_raw
    elif select == "n by fit":
        n_to_use = n_by_fit
    elif select == "n by cut":
        n_to_use = n_by_cut
    fit_dict = {
        'intensity': idx, 'efl': limit_low, 'efu': limit_upp,
        'cutoff': interval_cutoff, 'ef_intercept': intercept,
        'ef_slope': slope, 'ef_r': rvalue, 'which': select,
        'n_raw': n_raw, 'n_by_fit': n_by_fit, 'n_by_cut': n_by_cut,
        'n_to_use': n_to_use
    }
    print(fit_dict)
    return n_raw, n_by_fit, n_by_cut, n_to_use, fit_dict


# @app.callback(
#     Output('intervals-linear-or-log-out', 'data'),
#     Input('intervals-linear-or-log', 'value'),
# )


@app.callback(
    Output('count-raw_1', 'children'),
    Output('n-by-fit_1', 'children'),
    Output('n-by-cut_1', 'children'),
    Output('n-to-use_1', 'children'),
    Output('data-adjust-aftershocks_1', 'data'),
    Input('intensity-gteq_1', 'data'),
    Input('input-ef-range-low_1', 'value'),
    Input('input-ef-range-upp_1', 'value'),
    Input('input-interval-threshold_1', 'value'),
    Input('select-one-of-raw-fit-cut_1', 'value'),
    Input('n-raw-counts', 'data'),
)
def set_threshold_regression_1(
        dfi_dict, limit_low, limit_upp, interval_cutoff, select,
        n_raw_counts):
    n_raw, n_by_fit, n_by_cut, n_to_use, fit_dict = adjust_aftershocks(
        1, dfi_dict, limit_low, limit_upp, interval_cutoff, select,
        n_raw_counts)
    return [n_raw], [n_by_fit], [n_by_cut], [n_to_use], fit_dict


@app.callback(
    Output('count-raw_2', 'children'),
    Output('n-by-fit_2', 'children'),
    Output('n-by-cut_2', 'children'),
    Output('n-to-use_2', 'children'),
    Output('data-adjust-aftershocks_2', 'data'),
    Input('intensity-gteq_2', 'data'),
    Input('input-ef-range-low_2', 'value'),
    Input('input-ef-range-upp_2', 'value'),
    Input('input-interval-threshold_2', 'value'),
    Input('select-one-of-raw-fit-cut_2', 'value'),
    Input('n-raw-counts', 'data')
)
def set_threshold_regression_2(
        dfi_dict, limit_low, limit_upp, interval_cutoff, select,
        n_raw_counts):
    n_raw, n_by_fit, n_by_cut, n_to_use, fit_dict = adjust_aftershocks(
        2, dfi_dict, limit_low, limit_upp, interval_cutoff, select,
        n_raw_counts)
    return [n_raw], [n_by_fit], [n_by_cut], [n_to_use], fit_dict


@app.callback(
    Output('count-raw_3', 'children'),
    Output('n-by-fit_3', 'children'),
    Output('n-by-cut_3', 'children'),
    Output('n-to-use_3', 'children'),
    Output('data-adjust-aftershocks_3', 'data'),
    Input('intensity-gteq_3', 'data'),
    Input('input-ef-range-low_3', 'value'),
    Input('input-ef-range-upp_3', 'value'),
    Input('input-interval-threshold_3', 'value'),
    Input('select-one-of-raw-fit-cut_3', 'value'),
    Input('n-raw-counts', 'data')
)
def set_threshold_regression_3(
        dfi_dict, limit_low, limit_upp, interval_cutoff, select,
        n_raw_counts):
    n_raw, n_by_fit, n_by_cut, n_to_use, fit_dict = adjust_aftershocks(
        3, dfi_dict, limit_low, limit_upp, interval_cutoff, select,
        n_raw_counts)
    return [n_raw], [n_by_fit], [n_by_cut], [n_to_use], fit_dict


@app.callback(
    Output('count-raw_4', 'children'),
    Output('n-by-fit_4', 'children'),
    Output('n-by-cut_4', 'children'),
    Output('n-to-use_4', 'children'),
    Output('data-adjust-aftershocks_4', 'data'),
    Input('intensity-gteq_4', 'data'),
    Input('input-ef-range-low_4', 'value'),
    Input('input-ef-range-upp_4', 'value'),
    Input('input-interval-threshold_4', 'value'),
    Input('select-one-of-raw-fit-cut_4', 'value'),
    Input('n-raw-counts', 'data')
)
def set_threshold_regression_4(
        dfi_dict, limit_low, limit_upp, interval_cutoff, select,
        n_raw_counts):
    n_raw, n_by_fit, n_by_cut, n_to_use, fit_dict = adjust_aftershocks(
        4, dfi_dict, limit_low, limit_upp, interval_cutoff, select,
        n_raw_counts)
    return [n_raw], [n_by_fit], [n_by_cut], [n_to_use], fit_dict


@app.callback(
    Output('count-raw_5', 'children'),
    Output('n-by-fit_5', 'children'),
    Output('n-by-cut_5', 'children'),
    Output('n-to-use_5', 'children'),
    Output('data-adjust-aftershocks_5', 'data'),
    Input('intensity-gteq_5', 'data'),
    Input('input-ef-range-low_5', 'value'),
    Input('input-ef-range-upp_5', 'value'),
    Input('input-interval-threshold_5', 'value'),
    Input('select-one-of-raw-fit-cut_5', 'value'),
    Input('n-raw-counts', 'data')
)
def set_threshold_regression_5(
        dfi_dict, limit_low, limit_upp, interval_cutoff, select,
        n_raw_counts):
    n_raw, n_by_fit, n_by_cut, n_to_use, fit_dict = adjust_aftershocks(
        5, dfi_dict, limit_low, limit_upp, interval_cutoff, select,
        n_raw_counts)
    return [n_raw], [n_by_fit], [n_by_cut], [n_to_use], fit_dict


@app.callback(
    Output('count-raw_6', 'children'),
    Output('n-by-fit_6', 'children'),
    Output('n-by-cut_6', 'children'),
    Output('n-to-use_6', 'children'),
    Output('data-adjust-aftershocks_6', 'data'),
    Input('intensity-gteq_6', 'data'),
    Input('input-ef-range-low_6', 'value'),
    Input('input-ef-range-upp_6', 'value'),
    Input('input-interval-threshold_6', 'value'),
    Input('select-one-of-raw-fit-cut_6', 'value'),
    Input('n-raw-counts', 'data')
)
def set_threshold_regression_6(
        dfi_dict, limit_low, limit_upp, interval_cutoff, select,
        n_raw_counts):
    n_raw, n_by_fit, n_by_cut, n_to_use, fit_dict = adjust_aftershocks(
        6, dfi_dict, limit_low, limit_upp, interval_cutoff, select,
        n_raw_counts)
    return [n_raw], [n_by_fit], [n_by_cut], [n_to_use], fit_dict


@app.callback(
    Output('count-raw_7', 'children'),
    Output('n-by-fit_7', 'children'),
    Output('n-by-cut_7', 'children'),
    Output('n-to-use_7', 'children'),
    Output('data-adjust-aftershocks_7', 'data'),
    Input('intensity-gteq_7', 'data'),
    Input('input-ef-range-low_7', 'value'),
    Input('input-ef-range-upp_7', 'value'),
    Input('input-interval-threshold_7', 'value'),
    Input('select-one-of-raw-fit-cut_7', 'value'),
    Input('n-raw-counts', 'data'),
)
def set_threshold_regression_7(
        dfi_dict, limit_low, limit_upp, interval_cutoff, select,
        n_raw_counts):
    n_raw, n_by_fit, n_by_cut, n_to_use, fit_dict = adjust_aftershocks(
        7, dfi_dict, limit_low, limit_upp, interval_cutoff, select,
        n_raw_counts)
    return [n_raw], [n_by_fit], [n_by_cut], [n_to_use], fit_dict


@app.callback(
    Output('conditions', 'children'),
    Output('graphs', 'children'),
    Output('graph-intensity-occurrence', 'children'),
    Output('data-summary', 'data'),
    Output('data-summary-table', 'children'),
    Output('data-estimation', 'data'),
    Output('data-estimation-table', 'children'),
    Input('submit-button-state-all', 'n_clicks'),
    Input('intensity-gteq_1', 'data'),
    Input('intensity-gteq_2', 'data'),
    Input('intensity-gteq_3', 'data'),
    Input('intensity-gteq_4', 'data'),
    Input('intensity-gteq_5', 'data'),
    Input('intensity-gteq_6', 'data'),
    Input('intensity-gteq_7', 'data'),
    Input('data-adjust-aftershocks_1', 'data'),
    Input('data-adjust-aftershocks_2', 'data'),
    Input('data-adjust-aftershocks_3', 'data'),
    Input('data-adjust-aftershocks_4', 'data'),
    Input('data-adjust-aftershocks_5', 'data'),
    Input('data-adjust-aftershocks_6', 'data'),
    Input('data-adjust-aftershocks_7', 'data'),
    Input('data-range-reg-int-occ', 'data'),
    Input('station-meta-period', 'data'),
    Input('intervals-linear-or-log', 'value')
)
def set_conditions(_, dfi_dict_1, dfi_dict_2, dfi_dict_3, dfi_dict_4,
                   dfi_dict_5, dfi_dict_6, dfi_dict_7,
                   df_aas_dict_1, df_aas_dict_2, df_aas_dict_3, df_aas_dict_4,
                   df_aas_dict_5, df_aas_dict_6, df_aas_dict_7,
                   range_reg_int_occ, station_meta_period_dict,
                   interval_scale):
    df_summary = pd.DataFrame()
    for i in range(7):
        df_ass_dict = eval('df_aas_dict_' + str(i + 1))
        ser_to_add = pd.DataFrame.from_dict(df_ass_dict, orient='index')
        df_to_add = pd.DataFrame(ser_to_add).transpose()
        df_summary = pd.concat([df_summary, df_to_add])
    df_summary = df_summary.reset_index(drop=True)
    df_summary_dict = df_summary.to_dict()
    summary_table = [html.Div([
        dash_table.DataTable(
            data=df_summary.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in df_summary.columns]
        )
    ])]
    dfis = []
    for i in range(7):
        idx = i + 1
        dfis.append(pd.DataFrame.from_dict(eval('dfi_dict_' + str(idx))))
    msg = []
    figs = []
    fig1s = []
    for i_int, intensity in enumerate([1, 2, 3, 4, 5, 6, 7]):
        dfi = dfis[i_int]
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dfi['interval'], y=dfi['suvf'], mode='markers',
            marker=dict(color=px.colors.qualitative.T10[0]),
            name="I >= " + str(intensity)
        ))
        slope = df_summary.at[i_int, 'ef_slope']
        if slope is not None:
            intercept_suvf = df_summary.at[i_int, 'ef_intercept'] / \
                df_summary.at[i_int, 'n_raw']
            log10_intercept_suvf = np.log10(intercept_suvf)
            xls = np.linspace(0, dfi['interval'].max())
            yls = 10 ** (log10_intercept_suvf + slope * xls)
            fig.add_trace(go.Scatter(
                x=xls, y=yls, mode='lines',
                line=dict(color=px.colors.qualitative.T10[1]),
                name="Fitted"
            ))
        fig.update_layout(
            paper_bgcolor=cff.screen_background_color,
            xaxis_title="Intervals [days]",
            yaxis_title="1 - F",
            autosize=False,
            width=cff.fig_width,
            height=240,
            margin=dict(l=4/25 * cff.fig_width, b=4 / 25 * 240,
                        r=1/25 * cff.fig_width, t=1 / 25 * 240),
            legend=dict(x=.66, y=.98, font=dict(size=12)),
        )
        fig.update_yaxes(type='log')
        if interval_scale == 'log':
            fig.update_xaxes(type='log')
        figs.append(dcc.Graph(figure=fig, style={'display': 'inline-block'}))

    print(range_reg_int_occ)

    df_to_use = df_summary.loc[:, ['intensity', 'n_to_use']]
    df_to_use = df_to_use[df_to_use['intensity'] >= range_reg_int_occ['from']]
    df_to_use = df_to_use[df_to_use['intensity'] <= range_reg_int_occ['to']]
    y = np.array(df_to_use['n_to_use']).astype(np.float64)
    log10y = np.log10(y)
    x = np.array(df_to_use['intensity']).astype(np.float64)
    res = scipy.stats.linregress((x, log10y))
    xls = np.linspace(1, 7)
    yls = 10 ** (res.intercept + res.slope * xls)
    print(station_meta_period_dict[0])
    analysis_from = datetime.datetime.strptime(
        station_meta_period_dict[0]['analysis_from'], "%Y-%m-%d")
    analysis_to = datetime.datetime.strptime(
        station_meta_period_dict[0]['analysis_to'], "%Y-%m-%d")
    duration = relativedelta(analysis_to, analysis_from).years
    # duration = 1
    print(duration)
    est_5 = 10 ** (res.intercept + res.slope * 5) / duration
    est_6 = 10 ** (res.intercept + res.slope * 6) / duration
    est_7 = 10 ** (res.intercept + res.slope * 7) / duration
    df_est = pd.DataFrame()
    int_s = list(df_to_use['intensity'])
    for i, intensity in enumerate(int_s):
        idx_efl = 'efl_' + str(intensity)
        idx_efu = 'efu_' + str(intensity)
        idx_cut = 'cutoff_' + str(intensity)
        idx_which = 'which' + str(intensity)
        df_summary_sel = df_summary[df_summary['intensity'] == intensity]
        df_summary_sel = df_summary_sel.reset_index(drop=True)
        df_est.at[0, idx_efl] = df_summary.at[0, 'efl']
        df_est.at[0, idx_efu] = df_summary.at[0, 'efu']
        df_est.at[0, idx_cut] = df_summary.at[0, 'cutoff']
        df_est.at[0, idx_cut] = df_summary.at[0, 'which']
    df_est.at[0, 'intercept'] = round_to_k(res.intercept, 4)
    df_est.at[0, 'slope'] = round_to_k(res.slope, 4)
    df_est.at[0, 'rvalue'] = round_to_k(res.rvalue, 4)
    df_est.at[0, 'est_5'] = round_to_k(est_5, 3)
    df_est.at[0, 'est_6'] = round_to_k(est_6, 3)
    df_est.at[0, 'est_7'] = round_to_k(est_7, 3)
    df_est_dict = df_est.to_dict()
    est_table = [html.Div([
        dash_table.DataTable(
            data=df_est.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in df_est.columns])
    ])]
    print(df_est)
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(
        x=df_summary['intensity'], y=df_summary['n_raw'], mode='markers',
        marker=dict(
            symbol='square',
            color=px.colors.qualitative.T10[0], size=10)
    ))
    fig1.add_trace(go.Scatter(
        x=df_summary['intensity'], y=df_summary['n_by_cut'], mode='markers',
        marker=dict(
            symbol='cross', color=px.colors.qualitative.T10[3], size=10)
    ))
    fig1.add_trace(go.Scatter(
        x=df_summary['intensity'], y=df_summary['n_by_fit'], mode='markers',
        marker=dict(
            symbol='circle', color=px.colors.qualitative.T10[2], size=10)
    ))
    fig1.add_trace(go.Scatter(
        x=df_summary['intensity'], y=df_summary['n_to_use'], mode='markers',
        marker=dict(
            symbol='cross-thin', size=10, line=dict(width=2))
    ))

    fig1.add_trace(go.Scatter(
        x=xls, y=yls, mode='lines',
        line=dict(color=px.colors.qualitative.T10[1])
    ))
    fig1.update_layout(
        paper_bgcolor=cff.screen_background_color,
        xaxis_title="Intensity",
        yaxis_title="Occurrence",
        autosize=False,
        width=cff.fig_width,
        height=cff.fig_height,
        margin=dict(l=4 / 25 * cff.fig_width, b=4 / 25 * 240,
                    r=1 / 25 * cff.fig_width, t=1 / 25 * 240),
        legend=dict(x=.66, y=.98, font=dict(size=12)),
    )
    fig1.update_yaxes(type='log')
    fig1s.append(dcc.Graph(figure=fig1, style={'display': 'inline-block'}))

    return msg, figs, fig1s, df_summary_dict, summary_table, df_est_dict, \
           est_table
# 
# 


if __name__ == '__main__':
    app.run_server(debug=True)
