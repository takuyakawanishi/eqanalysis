# import datetime
# from dateutil.relativedelta import relativedelta
from dash import Dash, dcc, dash_table, html, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pandas as pd
# import scipy.stats
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
app = Dash(__name__)  # external_stylesheets=[dbc.themes.BOOTSTRAP])
app.layout = dbc.Container([
    cfd.titlebar("Earthquake Intensity-Frequency Analysis"),
    dbc.Container([
        dbc.Row([
            dbc.Col([
                dcc.Store(id='temp'),
                dcc.Store(id='station-meta'),
                dcc.Store(id='available-periods'),
                dcc.Store(id='set-period'),
                dcc.Store(id='set-period_1'),
                dcc.Store(id='set-period_2'),
                dcc.Store(id='summary'),
                #
                html.Br(),
                html.H4("Settings"),
                select_station(5510100),
                html.Div(id="stations-addresses"),
                html.Div(id="stations-periods"),
                html.Br(),
                html.H5("Setting the period"),
                html.H6("Primary plot"),
                cfd.select_date_from(1996, 4, 1, 1919, 2020),
                cfd.select_date_to(2019, 12, 31, 1919, 2020),
                cfd.radioitems_yes_no(
                    "  Show regression line?", 0, initial="Yes"),
                html.Br(),
                html.Table([
                    html.Tr([
                        html.Td([html.Div("Another plot?")]),
                        html.Td([
                            dcc.RadioItems(
                                id="if-second-plot",
                                options=["Yes", "No"],
                                value="No",
                                inputStyle={'margin-right': '8px',
                                            'margin-left': '8px',
                                            'display': 'inline-block'}),
                        ])
                    ])
                ], style={"height": "2.4rem", "align": "center"}),
                cfd.select_date_from(1996, 4, 1, 1919, 2020, id=1),
                cfd.select_date_to(2019, 12, 31, 1919, 2020, id=1),
                cfd.radioitems_yes_no(
                    "  Show regression line?", 1, initial="No"),
                html.Br(),
                html.Table([
                    html.Tr([
                        html.Td([html.Div("Yet another plot?")]),
                        html.Td([
                            dcc.RadioItems(
                                id="if-third-plot",
                                options=["Yes", "No"],
                                value="No",
                                inputStyle={'margin-right': '8px',
                                            'margin-left': '8px',
                                            'display': 'inline-block'}),
                        ])
                    ])
                ], style={"height": "2.4rem", "align": "center"}),
                cfd.select_date_from(1996, 4, 1, 1919, 2020, id=2),
                cfd.select_date_to(2019, 12, 31, 1919, 2020, id=2),
                cfd.radioitems_yes_no(
                    "  Show regression line?", 2, initial="No"),
                html.Br(),
                html.Br(),
            ], width={'size': 10}, sm=8, md=6, lg=4, xxl=3),
            dbc.Col([
                html.Br(),
                html.H4("High Intensity Earthquakes"),
                html.Div(id="high-intensity-quakes"),
                html.Br(),
                html.H4("Intensity-Frequency"),
                html.Div(id="actual-periods-durations-show"),
                html.Div(
                    id='graph-intensity-frequency',
                    style={'display': 'inline-block'}),
                dbc.Container([
                ], style={'display': 'block'}),
                html.Div(id="summary-show")

            ], width={'size': 12}, lg=8, xxl=9)
        ]),
    ], fluid=False)
], style=cfd.global_style, fluid=True)


################################################################################
#  Callbacks
################################################################################


@app.callback(
    Output('station-meta', 'data'),
    Output('station-data-msg', 'children'),
    Output('stations-addresses', 'children'),
    Input('submit-button-state', 'n_clicks'),
    State('station', 'value')
)
def check_station_is_in_the_database(_, str_code):
    code = int(str_code)
    if code in meta["code_prime"].values:
        meta_1 = meta[meta["code_prime"] == code]
        meta_1 = meta_1.reset_index(drop=True)
        msg = html.P([str_code + ' is in the database.', html.Br()])
        address = meta_1.at[0, "address"]
        address_msg = html.Div([
            html.P(address)
        ])
        # address_msg = None
        meta_1_dict = (pd.DataFrame(meta_1)).to_dict('records')

    else:
        msg = str_code + ' is NOT in the database.'
        meta_1_dict = None
        address_msg = None
    return meta_1_dict, msg, address_msg


