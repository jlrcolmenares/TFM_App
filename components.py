from logging import disable
import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_table
from dash.exceptions import PreventUpdate
import plotly.graph_objects as go
import plotly.express as px

from datetime import date
import json

# hidden_variables = html.Div(
#     [
#         html.Div( id='tarifa')
#     ], style = {'display': 'none'}
# )

########################## INPUT COMPONENTS #############################

mainHeader = html.Div(
    [
        dbc.Col([], ),
        dbc.Col(
            [
            html.H1("Factores que influyen en precio de la energía"),
            html.P("Un programa desarrollado por @joseluisramon"),
            ],
        )
    ], 
    id = 'starting-title', 
    style = dict( border = '1px solid #000')
)


selectores1 = dbc.FormGroup(
    [
        dbc.Label("Tarifa:"),
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
        dbc.Label("Potencias contratadas en vatios [W/año]"),
        dbc.InputGroup(
            [
                dbc.InputGroupAddon("P1C", addon_type="prepend"),
                dbc.Input(
                    #placeholder="",
                    type = "number", 
                    min = 1000, 
                    max = 30000, 
                    step = 1,
                    value = 0,
                    id='selector2-P1C'
                ),
            ], className="mb-3"
        ),
        dbc.InputGroup(
            [
                dbc.InputGroupAddon("P2C", addon_type="prepend"),
                dbc.Input(
                    #placeholder="",
                    type = "number", 
                    min = 1000, 
                    max = 30000, 
                    step = 1,
                    value = 0,
                    id='selector2-P2C'
                ),
            ], className="mb-3"
        ),
        dbc.InputGroup(
            [
                dbc.InputGroupAddon("P3C", addon_type="prepend"),
                dbc.Input(
                    #placeholder="",
                    type = "number", 
                    min = 1000, 
                    max = 30000, 
                    step = 1,
                    value = 0,
                    disabled = True,
                    id='selector2-P3C'
                ),
            ], className="mb-3"
        ),
        dbc.InputGroup(
            [
                dbc.InputGroupAddon("P4C", addon_type="prepend"),
                dbc.Input(
                    #placeholder="",
                    type = "number", 
                    min = 1000, 
                    max = 30000, 
                    step = 1,
                    value = 0,
                    disabled = True,
                    id='selector2-P4C'
                ),
            ], className="mb-3"
        ),
        dbc.InputGroup(
            [
                dbc.InputGroupAddon("P5C", addon_type="prepend"),
                dbc.Input(
                    #placeholder="",
                    type = "number", 
                    min = 1000, 
                    max = 30000, 
                    step = 1,
                    value = 0,
                    disabled = True,
                    id='selector2-P5C'
                ),
            ], className="mb-3"
        ),
        dbc.InputGroup(
            [
                dbc.InputGroupAddon("P6C", addon_type="prepend"),
                dbc.Input(
                    #placeholder="",
                    type = "number", 
                    min = 1000, 
                    max = 30000, 
                    step = 1,
                    value = 0,
                    disabled = True,
                    id='selector2-P6C'
                ),
            ], className="mb-3"
        )
    ]
)

selectores3 = html.Div(
    [
        html.H3("Peajes y Cargos"),
        dbc.CardHeader("Cargos y peajes en Potencia [EUR/kW/año]"),
        dbc.CardGroup([
            dbc.Card([
                dbc.CardBody(
                    [
                        html.H4("P1", className= "card-title"),
                        html.P(str(30.67))
                    ]
                )]
            ),
            dbc.Card([
                dbc.CardBody(
                    [
                        html.H4("P2", className= "card-title"),
                        html.P(str(1.23))
                    ]
                )]
            ),
            dbc.Card([
                dbc.CardBody(
                    [
                        html.H4("P3", className= "card-title"),
                        html.P(str(0))
                    ]
                )]
            ),
            dbc.Card([
                dbc.CardBody(
                    [
                        html.H4("P4", className= "card-title"),
                        html.P(str(0))
                    ]
                )]
            ),  
            dbc.Card([         
                dbc.CardBody(
                    [
                        html.H4("P5", className= "card-title"),
                        html.P(str(0))
                    ]
                )]
            ),
            dbc.Card([
                dbc.CardBody(
                    [
                        html.H4("P6", className= "card-title"),
                        html.P(str(0))
                    ]
                )]
            )
        ]),
        # Considera usar DashTable

    ]
)

