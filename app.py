from logging import PlaceHolder
import dash
from dash_bootstrap_components._components.CardBody import CardBody
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Output, Input, State
from dash.exceptions import PreventUpdate

import plotly.graph_objects as go
import plotly.express as px
import pprint

from datetime import date, datetime, timedelta
import pandas as pd
import json
import re

# Components
from components import *
from backend import *

"""
Paso 1: Traerse o crear los datos
"""

"""
Paso 3: Definicion de la app
"""
app = dash.Dash(
    __name__, external_stylesheets=[dbc.themes.COSMO],
    prevent_initial_callbacks= True, # Lo cargas inicalmente cuando ejecutas el programa
)  # https://dash-bootstrap-components.opensource.faculty.ai/docs/themes/explorer/


body = html.Div(
    [   
        dbc.Row( # Title and presentation. (It takes all the screen)
        [
            dbc.Col(
                [
                    html.Div(
                        children=[mainHeader]
                    )
                ], xs=10, sm=10, md=10, lg=10, xl=10
            ),
        ], justify="center"),
        dbc.Row( # Selector and outputs. Horizontal Layout
        [
            dbc.Col( # Left-layout
                [
                html.Div(#Inputs
                    children=[
                        selectores1,
                        selectores2, 
                        selectores3,
                        selectores4,
                        selectores5,
                        selectores6,
                        botonCalcular,
                    ]
                )
                ], md=6, lg=6, xl=6
            ),
            dbc.Col( # Right-layout
                [
                    html.Div (#Auxiliary Output
                        children=[aux_output]
                    ),# xs=10, sm=10, md=10, lg=9, xl=9
                    html.Div( # Output
                        children=[
                            desglose,
                            graph_tabs,
                        ]  
                    )
                ], md=4, lg=4, xl=4
            )
        ], justify="center"),
    ]
)
        
   
############################# CALL THE APP ####################################

# Main Call for
app.layout = html.Div(children=[body])


######################## CALLBACKS DE ENTRADA #################################
# Este callback nos va a asegurar que estemos tomando los datos desde el frontend
# y me los va a presentar en un diccionario
@app.callback(
    Output("output-selectores", "data"),[
    Input("selector1-tarifa-state","value"),
    Input("selector2-P1C", "value"),
    Input("selector2-P2C", "value"),
    Input("selector2-P3C", "value"),
    Input("selector2-P4C", "value"),
    Input("selector2-P5C", "value"),
    Input("selector2-P6C", "value"),
    Input("selector3-table-potencia", 'data'),
    Input("selector3-table-energia", "data"),
    Input("selector4-margen-potencia", "value"),
    Input("selector4-contador", "value"),
    Input("selector5-imp-elect", "value"),
    Input("selector5-imp-iva", "value"),
    Input("selector6-datepicker","start_date"),
    Input("selector6-datepicker","end_date"),
    ]
)
def build_input_dict( 
    tarifa, p1c, p2c, p3c, p4c, p5c, p6c, 
    rows_potencia, rows_energia, 
    margen_pot, alquiler_cont,
    imp_elect, iva,
    start_date, end_date
    ):

    # Limpiamos los valores del datatable
    for row in rows_potencia: 
        del row['Concepto']
    for row in rows_energia: 
        del row['Concepto']

    # Procesamos la salida del datepicker
    if start_date is not None:
        start_datetime = datetime.fromisoformat(start_date)
        start_date_string = start_datetime.strftime('%Y-%m-%d')
    if end_date is not None:
        end_datetime = datetime.fromisoformat(end_date)
        end_date_string = end_datetime.strftime('%Y-%m-%d')
    else: 
        start_date_string, end_date_string = '2021-06-01', '2021-08-31'

    # Construimos el diccionario de salida
    input_dict ={
        'tarifa': tarifa,
        'potencias': {
            'P1': p1c,
            'P2': p2c,
            'P3': p3c,
            'P4': p4c,
            'P5': p5c,
            'P6': p6c,
        },
        'peajes_potencia': rows_potencia[0],
        'cargos_potencia': rows_potencia[1],
        'peajes_energia': rows_energia[0],
        'cargos_energia': rows_energia[1],
        'margen_potencia': margen_pot,
        'alquiler_contador': alquiler_cont,
        'imp_electrico': imp_elect,
        'iva':iva,
        'start_date': start_date_string,
        'end_date': end_date_string
    }

    # return html.Div([
    #     html.P("Datos de entrada"),
    #     html.Pre( pprint.pformat(input_dict))
    # ])
    return json.dumps(input_dict)

###################### CALLBACK FRONTEND (FORMATOS) ###########################

