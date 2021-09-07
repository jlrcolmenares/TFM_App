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

        df_aux1["Consumo"] = df_aux1["COEF. PERFIL P2.0TD"] * df_aux1["PC"]*1000 # kWh
  
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

        df_aux1["Consumo"] = df_aux1["COEF. PERFIL P3.0TD"] * df_aux1["PC"] *1000# KWh

        df_aux1 = df_aux1.drop(columns=["COEF. PERFIL P3.0TD"])
        df_aux1 = df_aux1.rename( columns = { "30TD_periods":"Periodos" })

    elif tarifa == "6.1TD":
        # For 6.1TD
        pass

    return df_aux1


def termino_potencia(df_ree, tarifa, potences, peajes_potencia, cargos_potencia, margen):
    
    dias = len(df_ree.resample('1D').count())
    K = dias/356 # constante para adaptar el 
    
    if tarifa == '2.0TD':
        out_list = []
        for p in ['P1','P2']:
            out_list.append([
                p,
                potences[p],
                peajes_potencia[p],
                cargos_potencia[p],
                0,
                (dias/365),
                (potences[p] * (peajes_potencia[p] + cargos_potencia[p]) * (K))
            ])
        
        out_list.append([
            'Ppunta',
            potences['P1'],
            peajes_potencia[p],
            cargos_potencia[p],
            margen,
            (dias/365),
            (potences['P1'] * (margen) * (K))      
        ])
        
    elif tarifa == '3.0TD':
        out_list = []
        for p in ['P1','P2','P3','P4','P5','P6']:
            out_list.append([
                p,
                potences[p],
                peajes_potencia[p],
                cargos_potencia[p],
                0,
                (dias/365),
                (potences[p] * (peajes_potencia[p] + cargos_potencia[p]) * (K))
            ])
        
        out_list.append([
            'Ppunta',
            potences['P1'],
            0,
            0,
            margen,
            (dias/365),
            (potences['P1'] * (margen) * (K))      
        ])
        
    elif tarifa == '6.1TD':
        pass
    
    df = pd.DataFrame(out_list , columns = [ 'Periodos', 'PC', 'peajes_Potencia', 'cargos_Potencia', 'Margen', 'K.dias', 'T_Fijo'])
    return df 


