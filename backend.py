"""
Here is where all the data treatment function are located. The idea is to fill to use the data and take in 
"""
# %%
#  Python Utils

from datetime import datetime
import plotly.express as px
import pandas as pd
import timeit

# Function Utils
from ree_dates import ree_periods


def load_local_data():
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

    df_aux = pd.concat(
        [
            generation,
            prices,
            consumption_profiles,
            consumption_profiles,
            pollution_taxes,
        ],
        axis=1,
        join="inner",
    )
    min_date = df_aux.index.min().to_pydatetime()
    max_date = df_aux.index.max().to_pydatetime()

    return min_date, max_date, generation, prices, consumption_profiles, pollution_taxes


def build_consumptions_df(
    df_ree, tarifa, normalized_consumption, potencias_contratadas
    ):
    """
    The function take the hired potencies indicated by the user and build a consumptions curve
    taking into account the consumptions profiles the REE publish every year, and month to month

    [Disclaimer]: I'm assuming that the user power consumption is directly related with the
    hired potence. We could have another function that takes a consumption files hour per hour.
    """

    if tarifa == "2.0TD":
        # For 2.0TD
        df_aux = pd.concat(
            [normalized_consumption["COEF. PERFIL P2.0TD"], df_ree["20TD_periods"]],
            axis=1,
            join="inner",
        )

        df_aux["PC"] = 10  # default values to create the column
        df_aux["Curva_Consumo"] = 0.1  # default values to create the column

        df_aux.loc[df_ree["20TD_periods"] == 1, "PC"] = potencias_contratadas[tarifa][
            "P1"
        ]
        df_aux.loc[df_ree["20TD_periods"] == 2, "PC"] = potencias_contratadas[tarifa][
            "P1"
        ]
        df_aux.loc[df_ree["20TD_periods"] == 3, "PC"] = potencias_contratadas[tarifa][
            "P2"
        ]

        df_aux["Curva_Consumo"] = df_aux["COEF. PERFIL P2.0TD"] * df_aux["PC"]  # KWh

        df_aux = df_aux.drop(columns=["COEF. PERFIL P2.0TD"])

    elif tarifa == "3.0TD":
        # For 3.0TD
        df_aux = pd.concat(
            [normalized_consumption["COEF. PERFIL P3.0TD"], df_ree["30TD_periods"]],
            axis=1,
            join="inner",
        )

        df_aux["PC"] = 10
        df_aux["Curva_Consumo"] = 0.1

        df_aux.loc[df_ree["30TD_periods"] == 1, "PC"] = potencias_contratadas[tarifa][
            "P1"
        ]
        df_aux.loc[df_ree["30TD_periods"] == 2, "PC"] = potencias_contratadas[tarifa][
            "P2"
        ]
        df_aux.loc[df_ree["30TD_periods"] == 3, "PC"] = potencias_contratadas[tarifa][
            "P3"
        ]
        df_aux.loc[df_ree["30TD_periods"] == 4, "PC"] = potencias_contratadas[tarifa][
            "P4"
        ]
        df_aux.loc[df_ree["30TD_periods"] == 5, "PC"] = potencias_contratadas[tarifa][
            "P5"
        ]
        df_aux.loc[df_ree["30TD_periods"] == 6, "PC"] = potencias_contratadas[tarifa][
            "P6"
        ]

        df_aux["Curva_Consumo"] = df_aux["COEF. PERFIL P3.0TD"] * df_aux["PC"]  # KWh

        df_aux = df_aux.drop(columns=["COEF. PERFIL P3.0TD"])

    elif tarifa == "6.1TD":
        # For 6.1TD
        pass

    return df_aux


