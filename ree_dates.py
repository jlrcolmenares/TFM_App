import calendar
from datetime import date, datetime, timedelta
import holidays
import pandas as pd
import numpy as np
import re

class reeHolidays(holidays.Spain):
     def _populate(self, year):
        # Populate the holiday list with the default ES holidays
        full_holidays =  holidays.Spain._populate(self, year)
        # Remove Festivos Trasladados. That doesn't apply to REE
        trasladados = []
        for day in self.values():
            if re.search("(Trasladado)", day):
                trasladados.append(day)
            
        for item in trasladados:
            self.pop_named(item)
        
        # Then remove other 2 ones 
        # try:
        #     self.pop_named("Epifanía del Señor")
        # except KeyError:
        #     print("No existe Epifania")
        
        try:
            self.pop_named("Viernes Santo")
        except KeyError:
            self.pop_named('No existe Viernes Santo')
        
        # Add  Festivos (Just to remember)
        #self[ date( year , 1,6)] = "Día de Reyes"


def ree_periods( startdate, enddate ):
    """ 
    This function take two date and assign the period depending of what de legislation says
    """
    # Initial Assertions
    assert type(startdate) == datetime, 'Must be datetime'
    assert type(enddate) == datetime, 'Must be datetime'

    # Work with dates
    dates = ree_dates(startdate, enddate)
    
    # Periodos 2.0TD
    dates["20TD_periods"] = 'P0' # valor por defecto
    
    fest = (dates["feriado_finde"] == 1).values
    energy_20TD_P1 = dates.index.hour.isin( [10,11,12,13,18,19,20,21] ) & (fest == False) 
    energy_20TD_P2 = dates.index.hour.isin( [8,9,14,15,16,17,22,23] ) & (fest == False) 
    energy_20TD_P3 = dates.index.hour.isin( [0,1,2,3,4,5,6,7,] ) & (fest == False) 
    
    #potence_20TD_P1 = dates.index.hour.isin( range(0,8) )
    #potence_20TD_P2 = dates.index.hour.isin( range(8,24) )

    dates['20TD_periods'] = np.select(
        [energy_20TD_P1, energy_20TD_P2, energy_20TD_P3, fest],
        [1,2,3,3]
    )
    
    # Periodo 6.1TD y 3.0TD
    dates["61TD_periods"] = 'P0' # valor por defecto
    dates["30TD_periods"] = 'P0'

    fest = (dates["feriado_finde"] == 1).values
    ene_61TD_P6 = (dates.index.month == 1 ) & (dates.index.hour.isin( [0,1,2,3,4,5,6,7]) ) & (fest == False)
    ene_61TD_P2 = (dates.index.month == 1 ) & (dates.index.hour.isin( [8,14,15,16,17,22,23]) ) & (fest == False)
    ene_61TD_P1 = (dates.index.month == 1 ) & (dates.index.hour.isin( [9,10,11,12,13,18,19,20,21]) ) & (fest == False)
    feb_61TD_P6 = (dates.index.month == 2 ) & (dates.index.hour.isin( [0,1,2,3,4,5,6,7]) ) & (fest == False)
    feb_61TD_P2 = (dates.index.month == 2 ) & (dates.index.hour.isin( [8,14,15,16,17,22,23]) ) & (fest == False)
    feb_61TD_P1 = (dates.index.month == 2 ) & (dates.index.hour.isin( [9,10,11,12,13,18,19,20,21]) ) & (fest == False)
    mar_61TD_P6 = (dates.index.month == 3 ) & (dates.index.hour.isin( [0,1,2,3,4,5,6,7]) ) & (fest == False)
    mar_61TD_P3 = (dates.index.month == 3 ) & (dates.index.hour.isin( [8,14,15,16,17,22,23]) ) & (fest == False)
    mar_61TD_P2 = (dates.index.month == 3 ) & (dates.index.hour.isin( [9,10,11,12,13,18,19,20,21]) ) & (fest == False)
    abr_61TD_P6 = (dates.index.month == 4 ) & (dates.index.hour.isin( [0,1,2,3,4,5,6,7]) ) & (fest == False)
    abr_61TD_P5 = (dates.index.month == 4 ) & (dates.index.hour.isin( [8,14,15,16,17,22,23]) ) & (fest == False)
    abr_61TD_P4 = (dates.index.month == 4 ) & (dates.index.hour.isin( [9,10,11,12,13,18,19,20,21]) ) & (fest == False)
    may_61TD_P6 = (dates.index.month == 5 ) & (dates.index.hour.isin( [0,1,2,3,4,5,6,7]) ) & (fest == False)
    may_61TD_P5 = (dates.index.month == 5 ) & (dates.index.hour.isin( [8,14,15,16,17,22,23]) ) & (fest == False)
    may_61TD_P4 = (dates.index.month == 5 ) & (dates.index.hour.isin( [9,10,11,12,13,18,19,20,21]) ) & (fest == False)
    jun_61TD_P6 = (dates.index.month == 6 ) & (dates.index.hour.isin( [0,1,2,3,4,5,6,7]) ) & (fest == False)
    jun_61TD_P4 = (dates.index.month == 6 ) & (dates.index.hour.isin( [8,14,15,16,17,22,23]) ) & (fest == False)
    jun_61TD_P3 = (dates.index.month == 6 ) & (dates.index.hour.isin( [9,10,11,12,13,18,19,20,21]) ) & (fest == False)
    jul_61TD_P6 = (dates.index.month == 7 ) & (dates.index.hour.isin( [0,1,2,3,4,5,6,7]) ) & (fest == False)
    jul_61TD_P2 = (dates.index.month == 7 ) & (dates.index.hour.isin( [8,14,15,16,17,22,23]) ) & (fest == False)
    jul_61TD_P1 = (dates.index.month == 7 ) & (dates.index.hour.isin( [9,10,11,12,13,18,19,20,21]) ) & (fest == False)
    ago_61TD_P6 = (dates.index.month == 8 ) & (dates.index.hour.isin( [0,1,2,3,4,5,6,7]) ) & (fest == False)
    ago_61TD_P4 = (dates.index.month == 8 ) & (dates.index.hour.isin( [8,14,15,16,17,22,23]) ) & (fest == False)
    ago_61TD_P3 = (dates.index.month == 8 ) & (dates.index.hour.isin( [9,10,11,12,13,18,19,20,21]) ) & (fest == False)
    sep_61TD_P6 = (dates.index.month == 9 ) & (dates.index.hour.isin( [0,1,2,3,4,5,6,7]) ) & (fest == False)
    sep_61TD_P4 = (dates.index.month == 9 ) & (dates.index.hour.isin( [8,14,15,16,17,22,23]) ) & (fest == False)
    sep_61TD_P3 = (dates.index.month == 9 ) & (dates.index.hour.isin( [9,10,11,12,13,18,19,20,21]) ) & (fest == False)
    oct_61TD_P6 = (dates.index.month == 10 ) & (dates.index.hour.isin( [0,1,2,3,4,5,6,7]) ) & (fest == False)
    oct_61TD_P5 = (dates.index.month == 10 ) & (dates.index.hour.isin( [8,14,15,16,17,22,23]) ) & (fest == False)
    oct_61TD_P4 = (dates.index.month == 10 ) & (dates.index.hour.isin( [9,10,11,12,13,18,19,20,21]) ) & (fest == False)
    nov_61TD_P6 = (dates.index.month == 11 ) & (dates.index.hour.isin( [0,1,2,3,4,5,6,7]) ) & (fest == False)
    nov_61TD_P3 = (dates.index.month == 11 ) & (dates.index.hour.isin( [8,14,15,16,17,22,23]) ) & (fest == False)
    nov_61TD_P2 = (dates.index.month == 11 ) & (dates.index.hour.isin( [9,10,11,12,13,18,19,20,21]) ) & (fest == False)
    dic_61TD_P6 = (dates.index.month == 12 ) & (dates.index.hour.isin( [0,1,2,3,4,5,6,7]) ) & (fest == False)
    dic_61TD_P2 = (dates.index.month == 12 ) & (dates.index.hour.isin( [8,14,15,16,17,22,23]) ) & (fest == False)
    dic_61TD_P1 = (dates.index.month == 12 ) & (dates.index.hour.isin( [9,10,11,12,13,18,19,20,21]) ) & (fest == False)

    dates['61TD_periods'] = np.select([
        ene_61TD_P6, ene_61TD_P2, ene_61TD_P1,feb_61TD_P6, feb_61TD_P2, feb_61TD_P1,
        mar_61TD_P6, mar_61TD_P3, mar_61TD_P2,abr_61TD_P6, abr_61TD_P5, abr_61TD_P4,
        may_61TD_P6, may_61TD_P5, may_61TD_P4,jun_61TD_P6, jun_61TD_P4, jun_61TD_P3,
        jul_61TD_P6, jul_61TD_P2, jul_61TD_P1,ago_61TD_P6, ago_61TD_P4, ago_61TD_P3,
        sep_61TD_P6, sep_61TD_P4, sep_61TD_P3,oct_61TD_P6, oct_61TD_P5, oct_61TD_P4,
        nov_61TD_P6, nov_61TD_P3, nov_61TD_P2,dic_61TD_P6, dic_61TD_P2, dic_61TD_P1,
        fest],[
            6,2,1,6,2,1,
            6,3,2,6,5,4,
            6,5,4,6,4,3,
            6,2,1,6,4,3,
            6,4,3,6,5,4,
            6,3,2,6,2,1,
            6]
    )

    dates["30TD_periods"] = dates["61TD_periods"]

    return dates 


