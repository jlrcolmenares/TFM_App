import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_daq as daq
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
            html.Pre("Proyecto final del MSIET - Desarrollado por José Luis Colmenares - Universidad de Sevilla. 2021"),
            html.P("La aplicación está compuesta por seis secciones. Cada sección da acceso a variables que afectan el precio del recibo eléctrico y permite modificar las variables manualmente. Al pulsar el botón <Calcular recibo> se obtiene el precio a pagar por la factura eléctrica según las modificaciones y pueden visualizar distintas curvas"),
            ],
        )
    ],
    className = 'header--main',
    style = dict( margin = '50px 0px 20px', border = '2px solid black')
)


selectores1 = dbc.Row([
    dbc.Col([
        html.H2("Tarifa:"),
        html.P([
            "Seleccione la tarifa para la cual desea estimar el precio del recibo eléctrico. Las tarifas 2.0TD y 3.0TD tendrán los mismo márgenes de comercialización."],
            className = 'explanation'
        ),
        dbc.RadioItems(
            options=[
                {"label": "2.0TD", "value": "2.0TD"},
                {"label": "3.0TD", "value": "3.0TD"},
                {"label": "6.1TD", "value": "6.1TD", "disabled": True},
            ],
            value='2.0TD',
            id="selector1-tarifa-state",
        ),
    ], ),
    dbc.Col([
        html.H2("Curvas:"),
        html.P([
            "Puede trabajar con la curvas perfiladas de consumo y con el histórico de precio del mercado eléctrico o puede cargar sus propias curvas y ver cómo afectan al precio final."],
            className = 'explanation'
        ),
        dbc.Checklist(
            options = [
                {"label": 'Usar Perfiles REE', "value": 1, "disabled": True},
            ],
            value = [1],
            id = 'selector1-usar-perfiles', 
            switch = True,
        ),
        dbc.Checklist(
            options = [
                {"label": 'Usar Precios REE', "value": 1, "disabled": True},
            ],
            value = [1],
            id = 'selector1-usar-mercado', 
            switch = True,
        )
    ],),
])

selectores2 = dbc.FormGroup(
    [   
        html.H2("Potencias Contratadas:"),
        html.P([
            "Selecciones las que tiene contratadas (expresadas en kW/año) para cada uno de los periodos tarifarios."
            ], className = 'explanation'
        ),
        dbc.Row([
            dbc.Col(
                [
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
                ),
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
                ]       
            ),
            dbc.Col(
                [
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
                ]
            ),
        ], #no_gutters = True
        ),
        dbc.Tooltip(
            "P1C: Potencia Punta para 2.0TD",
            target="selector2-P1C",
        ),
        dbc.Tooltip(
            "P2C: Potencia Valle para 2.0TD",
            target="selector2-P2C",
        ),
    ], style = dict( margin = '20px 0px 0px')
)


selectores3 = html.Div(
    [
        html.H2("Peajes y Cargos"),
        html.P([
            "Los peajes de distribución y transporte aparecen descritos en BOE-A-2021-4565. Los cargos aparecen descritos en el BOE-A-2021-6390. La unidades en las que están expresados difieren:"],
            className = 'explanation'
        ),
        html.Ul([
            html.Li("En Potencia: Están expresados en [€/kW/año]"),
            html.Li("En Energía: Están expresados en [€/kWh]")
        ], className = 'explanation'),
        dbc.CardHeader("Peajes y Cargos Aplicables al Término de Potencia [€/kW/año]"),
        dash_table.DataTable(
            id='selector3-table-potencia',
            columns= [{"name": i, "id": i, "type": "numeric"} for i in CargosPeajes_enPotencia('6.1TD').columns],
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
                'overflow': 'hidden',
                'fontSize': '0.75rem',
            }
        ),
        dbc.CardHeader("Peajes y Cargos Aplicables al Término de Energia [€/kWh]"),
        dash_table.DataTable(
            id='selector3-table-energia',
            columns= [{"name": i, "id": i, "type": "numeric"} for i in CargosPeajes_enEnergia('6.1TD').columns],
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
                'overflow': 'hidden',
                'fontSize': '0.75rem',
            }
        ),
    ], style = dict( margin = '20px 0px 0px')
)