def build_peajesYcargos_df(df_ree, tarifa, peajes_potencia, peajes_energia):
    """
    This funcion take the regulatory payments indicated by State and Goverment agencies and
    build a dataframe that have the hourly regulatory payments.

    [Disclaimer]: Each  hour of the day have different payments. The results of this fact is that
    depending on the hour the electricity consumptions in going to be more or less expensive.
    """
    if tarifa == "2.0TD":
        # For 2.0TD
        df_aux2 = df_ree.loc[:, ["feriado_finde", "20TD_periods"]]

        df_aux2["peajes_Potencia"] = 0.1  # default values to create the column
        df_aux2["peajes_Energia"] = 0.1  # default values to create the column

        df_aux2.loc[df_aux2["20TD_periods"] == 1, "peajes_Potencia"] = (
            peajes_potencia[tarifa]["P1"] / (365 * 24) / 2
        )  # I divide by half because the other half is part of Period2
        df_aux2.loc[df_aux2["20TD_periods"] == 2, "peajes_Potencia"] = (
            peajes_potencia[tarifa]["P1"] / (365 * 24) / 2
        )  # I divide by half because the other half is part of Period1
        df_aux2.loc[df_aux2["20TD_periods"] == 3, "peajes_Potencia"] = peajes_potencia[
            tarifa
        ]["P2"] / (365 * 24)

        df_aux2.loc[df_aux2["20TD_periods"] == 1, "peajes_Energia"] = peajes_energia[
            tarifa
        ]["P1"]
        df_aux2.loc[df_aux2["20TD_periods"] == 2, "peajes_Energia"] = peajes_energia[
            tarifa
        ]["P2"]
        df_aux2.loc[df_aux2["20TD_periods"] == 3, "peajes_Energia"] = peajes_energia[
            tarifa
        ]["P3"]

    elif tarifa == "3.0TD":
        # For 3.0TD
        df_aux2 = df_ree.loc[:, ["feriado_finde", "30TD_periods"]]

        df_aux2["peajes_Potencia"] = 0.1  # default values to create the column
        df_aux2["peajes_Energia"] = 0.1  # default values to create the column

        df_aux2.loc[df_aux2["30TD_periods"] == 1, "peajes_Potencia"] = peajes_potencia[
            tarifa
        ]["P1"] / (365 * 24)
        df_aux2.loc[df_aux2["30TD_periods"] == 2, "peajes_Potencia"] = peajes_potencia[
            tarifa
        ]["P2"] / (365 * 24)
        df_aux2.loc[df_aux2["30TD_periods"] == 3, "peajes_Potencia"] = peajes_potencia[
            tarifa
        ]["P3"] / (365 * 24)
        df_aux2.loc[df_aux2["30TD_periods"] == 4, "peajes_Potencia"] = peajes_potencia[
            tarifa
        ]["P4"] / (365 * 24)
        df_aux2.loc[df_aux2["30TD_periods"] == 5, "peajes_Potencia"] = peajes_potencia[
            tarifa
        ]["P5"] / (365 * 24)
        df_aux2.loc[df_aux2["30TD_periods"] == 6, "peajes_Potencia"] = peajes_potencia[
            tarifa
        ]["P6"] / (365 * 24)

        df_aux2.loc[df_aux2["30TD_periods"] == 1, "peajes_Energia"] = peajes_energia[
            tarifa
        ]["P1"]
        df_aux2.loc[df_aux2["30TD_periods"] == 2, "peajes_Energia"] = peajes_energia[
            tarifa
        ]["P2"]
        df_aux2.loc[df_aux2["30TD_periods"] == 3, "peajes_Energia"] = peajes_energia[
            tarifa
        ]["P3"]
        df_aux2.loc[df_aux2["30TD_periods"] == 4, "peajes_Energia"] = peajes_energia[
            tarifa
        ]["P4"]
        df_aux2.loc[df_aux2["30TD_periods"] == 5, "peajes_Energia"] = peajes_energia[
            tarifa
        ]["P5"]
        df_aux2.loc[df_aux2["30TD_periods"] == 6, "peajes_Energia"] = peajes_energia[
            tarifa
        ]["P6"]

    elif tarifa == "6.1TD":
        # For 6.1TD
        df_aux2 = df_ree.loc[:, ["feriado_finde", "61TD_periods"]]

        df_aux2["peajes_Potencia"] = 0.1  # default values to create the column
        df_aux2["peajes_Energia"] = 0.1  # default values to create the column

        df_aux2.loc[df_aux2["61TD_periods"] == 1, "peajes_Potencia"] = peajes_potencia[
            tarifa
        ]["P1"] / (365 * 24)
        df_aux2.loc[df_aux2["61TD_periods"] == 2, "peajes_Potencia"] = peajes_potencia[
            tarifa
        ]["P2"] / (365 * 24)
        df_aux2.loc[df_aux2["61TD_periods"] == 3, "peajes_Potencia"] = peajes_potencia[
            tarifa
        ]["P3"] / (365 * 24)
        df_aux2.loc[df_aux2["61TD_periods"] == 4, "peajes_Potencia"] = peajes_potencia[
            tarifa
        ]["P4"] / (365 * 24)
        df_aux2.loc[df_aux2["61TD_periods"] == 5, "peajes_Potencia"] = peajes_potencia[
            tarifa
        ]["P5"] / (365 * 24)
        df_aux2.loc[df_aux2["61TD_periods"] == 6, "peajes_Potencia"] = peajes_potencia[
            tarifa
        ]["P6"] / (365 * 24)

        df_aux2.loc[df_aux2["61TD_periods"] == 1, "peajes_Energia"] = peajes_energia[
            tarifa
        ]["P1"]
        df_aux2.loc[df_aux2["61TD_periods"] == 2, "peajes_Energia"] = peajes_energia[
            tarifa
        ]["P2"]
        df_aux2.loc[df_aux2["61TD_periods"] == 3, "peajes_Energia"] = peajes_energia[
            tarifa
        ]["P3"]
        df_aux2.loc[df_aux2["61TD_periods"] == 4, "peajes_Energia"] = peajes_energia[
            tarifa
        ]["P4"]
        df_aux2.loc[df_aux2["61TD_periods"] == 5, "peajes_Energia"] = peajes_energia[
            tarifa
        ]["P5"]
        df_aux2.loc[df_aux2["61TD_periods"] == 6, "peajes_Energia"] = peajes_energia[
            tarifa
        ]["P6"]

    return df_aux2.iloc[:, -3:]


