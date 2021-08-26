"""
Here is where all the data treatment function are located. The idea is to fill to use the data and take in 
"""
# %%  
#  Python Utils
from datetime import datetime
import pandas as pd

# Function Utils
from ree_dates import ree_periods


def load_local_data():
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
    consumption_profiles = pd.read_csv("./data/consumption_curves/perfiles_homemade.csv", sep = ';', decimal = ',')
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
    
    df_aux = pd.concat([generation, prices, consumption_profiles, consumption_profiles, pollution_taxes], axis= 1, join='inner')
    min_date = df_aux.index.min().to_pydatetime()
    max_date = df_aux.index.max().to_pydatetime()

    return min_date, max_date, generation, prices, consumption_profiles, pollution_taxes


def build_peajes_df( df_ree, tarifa, peajes_potencia, peajes_energia):
    """
    
    """
    if tarifa == '2.0TD':
        # For 2.0TD
        df_aux = df_ree.loc[: , ['feriado_finde', '20TD_periods']]
        
        df_aux['peajes_Potencia'] = 0.1
        df_aux['peajes_Energia'] = 0.1
        

        df_aux.loc[df_aux['20TD_periods'] == 1, 'peajes_Potencia' ] = peajes_potencia[tarifa]['P1']/(365*24)
        df_aux.loc[df_aux['20TD_periods'] == 2, 'peajes_Potencia' ] = peajes_potencia[tarifa]['P1']/(365*24)
        df_aux.loc[df_aux['20TD_periods'] == 3, 'peajes_Potencia' ] = peajes_potencia[tarifa]['P2']/(365*24)

        df_aux.loc[df_aux['20TD_periods'] == 1, 'peajes_Energia' ] = peajes_energia[tarifa]['P1']
        df_aux.loc[df_aux['20TD_periods'] == 2, 'peajes_Energia' ] = peajes_energia[tarifa]['P2']
        df_aux.loc[df_aux['20TD_periods'] == 3, 'peajes_Energia' ] = peajes_energia[tarifa]['P3']
    
    elif tarifa == '3.0TD':
        # For 3.0TD
        df_aux = df_ree.loc[: , ['feriado_finde', '30TD_periods']]

        df_aux['peajes_Potencia'] = 0.1
        df_aux['peajes_Energia'] = 0.1
        
        df_aux.loc[df_aux['30TD_periods'] == 1, 'peajes_Potencia' ] = peajes_potencia[tarifa]['P1']/(365*24)
        df_aux.loc[df_aux['30TD_periods'] == 2, 'peajes_Potencia' ] = peajes_potencia[tarifa]['P2']/(365*24)
        df_aux.loc[df_aux['30TD_periods'] == 3, 'peajes_Potencia' ] = peajes_potencia[tarifa]['P3']/(365*24)
        df_aux.loc[df_aux['30TD_periods'] == 4, 'peajes_Potencia' ] = peajes_potencia[tarifa]['P4']/(365*24)
        df_aux.loc[df_aux['30TD_periods'] == 5, 'peajes_Potencia' ] = peajes_potencia[tarifa]['P5']/(365*24)
        df_aux.loc[df_aux['30TD_periods'] == 6, 'peajes_Potencia' ] = peajes_potencia[tarifa]['P6']/(365*24)

        df_aux.loc[df_aux['30TD_periods'] == 1, 'peajes_Energia' ] = peajes_energia[tarifa]['P1']
        df_aux.loc[df_aux['30TD_periods'] == 2, 'peajes_Energia' ] = peajes_energia[tarifa]['P2']
        df_aux.loc[df_aux['30TD_periods'] == 3, 'peajes_Energia' ] = peajes_energia[tarifa]['P3']
        df_aux.loc[df_aux['30TD_periods'] == 4, 'peajes_Energia' ] = peajes_energia[tarifa]['P4']
        df_aux.loc[df_aux['30TD_periods'] == 5, 'peajes_Energia' ] = peajes_energia[tarifa]['P5']
        df_aux.loc[df_aux['30TD_periods'] == 6, 'peajes_Energia' ] = peajes_energia[tarifa]['P6']

    elif tarifa == '6.1TD':
        # For 6.1TD
        df_aux = df_ree.loc[: , ['feriado_finde', '61TD_periods']]
    
        df_aux['peajes_Potencia'] = 0.1
        df_aux['peajes_Energia'] = 0.1

        df_aux.loc[df_aux['61TD_periods'] == 1, 'peajes_Potencia' ] = peajes_potencia[tarifa]['P1']/(365*24)
        df_aux.loc[df_aux['61TD_periods'] == 2, 'peajes_Potencia' ] = peajes_potencia[tarifa]['P2']/(365*24)
        df_aux.loc[df_aux['61TD_periods'] == 3, 'peajes_Potencia' ] = peajes_potencia[tarifa]['P3']/(365*24)
        df_aux.loc[df_aux['61TD_periods'] == 4, 'peajes_Potencia' ] = peajes_potencia[tarifa]['P4']/(365*24)
        df_aux.loc[df_aux['61TD_periods'] == 5, 'peajes_Potencia' ] = peajes_potencia[tarifa]['P5']/(365*24)
        df_aux.loc[df_aux['61TD_periods'] == 6, 'peajes_Potencia' ] = peajes_potencia[tarifa]['P6']/(365*24)

        df_aux.loc[df_aux['61TD_periods'] == 1, 'peajes_Energia' ] = peajes_energia[tarifa]['P1']
        df_aux.loc[df_aux['61TD_periods'] == 2, 'peajes_Energia' ] = peajes_energia[tarifa]['P2']
        df_aux.loc[df_aux['61TD_periods'] == 3, 'peajes_Energia' ] = peajes_energia[tarifa]['P3']
        df_aux.loc[df_aux['61TD_periods'] == 4, 'peajes_Energia' ] = peajes_energia[tarifa]['P4']
        df_aux.loc[df_aux['61TD_periods'] == 5, 'peajes_Energia' ] = peajes_energia[tarifa]['P5']
        df_aux.loc[df_aux['61TD_periods'] == 6, 'peajes_Energia' ] = peajes_energia[tarifa]['P6']
    
    return df_aux.iloc[:, -3:]