@app.callback(
    Output('available-periods', 'data'),
    Output('stations-periods', 'children'),
    Input('station-meta', 'data'),
)
def show_available_periods(group_dict):
    meta_1 = pd.DataFrame.from_dict(group_dict)
    meta_1 = meta_1.reset_index(drop=True)
    station = meta_1.at[0, "code_prime"]
    dfsp = eqa.find_available_periods(meta, station)
    stations_periods_dict = (pd.DataFrame(dfsp)).to_dict('records')
    stations_periods_show = html.Div([
        html.H5("Stations, periods"),
        html.P("This group contains the following."),
        dbc.Container([
            dash_table.DataTable(
                data=stations_periods_dict,
                columns=[{'name': i, 'id': i} for i in dfsp.columns]),
        ], style={"font-size": "1rem"})
    ])
    return stations_periods_dict, stations_periods_show


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


@app.callback(
    Output('start-year_1', 'disabled'),
    Output('start-month_1', 'disabled'),
    Output('start-day_1', 'disabled'),
    Output('end-year_1', 'disabled'),
    Output('end-month_1', 'disabled'),
    Output('end-day_1', 'disabled'),
    [Input(component_id='if-second-plot', component_property='value')]
)
def enable_disable_second_period_selection(if_second):
    if if_second == "Yes":
        return False, False, False, False, False, False
    else:
        return True, True, True, True, True, True


@app.callback(
    Output('set-period_1', 'data'),
    Input('start-year_1', 'value'),
    Input('start-month_1', 'value'),
    Input('start-day_1', 'value'),
    Input('end-year_1', 'value'),
    Input('end-month_1', 'value'),
    Input('end-day_1', 'value')
)
def setting_the_analysis_period_for_second_one(sy, sm, sd, ey, em, ed):
    analysis_from = str(sy) + '-' + str(sm).zfill(2) + '-' + str(sd).zfill(2)
    analysis_to = str(ey) + '-' + str(em).zfill(2) + '-' + str(ed).zfill(2)
    period_analyze_dict = {"set_from": analysis_from, "set_to": analysis_to}
    return period_analyze_dict


@app.callback(
    Output('start-year_2', 'disabled'),
    Output('start-month_2', 'disabled'),
    Output('start-day_2', 'disabled'),
    Output('end-year_2', 'disabled'),
    Output('end-month_2', 'disabled'),
    Output('end-day_2', 'disabled'),
    [Input(component_id='if-third-plot', component_property='value')]
)
def enable_disable_third_period_selection(if_second):
    if if_second == "Yes":
        return False, False, False, False, False, False
    else:
        return True, True, True, True, True, True


@app.callback(
    Output('set-period_2', 'data'),
    Input('start-year_2', 'value'),
    Input('start-month_2', 'value'),
    Input('start-day_2', 'value'),
    Input('end-year_2', 'value'),
    Input('end-month_2', 'value'),
    Input('end-day_2', 'value')
)
def setting_the_analysis_period_for_third_one(sy, sm, sd, ey, em, ed):
    analysis_from = str(sy) + '-' + str(sm).zfill(2) + '-' + str(sd).zfill(2)
    analysis_to = str(ey) + '-' + str(em).zfill(2) + '-' + str(ed).zfill(2)
    period_analyze_dict = {"set_from": analysis_from, "set_to": analysis_to}
    return period_analyze_dict


@app.callback(
    Output("high-intensity-quakes", "children"),
    Input('station-meta', 'data'),
)
def display_high_intensity_quakes(station_dict):
    station_meta = pd.DataFrame.from_dict(station_dict)
    station = station_meta.at[0, "code_prime"]
    highest_quakes = eqa.find_highest(meta, station, dir_data=DIR_DATA)
    highest_quakes_dict = highest_quakes.to_dict("records")
    disp_heighest_quakes = html.Div([
        dash_table.DataTable(
            data=highest_quakes_dict,
            columns=[{'name': i, 'id': i} for i in highest_quakes.columns]),
    ])
    print(station_meta.at[0, "code_prime"])
    return disp_heighest_quakes