selectores4 = html.Div(
    [
        html.H3("Relativos a la Comercialización"),
        dbc.CardGroup([
            dbc.Card([
                dbc.CardBody(
                    [
                        html.H4("Margen Comercial", className= "card-title"),
                        html.P(str(4)+" EUR/año")
                    ]
                )
            ]),
            dbc.Card([
                dbc.CardBody(
                    [
                        html.H4("Alquiler del Contador)", className= "card-title"),
                        html.P(str(2)+" EUR/año")
                    ]
                )
            ]),
            dbc.Card([
                dbc.CardBody(
                    [
                        html.H4("Servicios de Valor Añadido (SVA)", className= "card-title"),
                        html.P(str(0)+" EUR/kW/año")
                    ]
                )
            ]),
        ])
    ]
)

selectores5 = html.Div(
    [
        html.H3("Impuestos"),
        dbc.CardGroup([
            dbc.Card([
                dbc.CardBody(
                    [
                        html.H4("Impuesto Eléctrico", className= "card-title"),
                        html.P(str(5.117)+"%")
                    ]
                ),
                dbc.CardFooter( "Aplicable al término de potencia y de energia")
            ]),
            dbc.Card([
                dbc.CardBody(
                    [
                        html.H4("IVA", className= "card-title"),
                        html.P(str(10)+"%")
                    ]
                ),
                dbc.CardFooter( "Aplicable a la electrica + servicios adicionales")
            ]),
        ])
    ]
)


datePicker = html.Div(
    [
        html.P("Utilizando datos para la fecha (recuerda limitarla a 1 mes)"),
        # Esta fecha siempre tiene que ser anterior al día actual y los datos se traerán por medio de la API para empezar a probar podemos utilizar datos de 2020 para acá
        dcc.DatePickerRange(
            id="datepicker-range",
            min_date_allowed=date(2020, 1, 1),
            max_date_allowed=date.today(),
            initial_visible_month=date.today(),
            # end_date = date.today()
        ),
        html.P(id="output-container-datepicker-range"),
    ]
)
       

botonCalcular = dbc.Button(
    [
        dbc.Button(
            "Pasar variables",
            size="lg", 
            className = "mr-1",
            n_clicks = 0,
            disabled = False,
            id = 'submit-button'
        )
    ]
)

###################### AUXILIARY OUTPUT #################################
aux_output = html.Div(
    [
        html.Div(
            id = 'output-boton'
        ),
        html.Div(
            id= 'output-selectores'
        ),
        html.Div(
            id="output-inicial"
        ),
    ]   
)


########################## OUTPUT COMPONENTS #############################

def make_empty_fig():
    fig = go.Figure()
    fig.layout.paper_bgcolor = "#E5ECF6"
    fig.layout.plot_bgcolor = "#E5ECF6"
    return fig


treemap = html.Div(
    [
        dbc.Label("Componente del Precio"),
        html.Br(),
        dcc.Graph(id="price-treemap", figure=make_empty_fig()),
    ]
) 
    


# indicator_tabs = dbc.Tabs(
#     [
#         dbc.Tab(
#             [  # Consumo
#                 html.H4("Curva de Consumo"),
#                 html.P(
#                     " Selecciona el tipo de tarifa y la potencia que contrataría en cada periodo"
#                 ),
#                 dcc.Graph(id="consumption-graph", figure=make_empty_fig()),
#             ],
#             label="Consumo",
#         ),
#         dbc.Tab(
#             [  # Mercado y Generacion
#                 html.H4(
#                     "Precio del Mercado y generación"
#                 ),  # This is just to show of
#                 html.Br(),
#                 dcc.Graph(id="generation-graph", figure=make_empty_fig()),
#             ],
#             label="Generacion",
#         ),
#         dbc.Tab(
#             [
#                 html.H4("Cargos y Peajes"),
#                 html.P("Se aplica a los potencia contrata y la energía"),
#                 dcc.Dropdown(id="peajes_dropdown", options=[], value=None),
#                 html.Button("Agregar peaje", id="peajes_button", n_clicks=0),
#             ],
#             label="Cargos y Peajes",
#         ),
#         dbc.Tab([], label="Impuestos"),
#     ]
# ),style=dict(height=2000, padding="20px 5% 30px", border="1px solid #000")