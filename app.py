from logging import PlaceHolder
import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Output, Input, State
from dash.exceptions import PreventUpdate

import plotly.graph_objects as go
import plotly.express as px

from datetime import date, datetime, timedelta  
import pandas as pd
import re

"""
Paso 1: Llamado a las funciones que generan los datasets iniciales 
"""

"""
Paso 2: Funciones de Dash
"""
def make_empty_fig():
    fig = go.Figure()
    fig.layout.paper_bgcolor = '#E5ECF6'
    fig.layout.plot_bgcolor = '#E5ECF6'
    return fig

"""
Paso 3: Definicion de la app
"""
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.COSMO])


app.layout = html.Div([
    dbc.Row([ # Main header
        dbc.Col([], lg= 1),
        dbc.Col([
            html.H1("Factores que influye en precio de la energía"),
            html.P("Una programa desarrollado por @joseluisramon"),
            html.Br(),
        ], lg = 10)
    ]),
    dbc.Row([
       dbc.Col([], lg =2),
       dbc.Col([ # Calcula
            dbc.Button(
                "Calcular precio",
                 color="primary",
                 block = True)
       ], lg = 8), 
       html.Br()
    ]),
    # Fila con el gráfico de componentes
    dbc.Row([
        html.Br(),
        dbc.Col([], lg = 2), # Offset de columnas
        dbc.Col([ 
            dbc.Label("Componente del Precio"),
            html.Br(),
            dcc.Graph(  id='price-treemap',
                        figure = make_empty_fig() )
        ], md= 12, lg = 8)  
    ]),
    # Fila con informacion de contrato y precio
    dbc.Row([ # Offset de columnas
        dbc.Col([], lg= 1),
        dbc.Col([ # contract info
            html.H2("Contrato",),
            html.Ul([
                html.Ol("Tarifa 2.0TD"),
                html.Ol("Potencia contratada: P1 = 3.45kW \ P2 = 3.45kW")
            ])
        ], md = 8, lg = 5),
        dbc.Col([ # calculated price
            html.H2("Precio periodo factura"),
            html.H3("120 EUR")
        ], md = 8, lg=  5 )
    ]),
    # Fila para jugar con los componentes del contrato
    dbc.Tabs([
        dbc.Tab([ # Consumo
            html.H4("Curva de Consumo"),
            html.P(" Selecciona el tipo de tarifa y la potencia que contrataría en cada periodo"),
            dcc.Dropdown(
                id = 'tarifa_dropdown',
                placeholder= "Selecciona tu tarifa",
                options = [ # Cambiar dependiendo de los perfiles
                    {'label':'2.0TD', 'value':'2.0TD'},
                    {'label':'3.0TD', 'value':'3.0TD'},
            ]),
            html.P("Potencias"),
            dbc.Row([
                dbc.Col([
                    dbc.Input(
                        placeholder = "P1C",
                        type = "number",
                        min = 0, max = 150000,
                        step = 1000
                    ),
                ], lg = 2),
                dbc.Col([
                    dbc.Input(
                        placeholder = "P2C",
                        type = "number",
                        min = 0, max = 150000,
                        step = 1000
                    ),
                ], lg = 2),
                dbc.Col([
                    dbc.Input(
                        placeholder = "P3C",
                        type = "number",
                        min = 0, max = 150000,
                        step = 1000
                    ),
                ], lg = 2),
                dbc.Col([
                    dbc.Input(
                        placeholder = "P4C",
                        type = "number",
                        min = 0, max = 150000,
                        step = 1000
                    ),
                ], lg = 2),
                dbc.Col([
                    dbc.Input(
                        placeholder = "P5C",
                        type = "number",
                        min = 0, max = 150000,
                        step = 1000
                    ),
                ], lg = 2),
                dbc.Col([
                    dbc.Input(
                        placeholder = "P6C",
                        type = "number",
                        min = 0, max = 150000,
                        step = 1000
                    ) 
                ], lg = 2),
            ]),
            dcc.Graph(  id='consumption-graph',
                        figure=make_empty_fig()),
        ], label = 'Consumo'),
        dbc.Tab([ # Mercado y Generacion
            html.H4("Precio del Mercado y generación"),
            html.P("Selecciona la fecha para la cual quiere ver los datos"),
            # Esta fecha siempre tiene que ser anterior al día actual y los datos se traerán por medio de la API
            # para empezar a probar podemos utilizar datos de 2020 para acá
            dcc.DatePickerRange(
                id = 'datepicker-range',
                min_date_allowed = date(2020,1,1),
                max_date_allowed = date.today(),
                initial_visible_month=date.today(),
                # end_date = date.today()
            ),
            html.Div( id = 'output-container-datepicker-range'), # This is just to show of 
            html.Br(),
            dcc.Graph(  id='generation-graph',
                        figure = make_empty_fig() )
        ], label = 'Generacion'),
        dbc.Tab([
            html.H4("Cargos y Peajes"),
            html.P("Se aplica a los potencia contrata y la energía"),
            dcc.Dropdown(
                id = 'peajes_dropdown',
                options = [],
                value = None
            ),
            html.Button(
                "Agregar peaje",
                id = 'peajes_button',
                n_clicks = 0
            ),
        ], label = 'Cargos y Peajes'),
        dbc.Tab([

        ], label = 'Impuestos')
    ])

])

"""
Callbacks para generación
"""
@app.callback(
    dash.dependencies.Output( 'output-container-datepicker-range', 'children'),
    [dash.dependencies.Input( 'datepicker-range', 'start_date'),
    dash.dependencies.Input( 'datepicker-range', 'end_date'),]
)
def update_output(start_date, end_date):
    string_prefix = 'Saliendo fechas de: '
    if start_date is not None: 
        start_date_object = date.fromisoformat(start_date)
        start_date_string = start_date_object.strftime("%d-%m-%Y")
        string_prefix = string_prefix + 'Start Date: ' + start_date_string + ' | '
    if end_date is not None: 
        end_date_object = date.fromisoformat(end_date)
        end_date_string = end_date_object.strftime("%d-%m-%Y")
        string_prefix = string_prefix + 'End Date: ' + end_date_string
    if len( string_prefix ) == len('You selected: '):
        return 'Select a date '
    else: 
        return string_prefix

"""
Callback de peajes
"""
@app.callback(
    Output('peajes_dropdown', 'options'),
    [Input('peajes_button','n_clicks')],
    [State('peajes_dropdown', 'options')]
)
def update_options( n_click, existing_options):
    option_name =  f"Option {n_click}"
    existing_options.append( {'label': option_name, 'value': option_name })
    return existing_options

if __name__ == '__main__':
    app.run_server(debug = True)