def build_consumptions_df( df_ree, tarifa, normalized_consumption, potencias_contratadas ):
    """
    """

    if tarifa == '2.0TD':
        # For 2.0TD
        df_aux2 = pd.concat( [ normalized_consumption['COEF. PERFIL P2.0TD'], df_ree['20TD_periods'] ], axis = 1, join = 'inner')
        
        df_aux2['PC'] = 10
        df_aux2['Curva_Consumo']= 0.1

        df_aux2.loc[df_ree['20TD_periods'] == 1, 'PC' ] = potencias_contratadas[tarifa]['P1']
        df_aux2.loc[df_ree['20TD_periods'] == 2, 'PC' ] = potencias_contratadas[tarifa]['P1']
        df_aux2.loc[df_ree['20TD_periods'] == 3, 'PC' ] = potencias_contratadas[tarifa]['P2']

        df_aux2['Curva_Consumo'] = df_aux2['COEF. PERFIL P2.0TD']*df_aux2['PC'] # KWh

        df_aux2 = df_aux2.drop( columns = ['COEF. PERFIL P2.0TD'] )

    elif tarifa == '3.0TD':
        # For 3.0TD
        df_aux2 = pd.concat( [ normalized_consumption['COEF. PERFIL P3.0TD'], df_ree['30TD_periods'] ], axis = 1, join = 'inner')
        
        df_aux2['PC'] = 10
        df_aux2['Curva_Consumo']= 0.1

        df_aux2.loc[df_ree['30TD_periods'] == 1, 'PC' ] = potencias_contratadas[tarifa]['P1']
        df_aux2.loc[df_ree['30TD_periods'] == 2, 'PC' ] = potencias_contratadas[tarifa]['P2']
        df_aux2.loc[df_ree['30TD_periods'] == 3, 'PC' ] = potencias_contratadas[tarifa]['P3']
        df_aux2.loc[df_ree['30TD_periods'] == 4, 'PC' ] = potencias_contratadas[tarifa]['P4']
        df_aux2.loc[df_ree['30TD_periods'] == 5, 'PC' ] = potencias_contratadas[tarifa]['P5']
        df_aux2.loc[df_ree['30TD_periods'] == 6, 'PC' ] = potencias_contratadas[tarifa]['P6']


        df_aux2['Curva_Consumo'] = df_aux2['COEF. PERFIL P3.0TD']*df_aux2['PC'] # KWh

        df_aux2 = df_aux2.drop( columns = ['COEF. PERFIL P3.0TD'] )


    elif tarifa == '6.1TD':
        # For 6.1TD
        pass

    return df_aux2


