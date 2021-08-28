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
import json
import re

# Components
from components import *
from backend import starting_backend, get_tidy_df

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
        # Main title and information
        dbc.Row(  
            [
                dbc.Col(
                    html.Div(
                        children=[mainHeader]
                    ), xs=10, sm=10, md=10, lg=9, xl=9
                )
            ],
            justify="center",
        ),
        #Inputs
        dbc.Row(
            [  
                dbc.Col(
                    html.Div(
                        children=[selectores1, selectores2, selectores3,selectores4,selectores5]
                    ),xs=10, sm=10, md=10, lg=9, xl=9
                )
            ],
            justify="center",
        ),
        dbc.Row(# Date Selection
            [  
                dbc.Col(
                    html.Div(
                        children=[datePicker]
                    ), xs=10, sm=10, md=10, lg=9, xl=9
                )
            ],
            justify="center", 
        ),
        dbc.Row(  # Trigger
            [
                dbc.Col(
                    html.Div(
                        [botonCalcular]
                    ), xs=6, sm=6, md=6, lg=5, xl=5
                )
            ]
        ),
        #Auxiliary Output
        dbc.Row(
            [  
                dbc.Col(
                    html.Div(
                        children=[aux_output]
                    ), xs=10, sm=10, md=10, lg=9, xl=9
                )
            ],
            justify="center", 
        ),
        # Output
        dbc.Row(
            [  
                dbc.Col(
                    html.Div(
                        children=[treemap]
                    ), xs=10, sm=10, md=10, lg=9, xl=9
                )
            ],
            justify="center", 
        ),
    ]
)

################################## CALL THE APP ##############################

# Main Call for
app.layout = html.Div(children=[body])


########################## MAIN CALLBACKS ##############################
# CALLBACK 0: Callback inicial. Solo se ejecuta al inicio
@app.callback(
    Output('output-inicial','contentEditable'),
    Input('starting-title', 'loading_state')
)
def starting_values():
    # DEFAULT VARIABLES: Callback going to edit and recall these variables
    print("Callback 0: Inicial")
    
    tarifa_init = "2.0TD"
    potencias_contratadas = {
        "2.0TD": {  # kW
            "P1": 5100,  # P. Punta = P1P
            "P2": 3450,  # P. Punta = P2P
            "P3": 0,  # P. Valle = P3P
            "P4": 0,
            "P5": 0,
            "P6": 0,
        },
        "3.0TD": {  # kW
            "P1": 9810,
            "P2": 9810,
            "P3": 9810,
            "P4": 9810,
            "P5": 9810,
            "P6": 15001,
        },
        "6.1TD": {  # kW
            "P1": 50000,
            "P2": 100000,
            "P3": 100000,
            "P4": 100000,
            "P5": 100000,
            "P6": 125000,
        },
    }
    peajesYcargos_potencia_boe = (
        {  # €/KW.Año. Recuerda dividir entre (365*240 horas/Año
            "2.0TD": {"P1": 30.67, "P2": 1.42, "P3": 0, "P4": 0, "P5": 0, "P6": 0},
            "3.0TD": {
                "P1": 19.60,
                "P2": 13.78,
                "P3": 7.01,
                "P4": 6.11,
                "P5": 4.40,
                "P6": 2.64,
            },
            "6.1TD": {
                "P1": 30.54,
                "P2": 25.89,
                "P3": 14.91,
                "P4": 12.09,
                "P5": 3.94,
                "P6": 2.11,
            },
        }
    )
    peajesYcargos_energia_boe = {  # €/KWh. Se suman a cada hora de consumo
        "2.0TD": {
            "P1": 0.133118,
            "P2": 0.041772,
            "P3": 0.006001,
            "P4": 0,
            "P5": 0,
            "P6": 0,
        },
        "3.0TD": {
            "P1": 0.077436,
            "P2": 0.059310,
            "P3": 0.032102,
            "P4": 0.017413,
            "P5": 0.007897,
            "P6": 0.005056,
        },
        "6.1TD": {
            "P1": 0.050891,
            "P2": 0.039222,
            "P3": 0.021931,
            "P4": 0.012193,
            "P5": 0.004437,
            "P6": 0.002892,
        },
    }
    margen = 4
    alquileres = 2
    adicionales = 0
    impuestos = {"IVA": 10}
    (
        min_date,
        max_date,
        generation,
        prices,
        consumption_profiles,
        pollution_taxes,
        df_terminos_hora,
        df_subtotal,
        df_total,
        importe_factura,
    ) = starting_backend(
        tarifa_init, 
        potencias_contratadas, 
        peajesYcargos_potencia_boe, 
        peajesYcargos_energia_boe, 
        margen, 
        alquileres, 
        adicionales, 
        impuestos
    )
    print( "Fechas: ", min_date, "-", max_date)

    return ( 
        min_date,
        max_date,
        generation,
        prices,
        consumption_profiles,
        pollution_taxes,
        df_terminos_hora,
        df_subtotal,
        df_total,
        importe_factura
    )