def termino_energia(df_ree, tarifa, peajes_energia, cargos_energia, curva_consumo, prices):
    """
    This funcion take the regulatory payments indicated by State and Goverment agencies and
    build a dataframe that have the hourly regulatory payments.

    [Disclaimer]: Each  hour of the day have different payments. The results of this fact is that
    depending on the hour the electricity consumptions in going to be more or less expensive.
    """
 
    if tarifa == "2.0TD":
        # For 2.0TD
        df_aux = df_ree.loc[:, ["feriado_finde", "20TD_periods"]]
        for p in ['P1','P2','P3']:
            df_aux.loc[df_aux["20TD_periods"] == int(p[-1]) , "peajes_Energia"] = peajes_energia[p]
            df_aux.loc[df_aux["20TD_periods"] == int(p[-1]) , "cargos_Energia"] = cargos_energia[p]
    
    elif tarifa == "3.0TD":
        # For 3.0TD
        df_aux = df_ree.loc[:, ["feriado_finde", "30TD_periods"]]
        for p in ['P1','P2','P3','P4','P5','P6']:
            df_aux.loc[df_aux["30TD_periods"] == int(p[-1]) , "peajes_Energia"] = peajes_energia[p]
            df_aux.loc[df_aux["30TD_periods"] == int(p[-1]) , "cargos_Energia"] = cargos_energia[p]
    
    elif tarifa == "6.1TD":
        # For 6.1TD
        pass
    
    peajesYcargos = df_aux.iloc[:, -2:]

    df_aux2 = pd.concat([
        curva_consumo.drop( columns= ['weekday']),
        peajesYcargos,
        prices["Suma Componentes Precio"].rename("PrecioEnergia")*0.001
        ], axis=1, join="inner")
    
    df_aux2["T_Variable"] = 0.001  # default values to create the column
    # The variable component (termino variable) is calculated easily with hourly division
    df_aux2["T_Variable"] = (df_aux2["Consumo"]) * ( df_aux2["peajes_Energia"] + df_aux2["cargos_Energia"] + df_aux2["PrecioEnergia"] )
    
    df_aux3 = df_aux2.groupby('Periodos').aggregate(
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


def precio_final( termino_potencia, termino_energia, imp_electrico, contador, iva):
    """
    The functions add the rest of the valuus of the selectors to calculate the final price
    """
    
    subt_fijo = termino_potencia['T_Fijo'].sum()
    subt_variable = termino_energia['T_Variable'].sum()
    subt_impElec = ( subt_fijo + subt_variable )*( imp_electrico / 100)
    subt_contador = contador * termino_potencia['K.dias'].values[0]
    subt_iva = (subt_fijo+subt_variable+subt_impElec+subt_contador)*( iva /100)
    total = subt_fijo+subt_variable+subt_impElec+subt_contador+subt_iva
    
    serie = termino_energia.sum()
    out1 = ['Peajes', serie['peajes_Energia']]
    out2 =['Cargos', serie['cargos_Energia']]
    out3 = ['Consumo', serie['T_Variable'] - serie['peajes_Energia'] - serie['cargos_Energia']]
    
    out4, out5, out6 = 0, 0 ,0
    for index,row in termino_potencia.iterrows():
        out4 = out4 + row['PC']*row['peajes_Potencia']*row['K.dias']
        out5 = out5 + row['PC']*row['cargos_Potencia']*row['K.dias'] 
        out6 = out6 + row['PC']*row['Margen']*row['K.dias'] 

    out4 = ['Peajes', out4 ]
    out5 = ['Cargos', out5 ]
    out6 = ['Margen', out6 ]

    out7 = ['Contador', subt_contador]
    out8 = ['Impuestos', subt_impElec]
    out9 = ['Impuestos',subt_iva]
    
    out_list = [out1, out2, out3, out4, out5, out6, out7, out8, out9]
    
    df_out = pd.DataFrame(out_list, columns = ['Concepto', 'Euros'])
    return df_out


def temporal_df( inputs, generation, prices, profiles, taxes):
    """
    This is the function
    """
    inicio = datetime.fromisoformat(inputs['start_date'] )
    fin = datetime.fromisoformat(inputs['end_date'] ) + timedelta(hours=23)
    fechas_ree = ree_periods( inicio , fin )
    fechas_ree = fechas_ree.drop(columns=["year", "month", "day", "hour", "string"])
    # Paso 1: Crear curva de consumo
    curva_consumo = build_consumptions_df(
        fechas_ree, 
        inputs['tarifa'],
        profiles[ inputs['start_date'] : inputs['end_date'] ],
        inputs['potencias']
    )
    
    generation = generation[ inputs['start_date'] : inputs['end_date']]
    prices = prices[ inputs['start_date'] : inputs['end_date']]
    profiles = profiles[ inputs['start_date'] : inputs['end_date']]
    taxes = taxes[ inputs['start_date'] : inputs['end_date']]


    # curva_consumo = salida.iloc[:,0:4]
    # prices = salida.iloc[:,4:20]
    # generation = salida.iloc[:, 20:43]
    # taxes = salida.iloc[:, 43,44]
    
    return pd.concat( [curva_consumo,prices,generation,taxes], axis = 1)


def total_df( inputs, curva_consumo, prices):
    """
     This function calculate the final prices
    
    """
    inicio = datetime.fromisoformat(inputs['start_date'] )
    fin = datetime.fromisoformat(inputs['end_date'] ) + timedelta(hours=23)
    fechas_ree = ree_periods( inicio , fin )
    fechas_ree = fechas_ree.drop(columns=["year", "month", "day", "hour", "string"])

    comp_fija = termino_potencia(
        fechas_ree,
        inputs['tarifa'], 
        inputs['potencias'], 
        inputs['peajes_potencia'], 
        inputs['cargos_potencia'],
        inputs['margen_potencia']
    )
    
    comp_variable = termino_energia(
        fechas_ree,
        inputs['tarifa'],  
        inputs['peajes_energia'], 
        inputs['cargos_energia'],
        curva_consumo,
        prices
    )

    df_final = precio_final(
        comp_fija,
        comp_variable,
        inputs['imp_electrico'],
        inputs['alquiler_contador'],
        inputs['iva'],
    )

    return df_final

 
if __name__ == "__main__":
    pass