def build_terminos_df( df_consumo, df_peajes, df_prices, tarifa, margen_comer):
    """
    It build the dataframe we need to calculate the final price
    """

    df1 = df_peajes.loc[:, ['peajes_Potencia', 'peajes_Energia']] # drop 'periodos' columns
    df2 = df_consumo
    df3 = df_prices['Suma Componentes Precio']*0.001
    
    df_factores = pd.concat( [df1, df2, df3] , axis =1, join = 'inner' )
    df_factores['Margen'] = margen_comer/(365*24) #
    
    df_factores['T_Fijo'] = 0.001
    df_factores['T_Variable'] = 0.001
    
    df_factores['T_Fijo'] = (df_factores['PC']*0.001)*(df_factores['peajes_Potencia'] + df_factores['Margen']) # *len(df_consumo)
    df_factores['T_Variable'] = (df_factores['Curva_Consumo'])*(df_factores['peajes_Energia']+df_factores['Suma Componentes Precio'])

    if tarifa == '2.0TD':  
        df_factores = df_factores.rename( columns = { '20TD_periods': 'Ptarif' } )
    
    elif tarifa == '3.0TD':
        df_factores = df_factores.rename( columns = { '30TD_periods': 'Ptarif' } )  

    elif tarifa == '6.1TD':
        pass

    return df_factores



def generation_between_date( start_date, end_date):
    """
    Datepicker-Range de Dash returns a date_string 
    in ISO format like this one "YYYY-MM-DD", so the
    input for this function must be like that
    """
    pass


