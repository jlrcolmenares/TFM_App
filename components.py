from logging import disable
import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_table
import plotly.graph_objects as go
import plotly.express as px

from datetime import date
import pandas as pd
import json

# hidden_variables = html.Div(
#     [
#         html.Div( id='tarifa')
#     ], style = {'display': 'none'}
# )

######################### AUXILIARY VARIABLES ###########################
peajes_potencia = pd.DataFrame(
    [
        [23.469833,0.961130,0,0,0,0],
        [10.646876,9.302956,3.751315,2.852114,1.145308,1.145308],
        [21.245192,21.245192,11.530748,8.716048,0.560259,0.560259],
        [15.272489,15.272489,7.484607,6.676931,0.459003,0.459003],
        [11.548232,11.548232,6.320362,3.694683,0.708338,0.708338],
        [12.051156,9.236539,4.442575,3.369751,0.628452,0.628452],
    ], 
    columns = ['P1','P2','P3','P4','P5','P6',],
    index = ['2.0TD','3.0TD','6.1TD','6.2TD','6.3TD','6.4TD',]
)

peajes_energia = pd.DataFrame(
     [
        [0.027378,0.020624,0.000714,0,0,0],
        [0.018489,0.015664,0.008523,0.005624,0.000340,0.000340],
        [0.018838,0.015479,0.009110,0.005782,0.000328,0.000328],
        [0.010365,0.008432,0.004925,0.003143,0.000180,0.000180],
        [0.009646,0.008076,0.004937,0.002290,0.000264,0.000264],
        [0.008775,0.006983,0.004031,0.002996,0.000175,0.000175],
    ], 
    columns = ['P1','P2','P3','P4','P5','P6',],
    index = ['2.0TD','3.0TD','6.1TD','6.2TD','6.3TD','6.4TD',]
)

cargos_potencia = pd.DataFrame(
    [
        [7.202827,0.463229,0,0,0,0],
        [8.950109,4.478963,3.254069,3.254069,3.254069,1.491685],
        [9.290603,4.649513,3.378401,3.378401,3.378401,1.548434],
        [5.455758,2.730784,1.983912,1.983912,1.983912,0.909293],
        [4.368324,2.186024,1.588236,1.588236,1.588236,0.728054],
        [2.136839,1.069310,0.777032,0.777032,0.777032,0.356140],
    ],
    columns = ['P1','P2','P3','P4','P5','P6',],
    index = ['2.0TD','3.0TD','6.1TD','6.2TD','6.3TD','6.4TD',]
)

cargos_energia = pd.DataFrame(
    [
        [0.105740,0.021148,0.005287,0,0,0],
        [0.058947,0.043646,0.023579,0.011789,0.007557,0.004716],
        [0.032053,0.023743,0.012821,0.006411,0.004109,0.002564],
        [0.015039,0.011139,0.006016,0.003008,0.001928,0.001203],
        [0.012328,0.009132,0.004931,0.002466,0.001581,0.000986],
        [0.004683,0.003469,0.001873,0.000937,0.000600,0.000375],
    ],
    columns = ['P1','P2','P3','P4','P5','P6',],
    index = ['2.0TD','3.0TD','6.1TD','6.2TD','6.3TD','6.4TD',]
)

########################## AUXILIARY FUNCTIONS ##########################

def CargosPeajes_enPotencia(tarifa):
    df1 = peajes_potencia.loc[tarifa,:].rename( 'Peajes' )
    df2 = cargos_potencia.loc[tarifa,:].rename( 'Cargos' )
    return pd.concat([df1,df2],axis =1).T.reset_index().rename(columns={'index':'Concepto'})

def CargosPeajes_enEnergia(tarifa):
    df1 = peajes_energia.loc[tarifa,:].rename( 'Peajes' )
    df2 = cargos_energia.loc[tarifa,:].rename( 'Cargos' )
    return pd.concat([df1,df2],axis =1).T.reset_index().rename(columns={'index':'Concepto'})


########################## INPUT COMPONENTS #############################

mainHeader = html.Div(
    [
        dbc.Col(
            [
            html.H1("Factores que influyen en precio de la electricidad"),
            html.P("Un proyecto desarrollado para el TFM del MSIET \n Desarrollado por @joseluisramon"),
            ],
        )
    ], 
    style = dict( margin = '50px 0px 20px', border = '2px solid black')
)


selectores1 = dbc.FormGroup(
    [
        html.H2("Tarifa:"),
        dbc.RadioItems(
            options=[
                {"label": "2.0TD", "value": "2.0TD"},
                {"label": "3.0TD", "value": "3.0TD"},
                {"label": "6.1TD", "value": "6.1TD", "disabled": True},
            ],
            value='2.0TD',
            id="selector1-tarifa-state",
        ),
    ]
) 

