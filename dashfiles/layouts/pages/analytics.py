import dash
from dash import Dash, html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
import dashfiles.layouts.fig_template as fig_template


cff = fig_template.FigSettings()
cfd = fig_template.DashSettings()

dash.register_page(__name__)
layout = html.Div(children=[
    dbc.Container([
    ], fluid=False)
])
layout = html.Div([
    dbc.Row([
        dbc.Col([
            html.Br(),
            html.H5("Analytics"),
        ], width={'size': 10}, sm=8, md=6, lg=4, xxl=3),
        dbc.Col([
            html.Br(),
            html.H5(children='This is our Analytics page'),
            html.Div([
                "Select a city: ",
                dcc.RadioItems(
                    ['New York City', 'Montreal', 'San Francisco'],
                    'Montreal',
                    id='analytics-input')
            ]),
            html.Br(),
            html.Div(id='analytics-output'),
        ], width={'size': 12}, lg=8, xxl=9)
    ])
])


@callback(
    Output(component_id='analytics-output', component_property='children'),
    Input(component_id='analytics-input', component_property='value')
)
def update_city_selected(input_value):
    return f'You selected: {input_value}'
