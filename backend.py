"""
Here is where all the data treatment function are located. The idea is to fill to use the data and take in 
"""
# %%
#  Python Utils
from datetime import datetime, timedelta
import plotly.express as px
import pandas as pd
import timeit

# Function Utils
from ree_dates import ree_periods

# Function Utils
from ree_dates import ree_periods

########################## FUNCIONES DE VALIDACIÓN ############################

def validation(inputs):
    """
    This functions takes the input dict and builds a set of alarms for
    """
    # Salidas
    alerts = []
    cont_flag = True
    # PASO 1: Comprobacion de potencias
    periodos = ['P1','P2','P3','P4','P5','P6']
    tariff = inputs['tarifa']
    potences = inputs['potencias']

    if tariff == '2.0TD':
        for p in periodos: 
            if potences[p] > 15.0:
                alerts.append(f"{p}C: Superior a máxima para 2.0TD (15kW)")
                cont_flag = False

    elif tariff == '3.0TD':
        pot_list = [] # greater than max number
        for p in periodos: 
            pot_list.append(potences[p])
        
        if ( all( pot_list[i] <= pot_list[i+1] for i in range(len(pot_list)-1))):
            cont_flag = True
        else: 
            alerts.append(f"Potencias no cumplen con P1<=P2...<=P6")
            cont_flag = False
    # PASO 2: Comprobaciones DataTable
    
    # PASO 3: Comprobar que las inputs no sean cero
    if inputs['margen_potencia'] == None: 
        alerts.append(f"El margen comercial no puede ser nulo. Insertar un número")
        cont_flag = False
    if inputs['alquiler_contador'] == None: 
        alerts.append(f"El pago por alquiler de equipos no puede ser nulo. Insertar un número")
        cont_flag = False
    if inputs['imp_electrico'] == None: 
        alerts.append(f"El impuesto eléctrico no puede ser nulo. Insertar un número")
        cont_flag = False
    if inputs['iva'] == None: 
        alerts.append(f"El IVA no puede ser nulo. Insertar un número")
        cont_flag = False
    
    #print('Validacion',alerts, cont_flag) 
    return alerts ,cont_flag



############ CALLBACKS PARA TRATAMIENTO DE DATOS DISPONIBLES ##################