selectores2 = dbc.FormGroup(
    [   
        html.H2("Potencias Contratadas:"),
        dbc.Label("Expresadas en kilovatios año [kW]"),
        dbc.Row([
            dbc.Col(
                dbc.InputGroup(
                    [
                        dbc.InputGroupAddon("P1C", addon_type="prepend"),
                        dbc.Input(
                            #placeholder="",
                            type = "number", 
                            min = 1, 
                            max = 250, 
                            step = 0.001,
                            value = 0,
                            id='selector2-P1C'
                        ),
                    ],
                )
            ),
            dbc.Col(
                dbc.InputGroup(
                    [
                        dbc.InputGroupAddon("P2C", addon_type="prepend"),
                        dbc.Input(
                            #placeholder="",
                            type = "number", 
                            min = 1, 
                            max = 250, 
                            step = 0.001,
                            value = 0,
                            id='selector2-P2C'
                        ),
                    ],
                ),
            ),
            dbc.Col(
                dbc.InputGroup(
                    [
                        dbc.InputGroupAddon("P3C", addon_type="prepend"),
                        dbc.Input(
                            #placeholder="",
                            type = "number", 
                            min = 1, 
                            max = 250, 
                            step = 0.001,
                            value = 0,
                            disabled = True,
                            id='selector2-P3C'
                        ),
                    ],
                ),
            ),
            dbc.Col(
                dbc.InputGroup(
                    [
                        dbc.InputGroupAddon("P4C", addon_type="prepend"),
                        dbc.Input(
                            #placeholder="",
                            type = "number", 
                            min = 1, 
                            max = 250, 
                            step = 0.001,
                            value = 0,
                            disabled = True,
                            id='selector2-P4C'
                        ),
                    ],
                ),
            ),
            dbc.Col(
                dbc.InputGroup(
                    [
                        dbc.InputGroupAddon("P5C", addon_type="prepend"),
                        dbc.Input(
                            #placeholder="",
                            type = "number", 
                            min = 1, 
                            max = 250, 
                            step = 0.001,
                            value = 0,
                            disabled = True,
                            id='selector2-P5C'
                        ),
                    ],
                ),
            ),
            dbc.Col(
                dbc.InputGroup(
                    [
                        dbc.InputGroupAddon("P6C", addon_type="prepend"),
                        dbc.Input(
                            #placeholder="",
                            type = "number", 
                            min = 1, 
                            max = 250, 
                            step = 0.001,
                            value = 0,
                            disabled = True,
                            id='selector2-P6C'
                        ),
                    ],
                ),
            ),
        ], no_gutters = True),
        dbc.Tooltip(
            "P1C: Potencia Valle para 2.0TD",
            target="selector2-P1C",
        ),
        dbc.Tooltip(
            "P2C: Potencia Punta para 2.0TD",
            target="selector2-P2C",
        ),
    ], # className="mb-3"
)


selectores3 = html.Div(
    [
        html.H2("Peajes y Cargos"),
        html.P("Los peajes de distribución y transporte aparecen descritos en BOE-XXXX. Los cargos aparecen descritos en el BOE-XXXX. La unidades en las que están expresados difieren: "
        ),
        html.Ul([
            html.Li("En Potencia: Están expresados en [EUR/kW/año]"),
            html.Li("En Energía: Están expresados en [EUR/kWh]")
        ]),
        dbc.CardHeader("Peajes y Cargos Aplicables al Término de Potencia"),
        dash_table.DataTable(
            id='selector3-table-potencia',
            columns= [{"name": i, "id": i} for i in CargosPeajes_enPotencia('6.1TD').columns],
            data=CargosPeajes_enPotencia('6.1TD').to_dict('records'),
            editable = True,
            style_header={
                'backgroundColor': 'rgb(50, 50, 50)',
                'color': 'white'
            },
            css=[{'selector': 'table', 'rule': 'table-layout: fixed'}],
            style_cell={
                'width': '{}%'.format(len(CargosPeajes_enPotencia('6.1TD').columns)),
                'textOverflow': 'ellipsis',
                'overflow': 'hidden'
            }
        ),
        dbc.CardHeader("Peajes y Cargos Aplicables al Término de Energia"),
        dash_table.DataTable(
            id='selector3-table-energia',
            columns= [{"name": i, "id": i} for i in CargosPeajes_enEnergia('6.1TD').columns],
            data=CargosPeajes_enEnergia('6.1TD').to_dict('records'),
            editable = True,
            style_header={
                'backgroundColor': 'rgb(80, 80, 80)',
                'color': 'white'
            },
            css=[{'selector': 'table', 'rule': 'table-layout: fixed'}],
            style_cell={
                'width': '{}%'.format(len(CargosPeajes_enEnergia('6.1TD').columns)),
                'textOverflow': 'ellipsis',
                'overflow': 'hidden'
            }
        ),
    ]
)