# CALLBACK 1: Pasan los valores a la función principal al pulsar el botón
@app.callback( 
    Output('output-boton', 'children'),
    Input( 'submit-button', 'n_clicks'),[
        State( 'selector1-tarifa-state', 'value' ),
        State( 'selector2-P1C', 'value' ),
        State( 'selector2-P2C', 'value' ),
        State( 'selector2-P3C', 'value' ),
        State( 'selector2-P4C', 'value' ),
        State( 'selector2-P5C', 'value' ),
        State( 'selector2-P6C', 'value' ),
    ]
)
def pass_valores_backend( n_clicks, tarifa, p1c, p2c, p3c, p4c, p5c, p6c):
    print("Callback principal")
    # ejecutar backend
    print(tarifa)
    print(p1c, p2c, p3c, p4c, p5c, p6c)
    
    # REALIZAR COMPROBACIONES ANTES DE CONTINUAR
    potencias = [p1c, p2c, p3c, p4c, p5c, p6c]
    if all(potencias):
        print("Valores validos. Calculando")

    return None

# CALBACK 2: Actualizar los elementos que están en la app


################### CALLBACKS PARA LOS SELECTORESS #####################

@app.callback( # selector 1 afecta selector 2
    [
       Output("selector2-P1C", "disabled"),
       Output("selector2-P2C", "disabled"),
       Output("selector2-P3C", "disabled"),
       Output("selector2-P4C", "disabled"),
       Output("selector2-P5C", "disabled"), 
       Output("selector2-P6C", "disabled"),
       Output("selector2-P1C", "max"),
       Output("selector2-P2C", "max"),
       Output("selector2-P3C", "max"),
       Output("selector2-P4C", "max"),
       Output("selector2-P5C", "max"), 
       Output("selector2-P6C", "max"),
    ],
    [
        Input("selector1-tarifa-state", "value"),
    ],
)
def cambio_tarifa(
    selector_tarifa_value,
    ):
    print("Callback 1")
    template = "Calculando para Tarifa: {}."

    output_string = template.format(
        selector_tarifa_value,
    )
    global tarifa
    tarifa = selector_tarifa_value # Esta variable es global
    print(output_string)
    
    if tarifa == "2.0TD":
        dis_input = (False, False, True, True, True, True)
        max_pot = (15000, 15000, 0 , 0, 0 ,0 )
        return dis_input+max_pot
    elif tarifa == "3.0TD":
        dis_input = (False, False, False, False, False, False)
        max_pot = (50000, 50000, 50000 , 50000, 50000 ,50000 )
        return  dis_input+max_pot


@app.callback(  # selector 2 afecta selector FINAL
    [
        #Output("output-selectores", "children"),
        Output("submit-button",'disabled' )
    ],
    [
        Input("selector2-P1C", "value"),
        Input("selector2-P2C", "value"),
        Input("selector2-P3C", "value"),
        Input("selector2-P4C", "value"),
        Input("selector2-P5C", "value"),
        Input("selector2-P6C", "value")
    ],
)
def cambio_potencia(
    P1C_value,
    P2C_value,
    P3C_value,
    P4C_value,
    P5C_value,
    P6C_value,
    ):
    print("Callback 2")
    global potencias
    potencias = [P1C_value, P2C_value, P3C_value, P4C_value,P5C_value, P6C_value]
    
    return None


############# ENTRY POINT #######################
if __name__ == "__main__":

    app.run_server(debug=True)