def ree_dates( startdate, enddate):
    """
    Take two dates and return a dataframe with the date that are according to REE
    """
    # Initial Assertions
    assert type(startdate) == datetime, 'Must be datetime'
    assert type(enddate) == datetime, 'Must be datetime'
    
    hours = [] # Outpu variable

    if startdate.year == enddate.year:
        year_spawn = range(startdate.year,enddate.year+1)
    else:
        year_spawn = range(startdate.year,enddate.year)

    # Calculate 'Festivos nacionales no desplazables'
    festivos = []
    for date in reeHolidays( prov=None, years = year_spawn).items():
        dt = datetime.combine(date[0], datetime.min.time())
        for hour in range(0,24):
            festivos.append(dt + timedelta(hours = hour))
    
    # Save, daylight saving days
    daylight_saving = []

    # Main Function
    for year in year_spawn:
        #print(year)
        for month in range(1,13): #
            #print(month)
            c = calendar.monthcalendar(year, month) # month-weeks
            month_days = []
            for week in c:
                for day in week:
                    if day != 0:
                        month_days.append(day)

            # Detecting daylight saving time day
            last_week = c[-1]
            before_last_week = c[-2]

            if month == 3: # March: month were change from winter to summer occurs
                if last_week[calendar.SUNDAY]:
                    day_short = last_week[calendar.SUNDAY]
                else:
                    day_short = before_last_week[calendar.SUNDAY]
                
                for day in month_days:
                    if day == day_short:
                        for hour in [0,1,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23]:
                            hours.append( datetime(year, month, day, hour) )
                    else: # any other in march
                        for hour in range(0,24):
                            hours.append( datetime(year, month, day, hour))

            elif month == 10: # October: month were change from summer to winter occurs
                if last_week[calendar.SUNDAY]:
                    day_long = last_week[calendar.SUNDAY]
                else:
                    day_long = before_last_week[calendar.SUNDAY]

                for day in month_days:
                    if day == day_long:
                        for hour in [0,1,2,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23]:
                            hours.append( datetime(year, month, day, hour) )
                    else: # any other day in october
                        for hour in range(0,24):
                            hours.append( datetime(year, month, day, hour))

            else: 
                for day in month_days:
                    for hour in range(0,24): # normal days with 24 hours
                        hours.append( datetime(year, month, day, hour))

            #daylight_saving.append([day_short, day_long])

    output = []
    for item in hours:
            output.append( [
                item.year,
                item.month,
                item.day,
                item.hour,
                item,
                item.strftime("%Y-%m-%dT%H:%M")])

    df = pd.DataFrame( output,  columns=["year", "month", "day", "hour", "datetime", "string"]) # add columns
    df = df.set_index('datetime')

    # Set a flag for holidays and weekends (important for electric periods)
    df['feriado_finde'] = 0
    df.loc[ ( df.index.weekday.isin([5,6]) | df.index.isin(festivos) ) , 'feriado_finde' ] = 1

    # invierno_verano
    # df['verano(1)/invierno(0)']
    # for pair in daylight_saving:
    #     summer_start = pair[0].strftime('%Y-%m-%d')
    #     summer_ends = pair[1].strftime('%Y-%m-%d')
    #     df.between_time( summer_start, summer_ends )

    # Before returning the output. Filter between the date: 
    df = df.loc[ startdate : enddate ]

    return df

if __name__ == '__main__':
    
    startdate = datetime(2019, 1,1,10)
    enddate = datetime(2022,5,1,8)
    ree_periods( startdate, enddate)
    print("END")
