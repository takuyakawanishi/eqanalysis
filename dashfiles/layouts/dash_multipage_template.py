import dash
from dash import Dash, dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import dashfiles.layouts.fig_template as fig_template


class MultiPageSettings():

    def __init__(self):
        self.screen_background_color = '#fffeee'


PLOTLY_LOGO = "https://images.plot.ly/logo/new-branding/plotly-logomark.png"

cff = fig_template.FigSettings()
cfd = fig_template.DashSettings()
app = Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.BOOTSTRAP]
)
app.layout = dbc.Container([
    cfd.titlebar("Demo, Multi-page application"),
    dbc.Container([
        dbc.Container([
            dbc.Row([
                dbc.Col([
                ], width={'size': 12}, sm=8, md=6, lg=4, xxl=3),
                dbc.Col([
                    html.Ul([
                        html.Li([
                            dbc.NavItem(dbc.NavLink(
                                "Home", href="/", active=True,
                                style={
                                    'color': '#f8f8f8', "padding-left": 0})),
                        ], style={
                            "display": "inline", "float": "left",
                            "width": "5rem", "padding-left": 0
                        }),
                        html.Li([
                            dbc.NavItem(dbc.NavLink(
                                "Archive", href="/archive",
                                style={
                                    'color': '#f8f8f8', "padding-left": 0})),
                        ], style={
                            "display": "inline", "float": "left",
                            "width": "5rem", "padding-left": 0
                        }),
                        html.Li([
                            dbc.NavItem(dbc.NavLink(
                                "Analytics", href="/analytics",
                                style={
                                    'color': '#f8f8f8', "padding-left": 0})),
                        ], style={
                            "display": "inline", "float": "left",
                            "width": "5rem", "padding-left": 0
                        })
                    ], style={"min-height": "1rem", "padding": 0,
                              "font-family": "Helvetica"}),
                ], width={'size': 12}, lg=8, xl=7, xxl=6),
                dbc.Col([
                ], width={"size": 12}, xl=1, xxl=3)
            ])
        ], fluid=False),
    ], fluid=True, style={
        'min-width': '100vw',
        'background-color': '#192f60',
        'margin-left': '-12px', 'margin-right': '-12px'}
    ),
    dbc.Container([
        dbc.Row([
            dash.page_container
        ])
    ], fluid=False)
], style=cfd.global_style, fluid=True)


if __name__ == '__main__':
    app.run_server(debug=True, port=8040)