if __name__ == '__main__':
    # Step 1: Load External Data
    min_date, max_date, generation, prices, consumption_profiles, pollution_taxes = load_local_data()
    
    # Step 2: Generate internal Data
    fechas_ree = ree_periods( min_date, max_date)
    fechas_ree = fechas_ree.drop( columns = ['year', 'month', 'day', 'hour', 'string'])

    # Step 3: Select Tarifa from app
    tarifa = '2.0TD'

    # Step 4: Load contracted potencies from app
    potencias_contratadas = {
        '2.0TD': { # kW
            'P1': 5100, # P. Punta = P1P
            'P2': 3450, # P. Punta = P2P
            'P3': 0, # P. Valle = P3P
            'P4': 0,
            'P5': 0,
            'P6': 0},
        '3.0TD': { # kW
            'P1': 9810,
            'P2': 9810,
            'P3': 9810,
            'P4': 9810,
            'P5': 9810,
            'P6': 15001},
        '6.1TD': { # kW
            'P1': 50000,
            'P2': 100000,
            'P3': 100000,
            'P4': 100000,
            'P5': 100000,
            'P6': 125000}, 
    }
    
    df_consumo =  build_consumptions_df(fechas_ree, tarifa, consumption_profiles, potencias_contratadas)

    # Step 5: Load 'Cargos y peajes'. Esta variables pueden venir del frontend
    peajes_potencia_boe = { #€/KW.Año. Recuerda dividir entre (365*240 horas/Año
        '2.0TD': { 
            'P1': 30.67,
            'P2': 1.42,
            'P3': 0,
            'P4': 0,
            'P5': 0,
            'P6': 0},
        '3.0TD': {
            'P1': 19.60,
            'P2': 13.78,
            'P3': 7.01,
            'P4': 6.11,
            'P5': 4.40,
            'P6': 2.64},
        '6.1TD': {
            'P1': 30.54,
            'P2': 25.89,
            'P3': 14.91,
            'P4': 12.09,
            'P5': 3.94,
            'P6': 2.11}, 
    }

    peajes_energia_boe = { # €/KWh. Se suman a cada hora de consumo
        '2.0TD': { 
            'P1': 0.133118,
            'P2': 0.041772,
            'P3': 0.006001,
            'P4': 0,
            'P5': 0,
            'P6': 0},
        '3.0TD': {
            'P1': 0.077436,
            'P2': 0.059310,
            'P3': 0.032102,
            'P4': 0.017413,
            'P5': 0.007897,
            'P6': 0.005056},
        '6.1TD': {
            'P1': 0.050891,
            'P2': 0.039222,
            'P3': 0.021931,
            'P4': 0.012193,
            'P5': 0.004437,
            'P6': 0.002892}, 
    }
    
    df_peajes = build_peajes_df(fechas_ree, tarifa, peajes_potencia_boe, peajes_energia_boe )


    # Step 6. Multiply to get terminios fijo y variables between potence and energy
    margen = 4 # eEUR / kW.año - Dividir para 365*24 para sacar horas
    df_terminos_hora = build_terminos_df( df_consumo, df_peajes, prices, tarifa, margen)


    # Step 7: Load 'Impuestos'. Esta variables pueden venir del frontend 

    df_terminos_totales = df_terminos_hora.groupby('Ptarif').sum()
    
    T_Fijo = df_terminos_totales['T_Fijo'].sum()
    T_Variable = df_terminos_totales['T_Variable'].sum()
    
    
    df_subtotal = df_terminos_hora[['Ptarif','PC']]
    df_subtotal.loc[:, 'TF'] = T_Fijo
    df_subtotal.loc[:,'TV'] = T_Variable
    df_subtotal.loc[:, 'IEE'] =  (5.1127/100)*(df_subtotal['TF'] + df_subtotal['TV'])
    df_subtotal.loc[:, 'Alquiler'] = 2/(365*24) # 2 euros al año
    
    # Calculamos el total
    df_total =  df_subtotal.aggregate( {'Ptarif': 'count', 'TF': 'mean', 'TV': 'mean', 'IEE':'mean', 'Alquiler': 'sum' })

    iva = df_total[['TF','TV','IEE','Alquiler']].sum()*(10/100) #  10%
    
    importe_factura = df_total[['TF','TV','IEE','Alquiler']].sum() + iva

    # Volteamos la tortilla
    df_terminos_hora['Imp Electrico'] = df_subtotal['IEE']/len(df_terminos_hora)
    df_terminos_hora['Imp IVA'] = iva/len(df_terminos_hora)
    df_terminos_hora['Alquiler'] = df_subtotal['Alquiler']

    df_terminos_hora.loc[: , 'Peajes Potencia'] = 0.001*df_terminos_hora['PC']*df_terminos_hora['peajes_Potencia']
    df_terminos_hora.loc[: , 'Margen Comercial'] = 0.001*df_terminos_hora['PC']*df_terminos_hora['Margen']
    df_terminos_hora.loc[: , 'Peajes Energia'] = df_terminos_hora['Curva_Consumo']*df_terminos_hora['peajes_Energia']
    df_terminos_hora.loc[: , 'Precio Mercado'] = df_terminos_hora['Curva_Consumo']*df_terminos_hora['Suma Componentes Precio']

    df_graph = df_terminos_hora.loc[: , ['Ptarif','Peajes Potencia','Margen Comercial','Peajes Energia','Precio Mercado','Alquiler','Imp Electrico', 'Imp IVA'] ]

    # Limpiar lo que no está bien
    df_terminos_hora = df_terminos_hora.drop( columns = ['Peajes Potencia','Margen Comercial','Peajes Energia','Precio Mercado'])
#   %% Construimos el Dataframe bonito
    df_tidy = pd.melt( df_graph, id_vars = 'Ptarif', value_vars = ['Precio Mercado','Peajes Potencia','Peajes Energia','Margen Comercial','Alquiler','Imp Electrico','Imp IVA'], ignore_index = False)
    # Asignar Tipo
    df_tidy.loc[ df_tidy['variable'] == 'Precio Mercado', 'type'] = 'Mercado'
    df_tidy.loc[ df_tidy['variable'] == 'Peajes Potencia', 'type'] = 'Peajes'		
    df_tidy.loc[ df_tidy['variable'] == 'Peajes Energia', 'type'] = 'Peajes'
    df_tidy.loc[ df_tidy['variable'] == 'Margen Comercial', 'type'] = 'Comercializadora'
    df_tidy.loc[ df_tidy['variable'] == 'Alquiler', 'type'] = 'Comercializadora'
    df_tidy.loc[ df_tidy['variable'] == 'Imp Electrico', 'type'] = 'Impuestos'
    df_tidy.loc[ df_tidy['variable'] == 'Imp IVA', 'type'] = 'Impuestos'

    print('Hurra!')

#   %% GRAFICAMOS ESTA LOCURITA
    import plotly.express as px
    fig = px.treemap(df_tidy,
        path=[px.Constant("Componentes"), 'type', 'variable'], 
        values='value')
    fig.update_traces(root_color="lightgrey")
    fig.update_layout(margin = dict(t=30, l=25, r=25, b=25))
    fig.show()

    

# %%
