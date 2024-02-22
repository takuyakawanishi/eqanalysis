from dash import Dash, dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go


class ColorUniversalDesign(object):
    def __init__(self):
        self.name = "Color Universal Design Color Palette"
        # Color Universal Design, Color Palette
        #
        # accent color
        #
        self.red = 'rgba(255, 40, 0, 1)'
        self.yellow = 'rgba(250, 245, 0, 1)'
        self.green = 'rgba(53, 161, 107, 1)'
        self.blue = 'rgba(0, 65, 255, 1)'
        self.skyblue = 'rgba(102, 204, 255, 1)'
        self.pink = 'rgba(255, 153, 160, 1)'
        self.orange = 'rgba(255, 153, 0, 1)'
        self.purple = 'rgba(154, 0, 121, 1)'
        self.brown = 'rgba(102, 51, 0, 1)'
        self.bright_gray = 'rgba(200, 200, 203, 1)'
        self.gray = 'rgba(127, 135, 143, 1)'
        #
        # base color
        #
        self.pale_pink = 'rgba(255, 209, 209, 1)'
        self.cream = 'rgba(255, 255, 153, 1)'
        self.bright_yellow_green = 'rgba(203, 242, 102, 1)'
        self.pale_skyblue = 'rgba(180, 235, 250, 1)'
        self.beige = 'rgba(237, 197, 143, 1)'
        self.pale_green = 'rgba(135, 231, 176, 1)'
        self.pale_purple = 'rgba(199, 178, 222, 1)'


class FigSettings(object):

    def __init__(self):
        # self.screen_background_color = '#feeeed'  # 桜色
        # self.screen_background_color = '#fffaf9'  #
        # self.screen_background_color = '#ffedb3'  # クリーム
        self.screen_background_color = '#fffeee'
        #
        self.fig_width = 360
        self.fig_height = 360
        ll = int(self.fig_width * 5 / 24)
        rr = int(self.fig_width * 1 / 24)
        bb = int(self.fig_height * 5 / 24)
        tt = int(self.fig_height * 1 / 24)
        self.legend = dict(x=0.05, y=0.95, font=dict(size=14))
        self.margin = dict(l=ll, r=rr, t=tt, b=bb)
        self.marker_symbols = [
            'circle', 'square', 'diamond', 'triangle-up', 'triangle-down',
            'cross', 'x']
        self.marker_line = {'width': 0}
        self.marker_size = 12
        # self.marker_colors = [
        #     '#000000', '#252525', '#404040', '#808080', '#E3E3E3']
        self.colors_qualitative = px.colors.qualitative.Safe
        self.colors_qualitative = px.colors.qualitative.Vivid


