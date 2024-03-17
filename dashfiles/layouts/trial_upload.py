from dash import Dash, dash_table, dcc, html, Input, Output, State, callback

import base64
import io
import pandas as pd

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = Dash(__name__, external_stylesheets=external_stylesheets)

df = [["From", 1996, 4, 1, 12, 0, 0],
        ["to", 2021, 12, 31, 59, 59]]
df = pd.DataFrame(df, columns=["attrib", "year", "month", "day",
                                "hour", "minute", "second"])

app.layout = html.Div([
        dash_table.DataTable(
            id="datetime-from-to",
            columns=([{"id: "}])

        )

    # dcc.Upload(
    #     id='datatable-upload',
    #     children=html.Div([
    #         'Drag and Drop or ',
    #         html.A('Select Files')
    #     ]),
    #     style={
    #         'width': '100%', 'height': '60px', 'lineHeight': '60px',
    #         'borderWidth': '1px', 'borderStyle': 'dashed',
    #         'borderRadius': '5px', 'textAlign': 'center', 'margin': '10px'
    #     },
    # ),
])


def parse_contents(contents, filename):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    if 'csv' in filename:
        # Assume that the user uploaded a CSV file
        return pd.read_csv(
            io.StringIO(decoded.decode('utf-8')))
    elif 'xls' in filename:
        # Assume that the user uploaded an excel file
        return pd.read_excel(io.BytesIO(decoded))


@callback(Output('datatable-upload-container', 'data'),
          Output('datatable-upload-container', 'columns'),
            #   Input('datatable-upload', 'contents'),
            #   State('datatable-upload', 'filename')
)
def update_output(contents, filename):
    return df.to_dict('records'), [{"name": i, "id": i} for i in df.columns]


# @callback(Output('datatable-upload-graph', 'figure'),
#               Input('datatable-upload-container', 'data'))
# def display_graph(rows):
#     df = pd.DataFrame(rows)

#     if (df.empty or len(df.columns) < 1):
#         return {
#             'data': [{
#                 'x': [],
#                 'y': [],
#                 'type': 'bar'
#             }]
#         }
#     return {
#         'data': [{
#             'x': df[df.columns[0]],
#             'y': df[df.columns[1]],
#             'type': 'bar'
#         }]
#     }


if __name__ == '__main__':
    app.run(debug=True)