def build_terminos_df(df_consumo, df_peajes, df_prices, tarifa, margen_comer):
    """
    The function calculate the hourly fixed and variable components of the prices.
    Fixed component (availabily of power electricity) have a different calculation method that
    Variable component (power consumption itself).

    [Disclaimer]: I'm playing with the data to get fixed components. Everything is going to make sense
    in the at the end
    """

    df1 = df_peajes.loc[
        :, ["peajes_Potencia", "peajes_Energia"]
    ]  # drop 'periodos' columns
    df2 = df_consumo
    df3 = df_prices["Suma Componentes Precio"] * 0.001

    df_aux3 = pd.concat([df1, df2, df3], axis=1, join="inner")

    df_aux3["Margen"] = 0.001  # default values to create the column
    df_aux3["T_Fijo"] = 0.001  # default values to create the column
    df_aux3["T_Variable"] = 0.001  # default values to create the column

    # The variable component (termino variable) is calculated very easily with hourly division
    df_aux3["T_Variable"] = (df_aux3["Curva_Consumo"]) * (
        df_aux3["peajes_Energia"] + df_aux3["Suma Componentes Precio"]
    )

    # The fixed component (termino fijo) have a consideration and change between tariffs
    if tarifa == "2.0TD":
        df_aux3 = df_aux3.rename(columns={"20TD_periods": "Ptarif"})
        # El margen va en Eur/kW/año. Dividimos por (365*24) para obtener margen por hora
        df_aux3.loc[df_aux3["Ptarif"] == 1, "Margen"] = (
            margen_comer / (365 * 24) / 2
        )  # I divide by half because the other half is part of Period2
        df_aux3.loc[df_aux3["Ptarif"] == 2, "Margen"] = (
            margen_comer / (365 * 24) / 2
        )  # I divide by half because the other half is part of Period1
        df_aux3.loc[df_aux3["Ptarif"] == 3, "Margen"] = margen_comer / (365 * 24)

        df_aux3.loc[:, "P1C_Fijo"] = df_aux3.loc[df_aux3["Ptarif"] == 1, "PC"].mean()
        df_aux3.loc[:, "P2C_Fijo"] = df_aux3.loc[df_aux3["Ptarif"] == 3, "PC"].mean()

        df_aux3.loc[:, "Peajes_P1C"] = df_aux3.loc[
            df_aux3["Ptarif"] == 1, "peajes_Potencia"
        ].mean()
        df_aux3.loc[:, "Peajes_P2C"] = df_aux3.loc[
            df_aux3["Ptarif"] == 3, "peajes_Potencia"
        ].mean()

        # El termino fijo es distinto y toma encuenta que la potencia está disponible todas las horas
        df_aux3["T_Fijo"] = (
                (df_aux3["P1C_Fijo"] * 0.001) * (df_aux3["Peajes_P1C"] + df_aux3["Margen"]) * 2 + \
                (df_aux3["P2C_Fijo"] * 0.001) * (df_aux3["Peajes_P2C"] + df_aux3["Margen"])
        )
        # df_aux3 = df_aux3.drop( columns = ['P1C_Fijo', 'P2C_Fijo'])

    elif tarifa == "3.0TD":
        df_aux3 = df_aux3.rename(columns={"30TD_periods": "Ptarif"})
        # El margen va en Eur/kW/año. Dividimos por (365*24) para obtener margen por hora
        df_aux3["Margen"] = margen_comer / (365 * 24)

        df_aux3.loc[:, "P1C_Fijo"] = df_aux3.loc[df_aux3["Ptarif"] == 1, "PC"].mean()
        df_aux3.loc[:, "P2C_Fijo"] = df_aux3.loc[df_aux3["Ptarif"] == 2, "PC"].mean()
        df_aux3.loc[:, "P3C_Fijo"] = df_aux3.loc[df_aux3["Ptarif"] == 3, "PC"].mean()
        df_aux3.loc[:, "P4C_Fijo"] = df_aux3.loc[df_aux3["Ptarif"] == 4, "PC"].mean()
        df_aux3.loc[:, "P5C_Fijo"] = df_aux3.loc[df_aux3["Ptarif"] == 5, "PC"].mean()
        df_aux3.loc[:, "P6C_Fijo"] = df_aux3.loc[df_aux3["Ptarif"] == 6, "PC"].mean()
        # El termino fijo es distinto y toma encuenta que la potencia está disponible todas las horas
        df_aux3["T_Fijo"] = (
            (df_aux3["P1C_Fijo"] * 0.001) * (df_aux3["Peajes_P1C"] + df_aux3["Margen"]) + \
            (df_aux3["P2C_Fijo"] * 0.001) * (df_aux3["Peajes_P2C"] + df_aux3["Margen"]) + \
            (df_aux3["P3C_Fijo"] * 0.001) * (df_aux3["Peajes_P3C"] + df_aux3["Margen"]) + \
            (df_aux3["P4C_Fijo"] * 0.001) * (df_aux3["Peajes_P4C"] + df_aux3["Margen"]) + \
            (df_aux3["P5C_Fijo"] * 0.001) * (df_aux3["Peajes_P5C"] + df_aux3["Margen"]) + \
            (df_aux3["P6C_Fijo"] * 0.001) * (df_aux3["Peajes_P6C"] + df_aux3["Margen"])
        )
        # df_aux3 = df_aux3.drop( columns = ['P1C_Fijo', 'P2C_Fijo','P3C_Fijo', 'P4C_Fijo', 'P5C_Fijo', 'P6C_Fijo'])

    elif tarifa == "6.1TD":
        pass

    return df_aux3