class DashSettings(FigSettings):
    def __init__(self):
        FigSettings.__init__(self)
        self.global_style = {
            'background-color': self.screen_background_color,
            'min-width': '100vw',
            'min-height': '100vh',
            # 'margin-left': '-12px',
            # 'margin-right': '-12px'
        }
        self.navbar = dbc.Container([
            dbc.Container([
                dbc.Row([
                    dbc.Col([
                        html.Div(["EQAnalysis"],
                        style={'color': '#eee', 'font-family': 'Georgia',
                               'font-size': '24px', 'padding': 0,
                               'padding-top': '4px',
                               'margin': 0}),
                    ], width={'size': 10}, sm=8, md=6, lg=4, xxl=3),
                    dbc.Col([
                    ], width={'size': 12}, lg=8, xxl=9)
                ])
            ], fluid=False)  #, style={'max-width': '1440px'})
        ], fluid=True, style={
            'min-width': '100vw', 'height': '48px',
            'background-color': '#192f60',
            'margin-left': '-12px', 'margin-right': '-12px'}
        )

        self.date_from = html.Div([
            html.P(['From'], style={'display': 'inline-block', 'width': '15%'}),
            html.Div([
                dcc.Dropdown(
                    id='start-year',
                    options=[{'label': x, 'value': x} for x in
                             range(1919, 2100)],
                    value=1919)
            ], style={'display': 'inline-block', 'width': '35%'}),
            html.Div([
                dcc.Dropdown(
                    id='start-month',
                    options=[{'label': x, 'value': x} for x in range(1, 13)],
                    value=1)
            ], style={'display': 'inline-block', 'width': '25%'}),
            html.Div([
                dcc.Dropdown(
                    id='start-day',
                    options=[{'label': x, 'value': x} for x in range(1, 32)],
                    value=1)
            ], style={'display': 'inline-block', 'min-width': '25%'}),
        ])

        self.date_to = html.Div([
            html.P(['to'], style={'display': 'inline-block', 'width': '15%',
                                  'vertical-align': 'middle'}),
            html.Div([
                dcc.Dropdown(
                    id='end-year',
                    options=[
                        {'label': x, 'value': x} for x in range(1919, 2051)],
                    value=2021)
            ], style={'display': 'inline-block', 'min-width': '35%'}),
            html.Div([
                dcc.Dropdown(
                    id='end-month',
                    options=[{'label': x, 'value': x} for x in range(1, 13)],
                    value=12)
            ], style={'display': 'inline-block', 'min-width': '25%'}),
            html.Div([
                dcc.Dropdown(
                    id='end-day',
                    options=[{'label': x, 'value': x} for x in range(1, 32)],
                    value=31)
            ], style={'display': 'inline-block', 'min-width': '25%'}),
        ])

    def titlebar(self, title):
        output = dbc.Container([
            dbc.Container([
                dbc.Row([
                    dbc.Col([
                        html.Div(["EQAnalysis"],  # cc144f
                        style={'color': '#cc8b00', 'font-family': 'Georgia',
                               'font-size': '24px',
                               'padding-top': '8px', 'padding-bottom': '4px',
                               'margin': 0}),
                    ], width={'size': 12}, sm=8, md=6, lg=4, xxl=3),
                    dbc.Col([
                        html.Div([title], style={
                            "color": "#eee", "font-family": "Georgia",
                            "font-size": "24px",
                            "padding-top": "8px", "padding-bottom": "4px",
                            "margin": 0})
                    ], width={'size': 12}, lg=8, xxl=9)
                ])
            ], fluid=False)  #, style={'max-width': '1440px'})
        ], fluid=True, style={
            'min-width': '100vw', 'min-height': '60px',
            'background-color': '#192f60',
            'margin-left': '-12px', 'margin-right': '-12px'}
        )
        return output

    def select_date_from(
            self, init_year, init_month, init_day, year_b, year_e,
            id=0):
        st_y = "start-year_" + str(id)
        st_m = "start-month_" + str(id)
        st_d = "start-day_" + str(id)
        output = html.Div([
            html.Table([
               html.Tr([
                   html.Td(["From"], style={
                       'display': 'inline-block', 'width': '17%',
                       'padding-bottom': "0px"}),
                   html.Td([
                       dcc.Dropdown(
                           id=st_y,
                           options=[{'label': x, 'value': x} for x in
                                    range(year_b, year_e)],
                           value=init_year)
                   ], style={'display': 'inline-block', 'width': '33%',
                             "height": "1.8rem"}),
                   html.Td([
                       dcc.Dropdown(
                           id=st_m,
                           options=[{'label': x, 'value': x} for x in
                                    range(1, 13)],
                           value=init_month)
                   ], style={'display': 'inline-block', 'width': '25%',
                             "height": "1.8rem"}),
                   html.Td([
                       dcc.Dropdown(
                           id=st_d,
                           options=[{'label': x, 'value': x} for x in
                                    range(1, 32)],
                           value=init_day)
                   ], style={
                       'display': 'inline-block', 'width': '25%',
                       "height": "1.8rem"
                   }),
               ])
            ], style={"width": "100%", "align": "center"}),
        ], style={"display": "block", "height": "2.4rem", "align": "center"})
        return output

    def select_date_to(
            self, init_year, init_month, init_day, year_b, year_e,
            id=0):
        en_y = "end-year_" + str(id)
        en_m = "end-month_" + str(id)
        en_d = "end-day_" + str(id)
        output = html.Div([
            html.Table([
                html.Tr([
                    html.Td(['to'],
                           style={'display': 'inline-block', 'width': '17%',
                                  'vertical-align': 'middle'}),
                    html.Td([
                        dcc.Dropdown(
                            id=en_y,
                            options=[
                                {'label': x, 'value': x}
                                for x in range(year_b, year_e)],
                            value=init_year)
                    ], style={'display': 'inline-block', 'min-width': '33%',
                              "height": "1.8rem"}
                    ),
                    html.Td([
                        dcc.Dropdown(
                            id=en_m,
                            options=[{'label': x, 'value': x} for x in
                                     range(1, 13)],
                            value=init_month)
                    ], style={'display': 'inline-block', 'min-width': '25%',
                              "height": "1.8rem"}),
                    html.Td([
                        dcc.Dropdown(
                            id=en_d,
                            options=[{'label': x, 'value': x} for x in
                                     range(1, 32)],
                            value=init_day)
                    ], style={'display': 'inline-block', 'min-width': '25%',
                              "height": "1.8rem"}),
                ])
            ], style={"width": "100%"}),
        ], style={"display": "block", "height": "2.4rem"})
        return output

    def radioitems_yes_no(self, question, idx, initial="No"):
        idstr = "radioitems-yesno_" + str(idx)
        output = html.Div([
            html.Table([
                html.Tr([
                    html.Td([html.Div(question)]),
                    html.Td([
                        dcc.RadioItems(
                            id=idstr,
                            options=["Yes", "No"],
                            value=initial,
                            inputStyle={
                                'margin-right': '8px', 'margin-left': '8px',
                                'display': 'inline-block',
                                "align": "center"
                            }),
                    ])
                ])
            ], style={"height": "2.4rem", "align": "center"}),
        ])
        return output

    def dropdown(self, title, int_value, options, idx):
        idstr = 'dropdown_' + str(idx)
        output = html.Div([
            html.Div(
                [html.P(title)],
                style={'width': '50%', 'display': 'inline-block',
                       'margin': 'auto'}),
            html.Div(
                dcc.Dropdown(options, int_value, id=idstr),
                style={'width': '50%', 'display': 'inline-block',
                       'margin': 'auto'}),
        ], style={'display': 'block'})
        return output

    def input_one_value(self, idx, title, int_value):
        idstr = 'input-one-value_' + str(idx)
        idbtn = 'submit-button-state-one-value_' + str(idx)
        output = html.Div([
            html.Div(
                [html.P(title)],
                style={'width': '40%', 'display': 'inline-block'}),
            dcc.Input(
                id=idstr, type='text', value=int_value,
                style={'width': '30%', 'display': 'inline-block'}),
            html.Button(
                id=idbtn, n_clicks=0, children='Submit',
                style={'width': '30%', 'display': 'inline-block',
                       'margin': 'auto'})
        ], style={'display': 'block'})
        return output

    def input_two_values(self, idx, title, int_value_0, int_value_1):
        idstr_0 = 'input-two-values_0_' + str(idx)
        idstr_1 = 'input-two-values_1_' + str(idx)
        idbtn = 'submit-button-state-two-values_' + str(idx)
        output = html.Div([
            html.Div(
                [html.P(title)],
                style={'width': '35%', 'display': 'inline-block'}),
            dcc.Input(
                id=idstr_0, type='text', value=int_value_0,
                style={'width': '20%', 'display': 'inline-block'}),
            dcc.Input(
                id=idstr_1, type='text', value=int_value_1,
                style={'width': '20%', 'display': 'inline-block'}),
            html.Button(
                id=idbtn, n_clicks=0, children='Submit',
                style={'width': '25%', 'display': 'inline-block'}
            )
        ], style={'display': 'block'})
        return output

    def input_two_values_vo(self, idx, title, int_value_0, int_value_1):
        idstr_0 = 'input-two-values-vo_0_' + str(idx)
        idstr_1 = 'input-two-values-vo_1_' + str(idx)
        output = html.Div([
            html.Div(
                [html.P(title)],
                style={'width': '40%', 'display': 'inline-block'}),
            dcc.Input(
                id=idstr_0, type='text', value=int_value_0,
                style={'width': '30%', 'display': 'inline-block'}),
            dcc.Input(
                id=idstr_1, type='text', value=int_value_1,
                style={'width': '30%', 'display': 'inline-block'}),
        ], style={'display': 'block'})
        return output

    def radio_button_selection(self):
        output = html.Div([
            html.Table([
                html.Tr([
                    html.Td(["Title"]),
                    html.Td([dcc.RadioItems(["yes", "no"], inline=True)])
                ])
            ])
        ], style={"height": "1.75rem"})
        return output



class FigSettingsNpabg(FigSettings):
    def __init__(self):
        FigSettings.__init__(self)
        self.plot_area_background_color = self.screen_background_color


cff = FigSettings()
cfd = DashSettings()
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.layout = dbc.Container([
    cfd.navbar,
    dbc.Container([
        dbc.Row([
            dbc.Col([
                html.Br(),
                html.H5("Settings"),
                html.Div([
                    dcc.RadioItems()
                ])
            ], width={'size': 10}, sm=8, md=6, lg=4, xxl=3),
            dbc.Col([
                html.Br(),
                html.H5("Main Contents")
            ], width={'size': 12}, lg=8, xxl=9)
        ]),
    ], fluid=False, style={'max-width': '1440px'})
], style=cfd.global_style, fluid=True)


if __name__ == '__main__':
    app.run_server(debug=True, port=8070)