selectores4 = html.Div(
    [
        html.H2("Relativos a la Comercialización"),
        html.P([
            "El margen que se llevan las comercializadoras está regulados. El concepto a pagar por alquiler va a la distribuidora."
            ], className = 'explanation'),
        dbc.CardGroup([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Margen en potencia [€/kW/año]", className= "card-title"),
                    dbc.Input(
                        id = "selector4-margen-potencia",
                        placeholder = '€/kW/año',
                        type = "number",
                        value = 3.117,
                        min = 0, 
                        max = 50, 
                        step = 0.0001,
                    )
                ])
            ]),
            dbc.Card([
                dbc.CardBody([
                    html.H4("Alquiler del Contador [€/año]", className= "card-title"),
                    dbc.Input(
                        id = "selector4-contador",
                        placeholder = '€/año',
                        type = "number",
                        value = 16.32,
                        min = 0, 
                        max = 100, 
                        step = 0.01,
                    )  
                ])
            ]),
        ])
    ], style = dict( margin = '20px 0px 0px')
)


selectores5 = html.Div(
    [
        html.H2("Impuestos"),
        html.P([
            "Los impuesto a utilizar son el Impuesto Especial a la Electricidad (IEE) y el Impuesto al Valor Agregado (IVA). Estos están regulados por BOE pero se da la posibilidad de modificar los porcentajes"
            ], className = 'explanation'),
        dbc.CardGroup([
            dbc.Card([
                dbc.CardBody([
                    html.H4("IEE [%]", className= "card-title"),
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
                dbc.CardFooter([
                    "Aplicable a la suma del término de potencia y de energia"
                    ], className = 'explanation')
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
                dbc.CardFooter([
                    "Aplicable a la suma de todos los cargos"
                    ], className = 'explanation')
            ]),       
        ]),
    ],style = dict( margin = '20px 0px 0px')
)


selectores6 = html.Div(
    [
        html.H2("Rangos de Fechas"),
        html.P([
            "Las restricciones actuales de la aplicación solo permiten seleccionar fecha entre el 01 de junio de 2021 y el 31 de agosto de 2021."
            ], className = 'explanation'),
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
    ], style = dict( margin = '20px 0px 0px')
)
       

botonCalcular = html.Div(
    [ 
        dbc.Button(
        "Calcular Recibo Eléctrico",
        id = 'submit-button',
        color = "primary", 
        block = True,
        n_clicks = 0,
        disabled = False,
        style = dict(fontSize= '1.5rem', margin='20px 0px 80px'),
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
            id = "output-tiempo-graph",
        ),
        html.Div(
            id = "output-desglose",
            style = dict( width = '100%')
        ),
        
    ]   
)

def build_deglose( inputs, dict_out ):
    """
    Construir el desglose es un proceso más o menos fastidioso
    """
    valor1 = dict_out["Subt_Fijo"]
    d1_1 = [dbc.DropdownMenuItem(
        f"Término Fijo: {valor1:.3F} €",
        style = dict( fontSize = '1rem') 
    )]
    d1_2 = [
        dbc.DropdownMenuItem(
            f"{item[0]} = {item[1]:.3f} kW x ( ({item[2]:.3f} + {item[3]:.3f}) + {item[4]} ) €/kW/año x {item[5]:.3f} días/año) = {item[6]:.3f} €", 
            disabled=True,
            style = dict( fontSize = '0.75rem'),
            ) for item in dict_out["Termino_Fijo"]] 
    d1_3 = [dbc.DropdownMenuItem(divider=True)]
    
    valor2 = dict_out["Subt_Variable"]
    d2_1 = [dbc.DropdownMenuItem(
        f"Término Variable: {valor2:.3F} €",
        style = dict( fontSize = '1rem') 
    )]
    d2_2 = [
        dbc.DropdownMenuItem(
            f"{item[0]} = {item[1]:.3f} kWh x ( {item[2]:.3f} + {item[3]:.3f} + {item[4]:.3f} ) €/kWh = {item[5]:.3f} €", 
            disabled=True,
            style = dict( fontSize = '0.75rem'),
            ) for item in dict_out["Termino_Variable"]] 
    d2_3 = [dbc.DropdownMenuItem(divider=True)]


    valor31 = dict_out["IEE"]
    valor32 = inputs["imp_electrico"]
    d3_1 = [dbc.DropdownMenuItem(
        f"Impuesto Eléctrico: {valor31:.3F} €",
        style = dict( fontSize = '1rem') 
    )]
    d3_2 = [
        dbc.DropdownMenuItem(
            f"( {valor1:.3f} € + {valor2:.3f} € ) x {valor32:.3f}% = {valor31:.3f} €", 
            disabled=True,
            style = dict( fontSize = '0.75rem')
    )]
    d3_3 = [dbc.DropdownMenuItem(divider=True)]

    valor41 = dict_out["Contador"]
    valor42 = dict_out["Termino_Fijo"][0][5]
    valor43 = inputs["alquiler_contador"]
    d4_1 = [dbc.DropdownMenuItem(
        f"Alquiler del Contador: {valor41:.3F} €",
        style = dict( fontSize = '1rem') 
    )]
    d4_2 = [
        dbc.DropdownMenuItem(
            f"( {valor43:.3f} €/año x {valor42:.3f} días/año ) = {valor41:.3f} €", 
            disabled=True,
            style = dict( fontSize = '0.75rem')
    )]
    d4_3 = [dbc.DropdownMenuItem(divider=True)]

    valor51 = dict_out["IVA"]
    valor52 = inputs["iva"]
    d5_1 = [dbc.DropdownMenuItem(
        f"IVA: {valor51:.3F} €",
        style = dict( fontSize = '1rem') 
    )]
    d5_2 = [
        dbc.DropdownMenuItem(
            f"( {valor1:.3f} € + {valor2:.3f} € + {valor31:.3f} € + {valor41:.3f} € ) x {valor52:.3f}% = {valor51:.3f} €", 
            disabled=True,
            style = dict( fontSize = '0.75rem')
    )]
    d5_3 = [dbc.DropdownMenuItem(divider=True)]

    desglose_final = dbc.DropdownMenu(
        d1_1+d1_2+d1_3+d2_1+d2_2+d2_3+d3_1+d3_2+d3_3+d4_1+d4_2+d4_3+d5_1+d5_2+d5_3
        ,
        label = f"Total = {dict_out['Total']:.3f} €",
        color = "info",
        bs_size="lg",
    )

    return desglose_final


########################## OUTPUT COMPONENTS #############################

def make_empty_fig():
    fig = go.Figure()
    fig.layout.paper_bgcolor = "#E5ECF6"
    fig.layout.plot_bgcolor = "#E5ECF6"
    fig.layout.height = 800
    return fig


# Gráficos
graph_tabs = dbc.Tabs(
    [
        dbc.Tab(
            [ 
                html.H4("Componentes del Precio"), 
                dcc.Graph(id="components-graph", figure=make_empty_fig()),
            ],
            label="Componentes",
            style = dict( margin = '20px 0px 0px')
        ),
        dbc.Tab(
            [
                html.H4("Curva de Consumo"),
                dcc.Graph(id="consumption-graph", figure=make_empty_fig()),
            ],
            label="Consumo",
            style = dict( margin = '20px 0px 0px')
        ),
        dbc.Tab(
            [
                html.H4("Mercado"),
                dcc.Graph(id="market-graph", figure=make_empty_fig()),
            ],
            label="Mercado",
            style = dict( margin = '20px 0px 0px')
        ),
        dbc.Tab(
            [
                html.H4("Generación"),
                dcc.Graph(id="generation-graph", figure=make_empty_fig()),
            ],
            label="Generación",
            style = dict( margin = '20px 0px 0px')
        ),
    ], style = dict( margin = '20px 0px 0px')
)