selectores4 = html.Div(
    [
        html.H2("Relativos a la Comercialización"),
        html.P("El margen que se lleva las comercializadoras está regulados por el BOE-XXX. El concepto por alquiler va a la distribuidora. Igual dejamos abierto la posibilida de modificarlos para ver como afectan la factura final"),
        dbc.CardGroup([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Margen en potencia [EUR/kW/año]", className= "card-title"),
                    dbc.Input(
                        id = "selector4-margen-potencia",
                        placeholder = 'EUR/kW/año',
                        type = "number",
                        min = 0, 
                        max = 50, 
                        step = 0.01,
                    )
                ])
            ]),
            dbc.Card([
                dbc.CardBody([
                    html.H4("Alquiler del Contador [EUR/año]", className= "card-title"),
                    dbc.Input(
                        id = "selector4-contador",
                        placeholder = 'EUR/año',
                        type = "number",
                        min = 0, 
                        max = 50, 
                        step = 0.0001,
                    )  
                ])
            ]),
        ])
    ]
)


selectores5 = html.Div(
    [
        html.H2("Impuestos"),
        html.P("Los impuesto a utilizar son los impuestos designados por BOE. Aún así se da la posibilidad de modificar los porcentajes"),
        dbc.CardGroup([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Impuesto Eléctrico [%]", className= "card-title"),
                    dbc.Input(
                            id = "selector5-imp-elect",
                            #placeholder = '%',
                            type = "number",
                            value = 5.11269632,
                            min = 0, 
                            max = 10, 
                            step = 0.00000001,
                        )  
                    ]),
                dbc.CardFooter( "Aplicable a la suma del término de potencia y de energia")
            ]),
            dbc.Card([
                dbc.CardBody([
                        html.H4("IVA [%]", className= "card-title"),
                        dbc.Input(
                            id = "selector5-imp-iva",
                            #placeholder = '%',
                            type = "number",
                            value = 10,
                            min = 0, 
                            max = 27, 
                            step = 1,
                        )  
                    ]),
                dbc.CardFooter( "Aplicable a la sumatoria de todos los cargos")
            ]),       
        ]),
    ]
)


selectores6 = html.Div(
    [
        html.H2("Rangos de Fechas"),
        html.P("Las restricciones actuales de la aplicación solo permiten seleccionar fecha entre el 01 de junnio de 2021 y el 31 de agosto de 2021."),
        # Esta fecha siempre tiene que ser anterior al día actual y los datos se traerán por medio de la API para empezar a probar podemos utilizar datos de 2020 para acá
        dbc.Row([
            dcc.DatePickerRange(
                id="selector6-datepicker",
                min_date_allowed=date(2021,6,1),
                max_date_allowed=date(2021,9,1),
                initial_visible_month=date(2021,7,1),
                display_format = "DD/MM/YYYY",
                start_date_placeholder_text = "01/06/2021", 
                end_date_placeholder_text = "01/09/2021", 
                
                with_portal=True
            ),
        ], justify = 'center'),
    ],
)
       

botonCalcular = html.Div(
    [ 
        dbc.Button(
        "Calcular precio",
        id = 'submit-button',
        color="primary", 
        block = True,
        n_clicks = 0,
        disabled = False,
        style = dict(fontSize= '24pt', margin='50px 0px 100px'),
        ),
    ]
)


###################### AUXILIARY OUTPUT #################################

aux_output = html.Div(
    [
        dcc.Store(
            id = "output-selectores",
        ),
        html.Div(
            id = "output-alerts"
        ),
        dcc.Store(
            id = "output-boton",
        ),
    ]   
)

########################## OUTPUT COMPONENTS #############################

def make_empty_fig():
    fig = go.Figure()
    fig.layout.paper_bgcolor = "#E5ECF6"
    fig.layout.plot_bgcolor = "#E5ECF6"
    return fig

# Desglose
desglose = html.Div([
    dbc.Card([
        dbc.CardHeader("Termino Fijo"),
        dbc.CardBody([
        
        ]),
        dbc.CardHeader("Termino Variable"),
        dbc.CardBody([
        
        ])
    ],
    color="info",
    outline=True
    )
])

# Gráficos
graph_tabs = dbc.Tabs(
    [
        dbc.Tab(
            [
                html.H4("Curva de Consumo"),
                dcc.Graph(id="consumption-graph", figure=make_empty_fig()),
            ],
            label="Consumo",
        ),
        dbc.Tab(
            [ 
                html.H4("Componentes del Precio"), 
                dcc.Graph(id="components-graph", figure=make_empty_fig()),
            ],
            label="Componentes",
        ),
        dbc.Tab(
            [
                html.H4("Mercado"),
                dcc.Graph(id="marker-graph", figure=make_empty_fig()),
            ],
            label="Mercado",
        ),
        dbc.Tab(
            [
                html.H4("Generación"),
                dcc.Graph(id="generation-graph", figure=make_empty_fig()),
            ],
            label="Generación",
        ),
    ],
)