# CALLBACK 1: Si se selecciona la tarifa 2.0TD no se pueden cargar potencia en P3C~P6C
@app.callback( 
    [
        Output("selector2-P1C", "disabled"),
        Output("selector2-P2C", "disabled"),
        Output("selector2-P3C", "disabled"),
        Output("selector2-P4C", "disabled"),
        Output("selector2-P5C", "disabled"), 
        Output("selector2-P6C", "disabled"),
        Output("selector3-table-potencia", "data"),
        Output("selector3-table-energia", "data"),
    ],
    [
        Input("selector1-tarifa-state", "value"),
    ],
)
def restringir_potencias(tarifa):
    if tarifa == "2.0TD":
        disabled_pot = [False, False, True, True, True, True]
        table1 = CargosPeajes_enPotencia("2.0TD").to_dict('records')
        table2 = CargosPeajes_enEnergia("2.0TD").to_dict('records')
        out = disabled_pot + [table1] + [table2]
        return out
    elif tarifa == "3.0TD":
        disabled_pot = [False, False, False, False, False, False]
        table1 = CargosPeajes_enPotencia("3.0TD").to_dict('records')
        table2 = CargosPeajes_enEnergia("3.0TD").to_dict('records')
        out = disabled_pot + [table1] + [table2]
        return out


######################## CALLBACKS DE BACKEND #################################

# CALLBACK 1: Pasan los valores a la función principal al pulsar el botón
@app.callback(
    [
        Output('output-alerts','children'),
        Output('output-boton','data')
    ],
    [
        Input( 'submit-button', 'n_clicks'),
    ],
    State( 'output-selectores', 'data')
)
def imprimir_alertas( clicks, data ):
    # ejecutar backend
    print("Comprobación...")
    inputs = json.loads(data)
    print(inputs)
    alerts, flag_continue = validation(inputs)
   
    if flag_continue: # Si todo está bien 
        print("Calculado")
        print("Funcion backend")
        data_output = json.dumps({})
        card_output = [ # Alerts que no me dajan seguir
            dbc.Card(
                dbc.CardBody([
                    html.H4("Validación satisfactoria", className = "card-title"),
                    html.P("Cantidad de días a calcular")
                ]),
                color = 'success',
                inverse=True    
            )
        ]
        return [card_output, data_output] #Nothing to do here   
    
    else: # Si algo falla. Regresa componentes
        print(inputs)
        data_output = json.dumps({})
        card_output = [ # Alerts que no me dajan seguir
            dbc.Card(
                dbc.CardBody([
                    html.H4("Alertas de validación", className = "card-title"),
                    html.Ul(
                        [ html.Li(alert) for alert in alerts]
                    )
                ]),
                color = 'warning',
                inverse=True    
            )
        ]
        
        return [card_output, data_output]
    



######################## CALLBACKS DE GRAFICACION ################################
# @app.callback(
#     Output('graph-componentes', 'figure'),
#     [Input('output-boton', 'children')])
# def build_componentes(json_data):
#     df_all = pd.read_json( json_data)
#     # Utilizar una funcion de backend para traer la data que nos interesa

#     df_graph, df_tidy, df_tidy2 = get_tidy_df(df_all)
    
#     fig = px.treemap(
#          df_tidy,
#          path=[px.Constant("Componentes"), "type", "variable"],
#          values="value",
#     )
#     return fig


# @app.callback(
#     Output('graph-generacion', 'figure'),
#     [Input('output-boton', 'children')])
# def build_generacion(json_data):
#     df_all = pd.read_json( json_data)
#     # Utilizar una funcion de backend para traer la data que nos interesa

#     df_gen = df_all.iloc[:, 13:36]
#     demanda = df_gen.loc[:, ['Total']] # Demanda
#     generacion = df_gen.loc[:, df_gen.columns != 'Total']
#     # 
#     estructura_gen = pd.melt(
#         generacion,
#         #id_vars="Ptarif",
#         value_vars=generacion.columns,
#         ignore_index=False,
#     )
#     # Graficar
#     fig = px.area( 
#         estructura_gen, 
#         x = estructura_gen.index, 
#         y = estructura_gen['value'], 
#         color = estructura_gen['variable'],
#         #animation_frame = dfgen1['datetime'].dt.hour,
#         range_y = [-5000,45000])
#     fig.add_trace( 
#         go.Scatter(
#             x = demanda.index,
#             y = demanda['Total'],
#             name = 'Demanda',
#             line = dict( color = "black" )
#         )
#     )

#     return fig


# @app.callback(
#     Output('graph-mercado','figure'),
#     [Input('output-boton', 'children')])
# def build_mercado(json_data):
#     df_all = pd.read_json( json_data)
#     # Utilizar una funcion de backend para traer la data que nos interesa
    
#     precio = df_all.iloc[: , 36:52]
#     pollution = df_all.iloc[:, 52:53]
    
#     comp_precio = precio.iloc[:,:-1]
#     total = precio.iloc[:,-1]

#     estructura_gen = pd.melt(
#         generacion,
#         #id_vars="Ptarif",
#         value_vars=generacion.columns,
#         ignore_index=False,
#     )
#     # Graficar
#     fig = px.area( 
#         estructura_gen, 
#         x = estructura_gen.index, 
#         y = estructura_gen['value'], 
#         color = estructura_gen['variable'],
#         #animation_frame = dfgen1['datetime'].dt.hour,
#         range_y = [-5000,45000])
#     fig.add_trace( 
#         go.Scatter(
#             x = demanda.index,
#             y = demanda['Total'],
#             name = 'Demanda',
#             line = dict( color = "black" )
#         )
#     )

#     return fig


##########################################
############# ENTRY POINT ################
##########################################
if __name__ == "__main__":
    # starting_values()
    app.run_server(debug=True)
    
    

