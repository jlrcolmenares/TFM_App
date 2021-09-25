"""
Here is where all the data treatment function are located. The idea is to fill to use the data and take in 
"""
#  Python Utils
from datetime import datetime, timedelta
import plotly.express as px
import pandas as pd
import timeit

# Function Utils
from ree_dates import ree_periods


def build_data_sources():
    """
    This function takes json and csv files from scraping stage and transform 
    then into pickle files that are more actionable and usable inside the main app
    """
    # 1) Process "Power Generation" Data
    generation = pd.read_json(
        "./data/power_generation/export_GeneraciónProgramada +ConsumoBombeo +CableBalearesP48_2021-09-14_17_49.json",
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
    generation.to_pickle("./data/power_generation/generation.pkl")

    # 2) Process "Energy Prices" data
    prices = pd.read_json(
        "./data/energy_prices/export_PrecioMedioHorarioFinalSumaDeComponentes_2021-09-14_18_14.json",
        encoding="utf-8",
        dtype={"datetime": "str"},
    )
    prices["datetime"] = prices["datetime"].str.replace("+01:00", "", regex=False)
    prices["datetime"] = prices["datetime"].str.replace("+02:00", "", regex=False)

    prices.replace(
        {
            "Precio medio horario componente banda secundaria ": "Banda Secundaria",
            "Precio medio horario componente control factor potencia ": "Control Factor Potencia",
            "Precio medio horario componente desvíos medidos ": "Desvíos Medidos",
            "Precio medio horario componente fallo nominación UPG ": "Fallo Nominación UPG",
            "Precio medio horario componente incumplimiento energía de balance ": "Incumplimiento Energía de Balance",
            "Precio medio horario componente mercado diario ": "Mercado Diario",
            "Precio medio horario componente mercado intradiario ": "Mercado Intradiario",
            "Precio medio horario componente pago de capacidad ": "Pago por Capacidad",
            "Precio medio horario componente reserva de potencia adicional a subir ": "Reserva de Potencia adicional a subir",
            "Precio medio horario componente restricciones PBF ": "Restricciones PBF",
            "Precio medio horario componente restricciones intradiario ": "Restricciones Intradiario",
            "Precio medio horario componente restricciones tiempo real ": "Restricciones tiempo real",
            "Precio medio horario componente saldo P.O.14.6 ": "Saldo P.O.14.6",  # Intercambios internacionales no Realizados
            "Precio medio horario componente saldo de desvíos ": "Saldo de Desvíos",
            "Precio medio horario componente servicio de interrumpibilidad ": "Interrumpibilidad",
            "Precio medio horario final suma de componentes": "Suma Componentes Precio",  # TOTAL
        },
        inplace=True,
    )

    prices["datetime"] = pd.to_datetime(prices["datetime"])
    prices = prices.pivot_table(
        values="value", columns="name", index="datetime", fill_value=0
    )

    prices["Desvíos"] = prices["Desvíos Medidos"] + prices["Saldo de Desvíos"]
    prices["Restricciones"] = (
        prices["Restricciones Intradiario"]
        + prices["Restricciones tiempo real"]
        + prices["Restricciones PBF"]
        + prices["Saldo P.O.14.6"]
    )
    prices["Otros Ajustes"] = (
        prices["Banda Secundaria"]
        + prices["Control Factor Potencia"]
        + prices["Fallo Nominación UPG"]
        + prices["Incumplimiento Energía de Balance"]
        + prices["Reserva de Potencia adicional a subir"]
    )

    prices = prices.drop(
        columns={
            "Desvíos Medidos",
            "Saldo de Desvíos",
            "Restricciones Intradiario",
            "Restricciones tiempo real",
            "Restricciones PBF",
            "Saldo P.O.14.6",
            "Banda Secundaria",
            "Control Factor Potencia",
            "Fallo Nominación UPG",
            "Incumplimiento Energía de Balance",
            "Reserva de Potencia adicional a subir",
        }
    )
    prices.to_pickle(
        "./data/energy_prices/prices.pkl",
    )

    # 3) Process "Profile consuptions" data
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
    consumption_profiles.to_pickle(
        "./data/consumption/consump_profiles.pkl",
    )

    # 4) Process "CO2 right" data
    pollution_taxes = pd.read_csv(
        "./data/other_markets/historico-precios-CO2-_2021_.csv", sep=";"
    )
    pollution_taxes["Fecha"] = pd.to_datetime(
        pollution_taxes["Fecha"], dayfirst=True
    )  # .dt.tz_localize("UTC").dt.tz_convert("Europe/Madrid")
    pollution_taxes = pollution_taxes.set_index("Fecha")
    pollution_taxes = pollution_taxes[["EUA"]]
    pollution_taxes = pollution_taxes.resample("1H").ffill()  # hourly data format
    pollution_taxes.to_pickle(
        "./data/other_markets/co2_rights.pkl",
    )

    # 5) Spanish Gas Indexes prices
    gas_prices = pd.read_csv("./data/other_markets/mibgas.csv", sep=";", decimal=",")
    gas_prices["Fecha"] = pd.to_datetime(gas_prices["Delivery day"], dayfirst=True)

    gas_prices = gas_prices.set_index("Fecha")
    gas_prices = gas_prices[["MIBGAS Index\n[EUR/MWh]"]]
    gas_prices.columns = ["MIBGAS Index"]
    gas_prices = gas_prices.resample("1H").ffill()
    gas_prices.to_pickle(
        "./data/other_markets/gas_index.pkl",
    )


########################## FUNCIONES DE VALIDACIÓN ############################


def validation(inputs):
    """
    This functions takes the input dict and builds a set of alarms for
    """
    # Salidas
    alerts = []
    cont_flag = True
    # PASO 1: Comprobacion de potencias
    periodos = ["P1", "P2", "P3", "P4", "P5", "P6"]
    tariff = inputs["tarifa"]
    potences = inputs["potencias"]

    try:
        if tariff == "2.0TD":
            for p in periodos[:2]:
                if potences[p] == 0:
                    alerts.append(f"{p}C: No puede ser cero")
                    cont_flag = False

                if potences[p] > 15.0:
                    alerts.append(f"{p}C: Superior a máxima para 2.0TD (15kW)")
                    cont_flag = False

        elif tariff == "3.0TD":
            pot_list = []  # greater than max number

            for p in periodos:
                pot_list.append(potences[p])
                if potences[p] == 0:
                    alerts.append(f"{p}C: No puede ser cero")
                    cont_flag = False

            if all(pot_list[i] <= pot_list[i + 1] for i in range(len(pot_list) - 1)):
                cont_flag = True
            else:
                alerts.append(f"Potencias no cumplen con P1<=P2...<=P6")
                cont_flag = False
        # PASO 2: Comprobaciones DataTable

        # PASO 3: Comprobar que las inputs no sean cero
        if inputs["margen_potencia"] == None:
            alerts.append(f"El margen comercial no puede ser nulo. Insertar un número")
            cont_flag = False
        if inputs["alquiler_contador"] == None:
            alerts.append(
                f"El pago por alquiler de equipos no puede ser nulo. Insertar un número"
            )
            cont_flag = False
        if inputs["imp_electrico"] == None:
            alerts.append(
                f"El impuesto eléctrico no puede ser nulo. Insertar un número"
            )
            cont_flag = False
        if inputs["iva"] == None:
            alerts.append(f"El IVA no puede ser nulo. Insertar un número")
            cont_flag = False

        # print('Validacion',alerts, cont_flag)
        return alerts, cont_flag
    except TypeError:
        alerts.append(f"Alguno de los datos de entrada se encuentra vacío. Completar")
        cont_flag = False


############ CALLBACKS PARA TRATAMIENTO DE DATOS DISPONIBLES ##################


def load_local_data(joined=True):
    """This funcion consolidated data from the scraping phase and put it in disposition to the app.

    Returns:
        [dataframe]: dataframe with each one of the sources available
    """
    generation = pd.read_pickle("./data/power_generation/generation.pkl")
    prices = pd.read_pickle("./data/energy_prices/prices.pkl")
    consumption_profiles = pd.read_pickle("./data/consumption/consump_profiles.pkl")
    pollution_taxes = pd.read_pickle("./data/other_markets/co2_rights.pkl")
    gas_prices = pd.read_pickle("./data/other_markets/gas_index.pkl")

    # min_date = df_aux.index.min().to_pydatetime()
    # max_date = df_aux.index.max().to_pydatetime()
    if joined == True:  # Maybe in the future I don't want this data to be joined
        df_aux = pd.concat(
            [generation, prices, consumption_profiles, pollution_taxes, gas_prices],
            axis=1,
            join="inner",
        )
        return df_aux
    else:
        return generation, prices, consumption_profiles, pollution_taxes, gas_prices


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
            [
                normalized_consumption["COEF. PERFIL P2.0TD"],
                df_ree.loc[:, ["20TD_periods", "weekday"]],
            ],
            axis=1,
            join="inner",
        )

        df_aux1["PC"] = 10  # default values to create the column
        df_aux1["Consumo"] = 0.1  # default values to create the column

        df_aux1.loc[df_ree["20TD_periods"] == 1, "PC"] = potencias_contratadas["P1"]
        df_aux1.loc[df_ree["20TD_periods"] == 2, "PC"] = potencias_contratadas["P1"]
        df_aux1.loc[df_ree["20TD_periods"] == 3, "PC"] = potencias_contratadas["P2"]

        df_aux1["Consumo"] = (
            df_aux1["COEF. PERFIL P2.0TD"] * df_aux1["PC"] * 1000
        )  # kWh

        df_aux1 = df_aux1.drop(columns=["COEF. PERFIL P2.0TD"])
        df_aux1 = df_aux1.rename(columns={"20TD_periods": "Periodos"})

    elif tarifa == "3.0TD":
        # For 3.0TD
        df_aux1 = pd.concat(
            [
                normalized_consumption["COEF. PERFIL P3.0TD"],
                df_ree.loc[:, ["30TD_periods", "weekday"]],
            ],
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

        df_aux1["Consumo"] = (
            df_aux1["COEF. PERFIL P3.0TD"] * df_aux1["PC"] * 1000
        )  # KWh

        df_aux1 = df_aux1.drop(columns=["COEF. PERFIL P3.0TD"])
        df_aux1 = df_aux1.rename(columns={"30TD_periods": "Periodos"})

    elif tarifa == "6.1TD":
        # For 6.1TD
        pass

    return df_aux1


def termino_potencia(
    df_ree, tarifa, potences, peajes_potencia, cargos_potencia, margen
):
    """This functions calculates the termino de potencia

    Args:
        df_ree ([datafram]):
        tarifa ([string]):
        potences ([list]):
        peajes_potencia ([list]):
        cargos_potencia ([list]):
        margen ([float]):

    Returns:
        comp_fija [dataframe]:
    """
    dias = len(df_ree.resample("1D").count())
    K = dias / 356  # constante que contiene dias/año

    if tarifa == "2.0TD":
        out_list = []
        for p in ["P1", "P2"]:
            out_list.append(
                [
                    p,
                    potences[p],
                    peajes_potencia[p],
                    cargos_potencia[p],
                    0,
                    (dias / 365),
                    (potences[p] * (peajes_potencia[p] + cargos_potencia[p]) * (K)),
                ]
            )

        out_list.append(
            [
                "Ppunta",
                potences["P1"],
                0,
                0,
                margen,
                (dias / 365),
                (potences["P1"] * (margen) * (K)),
            ]
        )

    elif tarifa == "3.0TD":
        out_list = []
        for p in ["P1", "P2", "P3", "P4", "P5", "P6"]:
            out_list.append(
                [
                    p,
                    potences[p],
                    peajes_potencia[p],
                    cargos_potencia[p],
                    0,
                    (dias / 365),
                    (potences[p] * (peajes_potencia[p] + cargos_potencia[p]) * (K)),
                ]
            )

        out_list.append(
            [
                "Ppunta",
                potences["P1"],
                0,
                0,
                margen,
                (dias / 365),
                (potences["P1"] * (margen) * (K)),
            ]
        )

    elif tarifa == "6.1TD":
        pass

    df = pd.DataFrame(
        out_list,
        columns=[
            "Periodos",
            "PC",
            "peajes_Potencia",
            "cargos_Potencia",
            "Margen",
            "K.dias",
            "T_Fijo",
        ],
    )
    return df


def termino_energia(
    df_ree, tarifa, peajes_energia, cargos_energia, curva_consumo, prices
):
    """Calculates el termino de energia considering inputs

    Args:
        df_ree ([dataframe]):
        tarifa ([string]):
        peajes_energia ([list]):
        cargos_energia ([list]):
        curva_consumo ([dataframe]):
        prices ([dataframe]):

    Returns:
        comp_variable [dataframe]:
    """
    if tarifa == "2.0TD":
        # For 2.0TD
        df_aux = df_ree.loc[:, ["feriado_finde", "20TD_periods"]]
        for p in ["P1", "P2", "P3"]:
            df_aux.loc[
                df_aux["20TD_periods"] == int(p[-1]), "peajes_Energia"
            ] = peajes_energia[p]
            df_aux.loc[
                df_aux["20TD_periods"] == int(p[-1]), "cargos_Energia"
            ] = cargos_energia[p]

    elif tarifa == "3.0TD":
        # For 3.0TD
        df_aux = df_ree.loc[:, ["feriado_finde", "30TD_periods"]]
        for p in ["P1", "P2", "P3", "P4", "P5", "P6"]:
            df_aux.loc[
                df_aux["30TD_periods"] == int(p[-1]), "peajes_Energia"
            ] = peajes_energia[p]
            df_aux.loc[
                df_aux["30TD_periods"] == int(p[-1]), "cargos_Energia"
            ] = cargos_energia[p]

    elif tarifa == "6.1TD":
        # For 6.1TD
        pass

    peajesYcargos = df_aux.iloc[:, -2:]

    df_aux2 = pd.concat(
        [
            curva_consumo.drop(columns=["weekday"]),
            peajesYcargos,
            prices["Suma Componentes Precio"].rename("PrecioEnergia") * 0.001,
        ],
        axis=1,
        join="inner",
    )

    df_aux2["T_Variable"] = 0.001  # default values to create the column
    # The variable component (termino variable) is calculated easily with hourly division
    df_aux2["T_Variable"] = (df_aux2["Consumo"]) * (
        df_aux2["peajes_Energia"] + df_aux2["cargos_Energia"] + df_aux2["PrecioEnergia"]
    )

    df_aux3 = df_aux2.groupby("Periodos").aggregate(
        {
            "PC": "mean",
            "Consumo": "sum",
            "peajes_Energia": "mean",
            "cargos_Energia": "mean",
            "PrecioEnergia": "mean",
            "T_Variable": "sum",
        }
    )

    # df_aux2 para treemap, df_aux3 para desglose
    return df_aux3


def precio_final(termino_potencia, termino_energia, imp_electrico, contador, iva):
    """This function take the rest of input and calculate the final price in the bILL

    Args:
        termino_potencia ([dataframe]):
        termino_energia ([dataframe]):
        imp_electrico ([float]):
        contador ([float]):
        iva ([float]):

    Returns:
        [dataframe]: to build the graph
        [dict]: to build the desglose
    """
    subt_fijo = termino_potencia["T_Fijo"].sum()
    subt_variable = termino_energia["T_Variable"].sum()
    subt_impElec = (subt_fijo + subt_variable) * (imp_electrico / 100)
    subt_contador = contador * termino_potencia["K.dias"].values[0]
    subt_iva = (subt_fijo + subt_variable + subt_impElec + subt_contador) * (iva / 100)
    total = subt_fijo + subt_variable + subt_impElec + subt_contador + subt_iva

    out1, out2, out3 = 0, 0, 0
    for index, row in termino_energia.iterrows():
        out1 = out1 + row["Consumo"] * row["peajes_Energia"]
        out2 = out2 + row["Consumo"] * row["cargos_Energia"]
        out3 = out3 + row["Consumo"] * row["PrecioEnergia"]

    out1 = ["Peajes", out1]
    out2 = ["Cargos", out2]
    out3 = ["Energía", out3]

    out4, out5, out6 = 0, 0, 0
    for index, row in termino_potencia.iterrows():
        out4 = out4 + row["PC"] * row["peajes_Potencia"] * row["K.dias"]
        out5 = out5 + row["PC"] * row["cargos_Potencia"] * row["K.dias"]
        out6 = out6 + row["PC"] * row["Margen"] * row["K.dias"]

    out4 = ["Peajes", out4]
    out5 = ["Cargos", out5]
    out6 = ["Margen", out6]

    out7 = ["Contador", subt_contador]
    out8 = ["Impuestos", subt_impElec]
    out9 = ["Impuestos", subt_iva]

    out_list = [out1, out2, out3, out4, out5, out6, out7, out8, out9]

    df_out = (
        pd.DataFrame(out_list, columns=["Concepto", "Euros"]).groupby("Concepto").sum()
    )
    df_out = df_out.reset_index()
    df_out["Porcent"] = df_out["Euros"] / df_out["Euros"].sum()

    total = df_out["Euros"].sum()  # ATENCIÓN AQUÍ
    str_otros = [subt_fijo, subt_variable, subt_impElec, subt_contador, subt_iva, total]

    return df_out, str_otros


def temporal_df(inputs, generation, prices, profiles, taxes, gas):
    """This function builds a dataframe with all the data availble in the time range that is selected for the user. It also consider REE Periods

    Args:
        inputs ([dict]): Python dict with the options selected in the input form
        generation ([dataframe]): dataframe built with historical scraped data
        prices ([dataframe]): dataframe built with historical scraped data
        profiles ([dataframe]): dataframe built with historical scraped data
        taxes ([dataframe]): dataframe built with historical scraped data
        gas ([dataframe]): dataframe built with historical scraped data

    Returns:
        temporal_data [dataframe]: dataframe of concatenated data by column
    """
    inicio = datetime.fromisoformat(inputs["start_date"])
    fin = datetime.fromisoformat(inputs["end_date"]) + timedelta(hours=23)
    fechas_ree = ree_periods(inicio, fin)
    fechas_ree = fechas_ree.drop(columns=["year", "month", "day", "hour", "string"])
    # Paso 1: Crear curva de consumo
    curva_consumo = build_consumptions_df(
        fechas_ree,
        inputs["tarifa"],
        profiles[inputs["start_date"] : inputs["end_date"]],
        inputs["potencias"],
    )

    profiles = profiles[inputs["start_date"] : inputs["end_date"]]
    generation = generation[inputs["start_date"] : inputs["end_date"]]
    prices = prices[inputs["start_date"] : inputs["end_date"]]
    taxes = taxes[inputs["start_date"] : inputs["end_date"]]
    gas = gas[inputs["start_date"] : inputs["end_date"]]

    # curva_consumo = salida.iloc[:,0:4]
    # prices = salida.iloc[:,4:12]
    # generation = salida.iloc[:, 12:35]
    # taxes = salida.iloc[:, 35:36]
    # gas = salida.iloc[:, 36:37]

    return pd.concat([curva_consumo, prices, generation, taxes, gas], axis=1)


def total_df(inputs, curva_consumo, prices):
    """This function takes the inputs of the form, the prices and the curva de consumo
    indicated for the user and calculate de total price in euros of the electrical bill
    for the daterange selected in the form

    Args:
        inputs ([dict]): The input form throws a build a json dict with all the input data
        curva_consumo ([dataframe]): this df is build from the curva_consumo data indicated by the user
        prices ([dataframe]): this df is build from the historical prices or the

    Returns:
        df_final ([dataframe]): contains each one of the values divided by components
        dict_final ([dict]): contains the values to build the "desglose" of bill
    """
    inicio = datetime.fromisoformat(inputs["start_date"])
    fin = datetime.fromisoformat(inputs["end_date"]) + timedelta(hours=23)
    fechas_ree = ree_periods(inicio, fin)
    fechas_ree = fechas_ree.drop(columns=["year", "month", "day", "hour", "string"])

    comp_fija = termino_potencia(
        fechas_ree,
        inputs["tarifa"],
        inputs["potencias"],
        inputs["peajes_potencia"],
        inputs["cargos_potencia"],
        inputs["margen_potencia"],
    )

    fijo = []
    for index, row in comp_fija.iterrows():
        base_list = [
            row["Periodos"],
            row["PC"],
            row["peajes_Potencia"],
            row["cargos_Potencia"],
            row["Margen"],
            row["K.dias"],
            row["T_Fijo"],
        ]
        fijo.append(base_list)

    comp_variable = termino_energia(
        fechas_ree,
        inputs["tarifa"],
        inputs["peajes_energia"],
        inputs["cargos_energia"],
        curva_consumo,
        prices,
    )

    variable = []
    for index, row in comp_variable.iterrows():
        base_list = [
            f"P{index}",
            row["Consumo"],
            row["peajes_Energia"],
            row["cargos_Energia"],
            row["PrecioEnergia"],
            row["T_Variable"],
        ]
        variable.append(base_list)

    df_final, componentes = precio_final(
        comp_fija,
        comp_variable,
        inputs["imp_electrico"],
        inputs["alquiler_contador"],
        inputs["iva"],
    )

    subt_fijo, subt_variable, subt_impElec, subt_contador, subt_iva, total = componentes

    dict_final = {
        "Termino_Fijo": fijo,
        "Subt_Fijo": subt_fijo,
        "Termino_Variable": variable,
        "Subt_Variable": subt_variable,
        "IEE": subt_impElec,
        "Contador": subt_contador,
        "IVA": subt_iva,
        "Total": total,
    }

    return df_final, dict_final


if __name__ == "__main__":
    pass