def load_local_data( joined = True ):
    """
    The function load data from the given source. At the start, we
    are going to work with json files. In the following version I want to
    return the data from ESIOS api (or personal API):
    """
    # %%  1) Process "Power Generation" Data
    generation = pd.read_json(
        "./data/power_generation/export_GeneraciónProgramada +ConsumoBombeo +CableBalearesP48_2021-08-23_19_15.json",
        encoding="utf-8",
        dtype={"datetime": "str"},
    )
    generation["datetime"] = generation["datetime"].str.replace(
        "+01:00", "", regex=False
    )
    generation["datetime"] = generation["datetime"].str.replace(
        "+02:00", "", regex=False
    )
    generation.replace(
        {
            "Generación programada + Consumo bombeo + Cable Baleares P48": "Total",
            "Generación programada P48 Biogás": "Biogás",
            "Generación programada P48 Biomasa": "Biomasa",
            "Generación programada P48 Ciclo combinado": "Ciclo combinado",
            "Generación programada P48 Consumo bombeo": "Consumo bombeo",
            "Generación programada P48 Derivados del petróleo ó carbón": "Derivados del petróleo ó carbón",
            "Generación programada P48 Energía residual": "Energía residual",
            "Generación programada P48 Enlace Baleares": "Enlace Baleares",
            "Generación programada P48 Eólica terrestre": "Eólica terrestre",
            "Generación programada P48 Gas Natural Cogeneración": "Cogeneración",
            "Generación programada P48 Hidráulica UGH": "Hidráulica UGH",
            "Generación programada P48 Hidráulica no UGH": "Hidráulica no UGH",
            "Generación programada P48 Hulla antracita": "Hulla antracita",
            "Generación programada P48 Hulla sub-bituminosa": "Hulla sub-bituminosa",
            "Generación programada P48 Nuclear": "Nuclear",
            "Generación programada P48 Océano y geotérmica": "Océano y geotérmica",
            "Generación programada P48 Residuos domésticos y similares": "Residuos domésticos y similares",
            "Generación programada P48 Residuos varios": "Residuos varios",
            "Generación programada P48 Solar fotovoltaica": "Solar fotovoltáica",
            "Generación programada P48 Solar térmica": "Solar térmica",
            "Generación programada P48 Subproductos minería": "Subproductos minería",
            "Generación programada P48 Turbinación bombeo": "Turbinación bombeo",  # Hidroeléctrica reversible
            "Demanda programada P48 Corrección eólica": "Corrección eólica",
            "Demanda programada P48 Corrección solar": "Corrección eólica",
        },
        inplace=True,
    )

    generation["datetime"] = pd.to_datetime(generation["datetime"])
    generation = generation.pivot_table(
        values="value", columns="name", index="datetime", fill_value=0
    )

    # %% 2) Process "Energy Prices" data
    prices = pd.read_json(
        "./data/pvpc_prices/export_PrecioMedioHorarioFinalSumaDeComponentes_2021-08-23_19_18.json",
        encoding="utf-8",
        dtype={"datetime": "str"},
    )
    prices["datetime"] = prices["datetime"].str.replace("+01:00", "", regex=False)
    prices["datetime"] = prices["datetime"].str.replace("+02:00", "", regex=False)
    prices.replace(
        {
            "Precio medio horario componente banda secundaria ": "Banda Secundaria",
            "Precio medio horario componente control factor potencia ": " Control Factor Potencia",
            "Precio medio horario componente desvíos medidos ": " Desvíos Medidos",
            "Precio medio horario componente fallo nominación UPG ": " Fallo Nominación UPG",
            "Precio medio horario componente incumplimiento energía de balance ": " Incumplimiento Energía de Balance",
            "Precio medio horario componente mercado diario ": " Mercado Diario",
            "Precio medio horario componente mercado intradiario ": " Mercado Intradiario",
            "Precio medio horario componente pago de capacidad ": " Pago de Capacidad",
            "Precio medio horario componente reserva de potencia adicional a subir ": "Reserva de Potencia adicional a subir",
            "Precio medio horario componente restricciones PBF ": " Restricciones PBF",
            "Precio medio horario componente restricciones intradiario ": " Restricciones Intradiario",
            "Precio medio horario componente restricciones tiempo real ": " Restricciones tiempo real",
            "Precio medio horario componente saldo P.O.14.6 ": " Saldo P.O.14.6'",
            "Precio medio horario componente saldo de desvíos ": " Saldo de Desvíos",
            "Precio medio horario componente servicio de interrumpibilidad ": " Servicio de Interrumpibilidad",
            "Precio medio horario final suma de componentes": "Suma Componentes Precio",
        },
        inplace=True,
    )

    prices["datetime"] = pd.to_datetime(prices["datetime"])
    prices = prices.pivot_table(
        values="value", columns="name", index="datetime", fill_value=0
    )

    # %% 3) Process "Profile consuptions" data
    consumption_profiles = pd.read_csv(
        "./data/consumption_curves/perfiles_homemade.csv", sep=";", decimal=","
    )
    consumption_profiles["HORA"] = consumption_profiles["HORA"] - 1
    selection = consumption_profiles[["AÑO", "MES", "DIA", "HORA"]]
    selection = selection.rename(
        columns={"AÑO": "year", "MES": "month", "DIA": "day", "HORA": "hour"}
    )
    consumption_profiles["FECHA"] = pd.to_datetime(
        selection
    )  # .dt.tz_localize("UTC").dt.tz_convert("Europe/Madrid")
    consumption_profiles = consumption_profiles[
        ["FECHA", "VERANO(1)/INVIERNO(0)", "COEF. PERFIL P2.0TD", "COEF. PERFIL P3.0TD"]
    ]
    consumption_profiles = consumption_profiles.set_index("FECHA")

    # %% 4) Process "CO2 right" data
    pollution_taxes = pd.read_csv(
        "./data/other_markets/historico-precios-CO2-_2021_.csv", sep=";"
    )
    pollution_taxes["Fecha"] = pd.to_datetime(
        pollution_taxes["Fecha"], dayfirst=True
    )  # .dt.tz_localize("UTC").dt.tz_convert("Europe/Madrid")
    pollution_taxes = pollution_taxes.set_index("Fecha")
    pollution_taxes = pollution_taxes[["EUA"]]
    pollution_taxes = pollution_taxes.resample("1H").ffill()  # to have hourly data

    #min_date = df_aux.index.min().to_pydatetime()
    #max_date = df_aux.index.max().to_pydatetime()
    if joined == True: # Maybe in the future I don't want this data to be joined
        df_aux = pd.concat(
            [
                generation,
                prices,
                consumption_profiles,
                pollution_taxes,
            ],
            axis=1,
            join="inner",
        )
        return  df_aux
    else: 
        return generation, prices, consumption_profiles, pollution_taxes