def starting_backend(
    tarifa,
    potencias,
    peajes_potencia,
    peajes_energia,
    margen,
    alquileres,
    adicionales,
    impuestos,
    ):

    # Step 1: Load External Data
    (
        min_date,
        max_date,
        generation,
        prices,
        consumption_profiles,
        pollution_taxes,
    ) = load_local_data()

    # Step 2: Generate internal periods Data
    fechas_ree = ree_periods(min_date, max_date)
    fechas_ree = fechas_ree.drop(columns=["year", "month", "day", "hour", "string"])

    # Step 3: Build consumption curve
    df_consumo = build_consumptions_df(
        fechas_ree, tarifa, consumption_profiles, potencias
    )

    # Step 4: Load 'Cargos y peajes'. Esta variables pueden venir del frontend
    df_peajes = build_peajesYcargos_df(
        fechas_ree, tarifa, peajes_potencia, peajes_energia
    )

    # Step 5. Multiply to get hourly bill components or 'terminos' fijo y variables
    df_terminos_hora = build_terminos_df(df_consumo, df_peajes, prices, tarifa, margen)

    # Step 6: Calculate Total Components'. Electrical Tax is applied to this one
    df_terminos_totales = df_terminos_hora.groupby("Ptarif").aggregate(
        {
            "Ptarif": "count",
            "peajes_Potencia": lambda x: x.mean() * 8760,
            "peajes_Energia": "mean",
            "PC": "mean",
            "Curva_Consumo": "sum",
            "Margen": "mean",
            "T_Fijo": "sum",
            "T_Variable": "sum",
        }
    )

    T_Fijo = df_terminos_totales["T_Fijo"].sum()
    T_Variable = df_terminos_totales["T_Variable"].sum()

    df_subtotal = df_terminos_hora.loc[:, ["Ptarif", "PC"]] 
    df_subtotal.loc[:, "TF"] = T_Fijo # Asi no
    df_subtotal.loc[:, "TV"] = T_Variable
    df_subtotal.loc[:, "IEE"] = (5.1127 / 100) * (df_subtotal["TF"].mean() + df_subtotal["TV"].mean())
    df_subtotal.loc[:, "Alquiler"] = alquileres / (365 * 24)  # 2 euros al año
    df_subtotal.loc[:, "SVA"] = adicionales / (365 * 24)
        
    # Calculamos el total
    df_total = df_subtotal.aggregate(
        {
            "Ptarif": "count",
            "TF": "mean",
            "TV": "mean",
            "IEE": "mean",
            "Alquiler": "sum",
            "SVA": "sum",
        }
    )
    
    iva = df_total[["TF", "TV", "IEE", "Alquiler"]].sum() * (
        impuestos["IVA"] / 100
    )  #  10%

    importe_factura = df_total[["TF", "TV", "IEE", "Alquiler"]].sum() + iva
    
    df_total.loc['IVA'] = iva
    df_total.loc['Suma'] = importe_factura
    
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
        importe_factura,
    )


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


