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
            html.H1("Main Contents"),
            html.P(["Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."]),
            html.H2("Sub-Headings"),
            html.H3("H3 headings"),
            html.H4("H4 headings"),
            html.P(["The line spacing here is a bit larger than"
                    " usual English sites. This is a compromise for"
                    " using both Japanese and English in this site."
                    " Japanese sentences require more spacings than"
                    " English ones, and for this reason, the line-height"
                    " in this page is set to 1.75."])
        ], width={'size': 12}, lg=8, xl=7, xxl=7),
        dbc.Col([
        ], width={"size": 0}, xl=1, xxl=2)
    ]),
])