def build_consumptions_df(
    df_ree, tarifa, normalized_consumption, potencias_contratadas
    ):
    """
    The function take the hired potencies indicated by the user and build a consumptions curve
    taking into account the consumptions profiles the REE publish every year, and month to month

    [Disclaimer]: I'm assuming that the user power consumption is directly related with the
    hired potence. We could have another function that takes a consumption csv files with real data.
    """

    if tarifa == "2.0TD":
        # For 2.0TD
        df_aux1 = pd.concat(
            [normalized_consumption["COEF. PERFIL P2.0TD"], df_ree.loc[:,["20TD_periods","weekday"]]],
            axis=1,
            join="inner",
        )

        df_aux1["PC"] = 10  # default values to create the column
        df_aux1["Consumo"] = 0.1  # default values to create the column

        df_aux1.loc[df_ree["20TD_periods"] == 1, "PC"] = potencias_contratadas["P1"]
        df_aux1.loc[df_ree["20TD_periods"] == 2, "PC"] = potencias_contratadas["P1"]
        df_aux1.loc[df_ree["20TD_periods"] == 3, "PC"] = potencias_contratadas["P2"]

        df_aux1["Consumo"] = df_aux1["COEF. PERFIL P2.0TD"] * df_aux1["PC"]  # kWh
  
        df_aux1 = df_aux1.drop(columns=["COEF. PERFIL P2.0TD"])
        df_aux1 = df_aux1.rename( columns = { "20TD_periods":"Periodos" })

    elif tarifa == "3.0TD":
        # For 3.0TD
        df_aux1 = pd.concat(
            [normalized_consumption["COEF. PERFIL P3.0TD"],  df_ree.loc[:,["30TD_periods","weekday"]]],
            axis=1,
            join="inner",
        )

        df_aux1["PC"] = 10
        df_aux1["Consumo"] = 0.1

        df_aux1.loc[df_ree["30TD_periods"] == 1, "PC"] = potencias_contratadas["P1"]
        df_aux1.loc[df_ree["30TD_periods"] == 2, "PC"] = potencias_contratadas["P2"]
        df_aux1.loc[df_ree["30TD_periods"] == 3, "PC"] = potencias_contratadas["P3"]
        df_aux1.loc[df_ree["30TD_periods"] == 4, "PC"] = potencias_contratadas["P4"]
        df_aux1.loc[df_ree["30TD_periods"] == 5, "PC"] = potencias_contratadas["P5"]
        df_aux1.loc[df_ree["30TD_periods"] == 6, "PC"] = potencias_contratadas["P6"]

        df_aux1["Consumo"] = df_aux1["COEF. PERFIL P3.0TD"] * df_aux1["PC"]# KWh

        df_aux1 = df_aux1.drop(columns=["COEF. PERFIL P3.0TD"])
        df_aux1 = df_aux1.rename( columns = { "30TD_periods":"Periodos" })

    elif tarifa == "6.1TD":
        # For 6.1TD
        pass

    return df_aux1


def total_df( inputs, generation, prices, profiles, taxes):
    """
    This is the function
    """
    inicio = datetime.fromisoformat(inputs['start_date'] )
    fin = datetime.fromisoformat(inputs['end_date'] ) + timedelta(hours=23)
    fechas_ree = ree_periods( inicio , fin )
    fechas_ree = fechas_ree.drop(columns=["year", "month", "day", "hour", "string"])
    # Paso 1
    curva_consumo = build_consumptions_df(
        fechas_ree, 
        inputs['tarifa'],
        profiles[ inputs['start_date'] : inputs['end_date'] ],
        inputs['potencias']
    )
    
    return curva_consumo



    # # Step 3: Build consumption curve
    # df_subtotal = df_terminos_hora.loc[:, ["Ptarif", "PC"]] 
    # df_subtotal.loc[:, "TF"] = T_Fijo
    # df_subtotal.loc[:, "TV"] = T_Variable
    # df_subtotal.loc[:, "IEE"] = (5.1127 / 100) * (df_subtotal["TF"].mean() + df_subtotal["TV"].mean())
    # df_subtotal.loc[:, "Alquiler"] = alquileres / (365 * 24)  # 2 euros al año
    # df_subtotal.loc[:, "SVA"] = adicionales / (365 * 24)
        
    # # Calculamos el total
    # df_total = df_subtotal.aggregate(
    #     {
    #         "Ptarif": "count",
    #         "TF": "mean",
    #         "TV": "mean",
    #         "IEE": "mean",
    #         "Alquiler": "sum",
    #         "SVA": "sum",
    #     }
    # )
    
    # iva = df_total[["TF", "TV", "IEE", "Alquiler"]].sum() * (
    #     impuestos["IVA"] / 100
    # )  #  10%

    # importe_factura = df_total[["TF", "TV", "IEE", "Alquiler"]].sum() + iva
    
    # df_total.loc['IVA'] = iva
    # df_total.loc['Suma'] = importe_factura
    
    # return (
    #     min_date,
    #     max_date,
    #     generation,
    #     prices,
    #     consumption_profiles,
    #     pollution_taxes,
    #     df_terminos_hora,
    #     df_subtotal,
    #     df_total,
    #     importe_factura,
    #)