def join_all_data(
       generation,
       prices,
       pollution_taxes,
       df_terminos_hora,
       df_total,
    ):
    """
    This function was develop to simplify and adapt the flux of information 
    between the app
    """
    df_all = pd.concat(
        [
            df_terminos_hora,
            generation,
            prices.drop( columns = 'Suma Componentes Precio', inplace = True),
            pollution_taxes,
        ], axis =1, join='inner')

    for index,value in pd.DataFrame(df_total[1:]).iterrows():
        df_all.loc[: , index] = value[0]
    
    # termino_hora = df_all.iloc[:, 0:9]
    # generation = df_all .iloc[:, 13:36]
    # precio = df_all.iloc[: , 36:51]
    # pollution = df_all.iloc[:, 51:53]
    # totales = df_all.iloc[53:]
    return df_all 


if __name__ == "__main__":

    # Variables de entrada
    tarifa = "2.0TD"
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

    start_time = timeit.timeit()
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
        tarifa,
        potencias_contratadas,  # potencias_contratadas
        peajesYcargos_potencia_boe,  # peajesYcargos_potencia_boe
        peajesYcargos_energia_boe,  # peajesYcargos_energia_boe
        margen,
        alquileres,
        adicionales,
        impuestos,
    )
    end_time = timeit.timeit()
    print("Listo: ", start_time - end_time)

    df_all = join_all_data(
        generation,
        prices,
        pollution_taxes,
        df_terminos_hora,
        df_total,
    )
    
    #
    df_graph, df_tidy, df_tidy2 = get_tidy_df(df_all)


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
    #     path=[px.Constant("Periodos"), "Ptarif", "type", "variable"],
    #     values="value",
    # )
    # fig.show()
    # Este no muestra lo que quiero. Que es el aporte de cada uno por hora

    fig2 = px.bar(df_tidy2, x=df_tidy2.index, y="value", color="variable")
    fig2.show()
    # A esta figura le falta indicar el aporte porcentual de cada uno"""

# %%