@app.callback(
    Output('graph-intensity-frequency', 'children'),
    Output('summary', 'data'),
    Input('station-meta', 'data'),
    Input('set-period', 'data'),
    [Input(component_id='if-second-plot', component_property='value')],
    [Input(component_id='if-third-plot', component_property='value')],
    Input('set-period_1', 'data'),
    Input('set-period_2', 'data'),
    Input("radioitems-yesno_0", "value"),
    Input("radioitems-yesno_1", "value"),
    Input("radioitems-yesno_2", "value")
)
def draw_intensity_frequency(
        meta_1_dict, set_dict, if_second, if_third, set_1_dict, set_2_dict,
        show_regression_primary, show_regression_second, show_regression_third
):
    meta_1 = pd.DataFrame.from_dict(meta_1_dict)
    print("draw_intensity_frequency: meta_1")
    print(meta_1)
    station = meta_1.at[0, "code_prime"]
    print(station)
    frequency, fit, sum_0 = eqa.find_intensity_frequency_regression_summarize(
        meta, station, set_dict, dir_data=DIR_DATA)
    summary = sum_0
    freq_values = np.array(frequency.values)
    n = len(freq_values)
    intensities = np.arange(n) + 1
    width = 360
    height = 360
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=intensities, y=freq_values, mode='markers',
        marker=dict(color=px.colors.qualitative.T10[0], size=10),
        name="Observed",
    ))
    if n >= 4 and show_regression_primary == "Yes":
        xs = np.linspace(2, 7)
        ys = 10 ** (fit.intercept + fit.slope * xs)
        fig.add_trace(go.Scatter(
            x=xs, y=ys, mode='lines',
            line=dict(color='black', width=1),
            name="Fitted"
        ))
    if if_second == "Yes":
        frequency_1, fit_1, sum_1 = \
            eqa.find_intensity_frequency_regression_summarize(
                meta, station, set_1_dict, dir_data=DIR_DATA)
        summary = pd.concat([summary, sum_1], axis=1)
        freq_values_1 = np.array(frequency_1.values)
        intensities_1 = np.arange(len(freq_values_1)) + 1
        fig.add_trace(go.Scatter(
            x=intensities_1, y=freq_values_1, mode='markers',
            marker=dict(
                symbol="cross", color=px.colors.qualitative.T10[1], size=10),
            name="Second"
        ))

        xs = np.linspace(2, 7)
        ys = 10 ** (fit_1.intercept + fit_1.slope * xs)
        if show_regression_second == "Yes":
            fig.add_trace(go.Scatter(
                x=xs, y=ys, mode='lines',
                line=dict(color='black', width=1, dash='dash'),
                name="Second"
            ))

    if if_third == "Yes":
        frequency_2, fit_2, sum_2 = \
            eqa.find_intensity_frequency_regression_summarize(
                meta, station, set_2_dict, dir_data=DIR_DATA)
        summary = pd.concat([summary, sum_2], axis=1)
        freq_values_2 = np.array(frequency_2.values)
        intensities_2 = np.arange(len(freq_values_2)) + 1
        fig.add_trace(go.Scatter(
            x=intensities_2, y=freq_values_2, mode='markers',
            marker=dict(
                size=10, symbol="x", color=px.colors.qualitative.T10[2]),
            name="Third"
        ))
        xs = np.linspace(2, 7)
        ys = 10 ** (fit_2.intercept + fit_2.slope * xs)
        if show_regression_third == "Yes":
            fig.add_trace(go.Scatter(
                x=xs, y=ys, mode='lines',
                line=dict(color='black', width=1, dash='dot'),
                name="Third"
            ))
    fig.update_layout(
        paper_bgcolor=cff.screen_background_color,
        xaxis_title="Intensities",
        yaxis_title="Frequencies",
        autosize=False,
        font=dict(family="Helvetica", size=14),
        width=width,
        height=height,
        margin=dict(l=4 / 25 * width, b=4 / 25 * height,
                    r=1 / 25 * width, t=1 / 25 * height),
        legend=dict(x=.02, y=.02, font=dict(size=12)),
    )
    fig.update_yaxes(type='log')
    graph = dcc.Graph(figure=fig, style={'display': 'inline-block'})
    summary = pd.DataFrame(summary)
    summary = summary.transpose()
    print(summary)
    summary_dict = summary.to_dict("records")
    return graph, summary_dict


@app.callback(
    Output('summary-show', 'children'),
    Input('summary', 'data')
)
def show_summary(df_summary_dict):
    df_summary = pd.DataFrame.from_dict(df_summary_dict)
    df_summary_show = html.Div([
        html.H5("Summary"),
        dash_table.DataTable(
            data=df_summary_dict,
            columns=[{'name': i, 'id': i} for i in df_summary.columns]),
    ])
    return df_summary_show


if __name__ == '__main__':
    app.run_server(debug=True)
