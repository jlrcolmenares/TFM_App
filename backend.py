"""
Here is where all the data treatment function are located. The idea is to fill to use the data and take in 
"""
from numpy import generic
import pandas as pd
from datetime import datetime
import json

def load_data():
    """
    This function load data from the given source. At the start, we 
    are going to work with json files. In following version I want to 
    return the data from ESIOS api (or personal API):
    """

# %%  1) Process "Power Generation" Data
    generation = pd.read_json("./data/power_generation/export_GeneraciónProgramada +ConsumoBombeo +CableBalearesP48_2021-08-23_19_15.json", encoding = 'utf-8', dtype = {'datetime': 'str'})
    generation['datetime'] = generation['datetime'].str.replace("+01:00", "", regex = False)
    generation['datetime'] = generation['datetime'].str.replace("+02:00", "", regex = False)
    generation.replace({
        "Generación programada + Consumo bombeo + Cable Baleares P48" : "Total",
        "Generación programada P48 Biogás" : "Biogás",
        "Generación programada P48 Biomasa" : "Biomasa",
        "Generación programada P48 Ciclo combinado" : "Ciclo combinado",
        "Generación programada P48 Consumo bombeo" : "Consumo bombeo",
        "Generación programada P48 Derivados del petróleo ó carbón" : "Derivados del petróleo ó carbón",
        "Generación programada P48 Energía residual" : "Energía residual",
        "Generación programada P48 Enlace Baleares" : "Enlace Baleares",
        "Generación programada P48 Eólica terrestre" : "Eólica terrestre",
        "Generación programada P48 Gas Natural Cogeneración" : "Cogeneración",
        "Generación programada P48 Hidráulica UGH" : "Hidráulica UGH",
        "Generación programada P48 Hidráulica no UGH" : "Hidráulica no UGH",
        "Generación programada P48 Hulla antracita" : "Hulla antracita",
        "Generación programada P48 Hulla sub-bituminosa" : "Hulla sub-bituminosa",
        "Generación programada P48 Nuclear" : "Nuclear",
        "Generación programada P48 Océano y geotérmica" : "Océano y geotérmica",
        "Generación programada P48 Residuos domésticos y similares" : "Residuos domésticos y similares",
        "Generación programada P48 Residuos varios" : "Residuos varios", 
        "Generación programada P48 Solar fotovoltaica" : "Solar fotovoltáica",
        "Generación programada P48 Solar térmica" : "Solar térmica",
        "Generación programada P48 Subproductos minería" : "Subproductos minería",
        "Generación programada P48 Turbinación bombeo" : "Turbinación bombeo", # Hidroeléctrica reversible
        "Demanda programada P48 Corrección eólica" : "Corrección eólica",
        "Demanda programada P48 Corrección solar" : "Corrección eólica",}, inplace =True )
    
    generation['datetime'] = pd.to_datetime(generation['datetime'])
    generation = generation.pivot_table( values='value', columns='name', index='datetime', fill_value=0 )


# %% 2) Process "Energy Prices" data
    prices = pd.read_json("./data/pvpc_prices/export_PrecioMedioHorarioFinalSumaDeComponentes_2021-08-23_19_18.json", encoding = 'utf-8', dtype = {'datetime': 'str'})
    prices['datetime'] = prices['datetime'].str.replace("+01:00", "", regex = False)
    prices['datetime'] = prices['datetime'].str.replace("+02:00", "", regex = False)
    prices.replace({
        "Precio medio horario componente banda secundaria " : "Banda Secundaria",
        "Precio medio horario componente control factor potencia " : " Control Factor Potencia",
        "Precio medio horario componente desvíos medidos " : " Desvíos Medidos",
        "Precio medio horario componente fallo nominación UPG " : " Fallo Nominación UPG",
        "Precio medio horario componente incumplimiento energía de balance " : " Incumplimiento Energía de Balance",
        "Precio medio horario componente mercado diario " : " Mercado Diario",
        "Precio medio horario componente mercado intradiario " : " Mercado Intradiario",
        "Precio medio horario componente pago de capacidad " : " Pago de Capacidad",
        "Precio medio horario componente reserva de potencia adicional a subir " : "Reserva de Potencia adicional a subir",
        "Precio medio horario componente restricciones PBF " : " Restricciones PBF",
        "Precio medio horario componente restricciones intradiario " : " Restricciones Intradiario",
        "Precio medio horario componente restricciones tiempo real " : " Restricciones tiempo real",
        "Precio medio horario componente saldo P.O.14.6 " : " Saldo P.O.14.6'",
        "Precio medio horario componente saldo de desvíos " : " Saldo de Desvíos",
        "Precio medio horario componente servicio de interrumpibilidad " : " Servicio de Interrumpibilidad",
        "Precio medio horario final suma de componentes" : "Suma Componentes Precio",}, inplace =True )
    
    prices['datetime'] = pd.to_datetime(prices['datetime'])
    prices = prices.pivot_table( values='value', columns='name', index='datetime', fill_value=0 )

# %% 3) Process "Profile consuptions" data
    consumption_profiles = pd.read_csv("./data/consumption_curves/perfiles_homemade.csv", sep = ';')
    consumption_profiles['HORA'] = consumption_profiles['HORA'] - 1
    selection =  consumption_profiles[['AÑO','MES', 'DIA', 'HORA']]
    selection = selection.rename( columns = {
        'AÑO':'year',
        'MES':'month',
        'DIA':'day',
        'HORA':'hour'
    })
    consumption_profiles['FECHA'] = pd.to_datetime(selection) # .dt.tz_localize("UTC").dt.tz_convert("Europe/Madrid")
    consumption_profiles = consumption_profiles[['FECHA','VERANO(1)/INVIERNO(0)', 'COEF. PERFIL P2.0TD', 'COEF. PERFIL P3.0TD' ]]
    consumption_profiles = consumption_profiles.set_index('FECHA')

# %% 4) Process "CO2 right" data
    pollution_taxes = pd.read_csv("./data/other_markets/historico-precios-CO2-_2021_.csv", sep = ";")
    pollution_taxes['Fecha'] = pd.to_datetime( pollution_taxes['Fecha'], dayfirst = True) # .dt.tz_localize("UTC").dt.tz_convert("Europe/Madrid")
    pollution_taxes = pollution_taxes.set_index("Fecha")
    pollution_taxes = pollution_taxes[["EUA"]]
    pollution_taxes = pollution_taxes.resample('1H').ffill() # to have hourly data
    

# %% 
    # pd.concat([generation, prices, consumption_profiles, consumption_profiles, pollution_taxes], axis= 1, join='inner')
    return generation, prices, consumption_profiles, pollution_taxes

def generation_between_date( start_date, end_date):
    """
    Datepicker-Range de Dash returns a date_string 
    in ISO format like this one "YYYY-MM-DD", so the
    input for this function must be like that
    """
    try:
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)

        
    except Exception as exc:
        print(exc)



if __name__ == '__main__':
    load_data()