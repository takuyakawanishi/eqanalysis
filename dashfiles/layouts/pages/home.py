import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
import dashfiles.layouts.fig_template as fig_template


################################################################################
#   Preparation and Layout
################################################################################
cff = fig_template.FigSettings()
cfd = fig_template.DashSettings()

dash.register_page(__name__, path='/')
layout = html.Div([
    dbc.Row([
        dbc.Col([
            html.Br(),
            html.H4("Home"),
            html.Div([
                dcc.RadioItems()
            ])
        ], width={'size': 10}, sm=8, md=6, lg=4, xxl=3),
        dbc.Col([
            html.Br(),
            html.H4("Main Contents")
        ], width={'size': 12}, lg=8, xxl=9)
    ]),
])