def get_tidy_df(df_all):
    """
    Datepicker-Range de Dash returns a date_string in ISO format like this one "YYYY-MM-DD".
    The idea here is to filter the final data using the input of datepicker
    and return a few of perfectly treated DF that have what I need for graphics
    """

    #subtotales = df_subtotal[start_date:end_date]
    #terminos_hora = df_terminos_hora[start_date:end_date]

    # Volteamos la tortilla
    df_all.loc[ : , "Imp Electrico"] = df_all["IEE"] / len(df_all)
    df_all.loc[ : , "Imp IVA"] = df_all['IVA'] / len(df_all)
    df_all.loc[ : , "Alquiler"] = df_all["Alquiler"]

    df_all.loc[:, "Peajes Potencia"] = (
        0.001 * df_all["PC"] * df_all["peajes_Potencia"]
    )
    df_all.loc[:, "Margen Comercial"] = (
        0.001 * df_all["PC"] * df_all["Margen"]
    )
    df_all.loc[:, "Peajes Energia"] = (
        df_all["Curva_Consumo"] * df_all["peajes_Energia"]
    )
    df_all.loc[:, "Precio Mercado"] = (
        df_all["Curva_Consumo"] * df_all["Suma Componentes Precio"]
    )

    df_graph = df_all.loc[
        :,
        [
            "Ptarif",
            "Peajes Potencia",
            "Margen Comercial",
            "Peajes Energia",
            "Precio Mercado",
            "Alquiler",
            "Imp Electrico",
            "Imp IVA",
        ],
    ]

    # Limpiar lo que no está bien
    df_all = df_all.drop(
        columns=[
            "Peajes Potencia",
            "Margen Comercial",
            "Peajes Energia",
            "Precio Mercado",
        ]
    )

    #   %% Construimos el Dataframe bonito
    df_tidy = pd.melt(
        df_graph,
        id_vars="Ptarif",
        value_vars=[
            "Precio Mercado",
            "Peajes Potencia",
            "Peajes Energia",
            "Margen Comercial",
            "Alquiler",
            "Imp Electrico",
            "Imp IVA",
        ],
        ignore_index=False,
    )
    # Asignar Tipo
    df_tidy.loc[df_tidy["variable"] == "Precio Mercado", "type"] = "Mercado"
    df_tidy.loc[df_tidy["variable"] == "Peajes Potencia", "type"] = "Peajes"
    df_tidy.loc[df_tidy["variable"] == "Peajes Energia", "type"] = "Peajes"
    df_tidy.loc[df_tidy["variable"] == "Margen Comercial", "type"] = "Comercializadora"
    df_tidy.loc[df_tidy["variable"] == "Alquiler", "type"] = "Comercializadora"
    df_tidy.loc[df_tidy["variable"] == "Imp Electrico", "type"] = "Impuestos"
    df_tidy.loc[df_tidy["variable"] == "Imp IVA", "type"] = "Impuestos"

    df_tidy2 = pd.melt(
        df_graph.resample("1D").mean(),
        id_vars="Ptarif",
        value_vars=[
            "Precio Mercado",
            "Peajes Potencia",
            "Peajes Energia",
            "Margen Comercial",
            "Alquiler",
            "Imp Electrico",
            "Imp IVA",
        ],
        ignore_index=False,
    )

    print("Hurra!")
    return df_graph, df_tidy, df_tidy2


 
if __name__ == "__main__":
    pass
    # start_time = timeit.timeit()
    # (
        
    #     min_date,
    #     max_date,
    #     generation,
    #     prices,
    #     consumption_profiles,
    #     pollution_taxes,
    #     df_terminos_hora,
    #     df_subtotal,
    #     df_total,
    #     importe_factura,
    # ) = starting_backend(
    #     tarifa,
    #     potencias_contratadas,  # potencias_contratadas
    #     peajesYcargos_potencia_boe,  # peajesYcargos_potencia_boe
    #     peajesYcargos_energia_boe,  # peajesYcargos_energia_boe
    #     margen,
    #     alquileres,
    #     adicionales,
    #     impuestos,
    # )
    # end_time = timeit.timeit()
    # print("Listo: ", start_time - end_time)


# %%
    #   %% GRAFICAMOS ESTA LOCURITA
    fig1 = px.treemap(
        df_tidy, path=[px.Constant("Componentes"), "type", "variable"], values="value"
    )
    fig1.update_traces(root_color="lightgrey")
    fig1.update_layout(margin=dict(t=30, l=25, r=25, b=25))
    fig1.show()

    # fig = px.treemap(
    #     df_tidy,
    #     path=[px.Constant("Periodpros"), "Ptarif", "type", "variable"],
    #     values="value",
    # )
    # fig.show()
    # Este no muestra lo que quiero. Que es el aporte de cada uno por hora

    fig2 = px.bar(df_tidy2, x=df_tidy2.index, y="value", color="variable")
    fig2.show()
    # A esta figura le falta indicar el aporte porcentual de cada uno"""
