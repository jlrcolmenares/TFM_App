import calendar
from datetime import datetime, timedelta
import holidays
import pandas as pd
import numpy as np

class reeHolidays(holidays.Spain):
     def _populate(self, year):
         # Populate the holiday list with the default ES holidays
         holidays.Spain._populate(self, year)
         # Remove Wrong Festivos
         self.pop_named("Epifanía del Señor")
         self.pop_named("Asunción de la Virgen (Trasladado)")
         #self.pop_named("Asunción de la Virgen")

def ree_periods( startdate, enddate ):
    """ 
    This function take two date and assign the period depending of what de legislation says
    """
    # Initial Assertions
    assert type(startdate) == datetime, 'Must be datetime'
    assert type(enddate) == datetime, 'Must be datetime'

    # Functions
    dates = ree_dates(startdate, enddate)
    dates["period"] = 'P0' # valor por defecto

    # Periodo 6.1A
    ene_61TD_P6 = (dates["datetime"].dt.month == 1 ) & (dates["datetime"].dt.hour.isin( [0,1,2,3,4,5,6,7]) )
    ene_61TD_P2 = (dates["datetime"].dt.month == 1 ) & (dates["datetime"].dt.hour.isin( [8,14,15,16,17,22,23]) )
    ene_61TD_P1 = (dates["datetime"].dt.month == 1 ) & (dates["datetime"].dt.hour.isin( [9,10,11,12,13,18,19,20,21]) )
    feb_61TD_P6 = (dates["datetime"].dt.month == 2 ) & (dates["datetime"].dt.hour.isin( [0,1,2,3,4,5,6,7]) )
    feb_61TD_P2 = (dates["datetime"].dt.month == 2 ) & (dates["datetime"].dt.hour.isin( [8,14,15,16,17,22,23]) )
    feb_61TD_P1 = (dates["datetime"].dt.month == 2 ) & (dates["datetime"].dt.hour.isin( [9,10,11,12,13,18,19,20,21]) )
    mar_61TD_P6 = (dates["datetime"].dt.month == 3 ) & (dates["datetime"].dt.hour.isin( [0,1,2,3,4,5,6,7]) )
    mar_61TD_P3 = (dates["datetime"].dt.month == 3 ) & (dates["datetime"].dt.hour.isin( [8,14,15,16,17,22,23]) )
    mar_61TD_P2 = (dates["datetime"].dt.month == 3 ) & (dates["datetime"].dt.hour.isin( [9,10,11,12,13,18,19,20,21]) )
    abr_61TD_P6 = (dates["datetime"].dt.month == 4 ) & (dates["datetime"].dt.hour.isin( [0,1,2,3,4,5,6,7]) )
    abr_61TD_P5 = (dates["datetime"].dt.month == 4 ) & (dates["datetime"].dt.hour.isin( [8,14,15,16,17,22,23]) )
    abr_61TD_P4 = (dates["datetime"].dt.month == 4 ) & (dates["datetime"].dt.hour.isin( [9,10,11,12,13,18,19,20,21]) )
    may_61TD_P6 = (dates["datetime"].dt.month == 5 ) & (dates["datetime"].dt.hour.isin( [0,1,2,3,4,5,6,7]) )
    may_61TD_P5 = (dates["datetime"].dt.month == 5 ) & (dates["datetime"].dt.hour.isin( [8,14,15,16,17,22,23]) )
    may_61TD_P4 = (dates["datetime"].dt.month == 5 ) & (dates["datetime"].dt.hour.isin( [9,10,11,12,13,18,19,20,21]) )
    jun_61TD_P6 = (dates["datetime"].dt.month == 6 ) & (dates["datetime"].dt.hour.isin( [0,1,2,3,4,5,6,7]) )
    jun_61TD_P4 = (dates["datetime"].dt.month == 6 ) & (dates["datetime"].dt.hour.isin( [8,14,15,16,17,22,23]) )
    jun_61TD_P3 = (dates["datetime"].dt.month == 6 ) & (dates["datetime"].dt.hour.isin( [9,10,11,12,13,18,19,20,21]) )
    jul_61TD_P6 = (dates["datetime"].dt.month == 7 ) & (dates["datetime"].dt.hour.isin( [0,1,2,3,4,5,6,7]) )
    jul_61TD_P2 = (dates["datetime"].dt.month == 7 ) & (dates["datetime"].dt.hour.isin( [8,14,15,16,17,22,23]) )
    jul_61TD_P1 = (dates["datetime"].dt.month == 7 ) & (dates["datetime"].dt.hour.isin( [9,10,11,12,13,18,19,20,21]) )
    ago_61TD_P6 = (dates["datetime"].dt.month == 8 ) & (dates["datetime"].dt.hour.isin( [0,1,2,3,4,5,6,7]) )
    ago_61TD_P4 = (dates["datetime"].dt.month == 8 ) & (dates["datetime"].dt.hour.isin( [8,14,15,16,17,22,23]) )
    ago_61TD_P3 = (dates["datetime"].dt.month == 8 ) & (dates["datetime"].dt.hour.isin( [9,10,11,12,13,18,19,20,21]) )
    sep_61TD_P6 = (dates["datetime"].dt.month == 9 ) & (dates["datetime"].dt.hour.isin( [0,1,2,3,4,5,6,7]) )
    sep_61TD_P4 = (dates["datetime"].dt.month == 9 ) & (dates["datetime"].dt.hour.isin( [8,14,15,16,17,22,23]) )
    sep_61TD_P3 = (dates["datetime"].dt.month == 9 ) & (dates["datetime"].dt.hour.isin( [9,10,11,12,13,18,19,20,21]) )
    oct_61TD_P6 = (dates["datetime"].dt.month == 10 ) & (dates["datetime"].dt.hour.isin( [0,1,2,3,4,5,6,7]) )
    oct_61TD_P5 = (dates["datetime"].dt.month == 10 ) & (dates["datetime"].dt.hour.isin( [8,14,15,16,17,22,23]) )
    oct_61TD_P4 = (dates["datetime"].dt.month == 10 ) & (dates["datetime"].dt.hour.isin( [9,10,11,12,13,18,19,20,21]) )
    nov_61TD_P6 = (dates["datetime"].dt.month == 11 ) & (dates["datetime"].dt.hour.isin( [0,1,2,3,4,5,6,7]) )
    nov_61TD_P3 = (dates["datetime"].dt.month == 11 ) & (dates["datetime"].dt.hour.isin( [8,14,15,16,17,22,23]) )
    nov_61TD_P2 = (dates["datetime"].dt.month == 11 ) & (dates["datetime"].dt.hour.isin( [9,10,11,12,13,18,19,20,21]) )
    dic_61TD_P6 = (dates["datetime"].dt.month == 12 ) & (dates["datetime"].dt.hour.isin( [0,1,2,3,4,5,6,7]) )
    dic_61TD_P2 = (dates["datetime"].dt.month == 12 ) & (dates["datetime"].dt.hour.isin( [8,14,15,16,17,22,23]) )
    dic_61TD_P1 = (dates["datetime"].dt.month == 12 ) & (dates["datetime"].dt.hour.isin( [9,10,11,12,13,18,19,20,21]) )
    fest = dates["feriado_finde"]

    dates['period'] = np.select([
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


def ree_dates( startdate, enddate):
    """
    Take two dates and return a dataframe with the date that are according to REE
    """
    # Initial Assertions
    assert type(startdate) == datetime, 'Must be datetime'
    assert type(enddate) == datetime, 'Must be datetime'
    # Functions
    hours = []

    if startdate.year == enddate.year:
        year_spawn = range(startdate.year,enddate.year+1)
    else:
        year_spawn = range(startdate.year,enddate.year)

    # Calculate 'Festivos nacionales no desplazables'
    festivos = []
    for date in reeHolidays( prov=None, years = year_spawn).items():
        for hour in range(0,13):
            dt = datetime.combine(date[0], datetime.hour.time( hour ))
            festivos.append( dt ) # Tengo el problema que me toma el 6 de enero y 16 de agosto como festivos nacionales. Eso no es así
    print( len( festivos ))
    
    for year in year_spawn:
        #print(year)
        for month in range(1,13): #
            #print(month)
            c = calendar.monthcalendar(year, month) # month_weeks
            month_days = []
            for week in c:
                for day in week:
                    if day != 0:
                        month_days.append(day)

            last_week = c[-1]
            before_last_week = c[-2]

            if month == 3: # march
                if last_week[calendar.SUNDAY]:
                    day_short = last_week[calendar.SUNDAY]
                else:
                    day_short = before_last_week[calendar.SUNDAY]
                
                for day in month_days:
                    if day == day_short:
                        for hour in [0,1,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23]:
                            hours.append( datetime(year, month, day, hour) )
                    else: # another day in march
                        for hour in range(0,24):
                            hours.append( datetime(year, month, day, hour))

            elif month == 10: # october
                if last_week[calendar.SUNDAY]:
                    day_long = last_week[calendar.SUNDAY]
                else:
                    day_long = before_last_week[calendar.SUNDAY]

                for day in month_days:
                    if day == day_long:
                        for hour in [0,1,2,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23]:
                            hours.append( datetime(year, month, day, hour) )
                    else: # another day in october
                        for hour in range(0,24):
                            hours.append( datetime(year, month, day, hour))

            else: 
                for day in month_days:
                    for hour in range(0,24): # usual days with 24 hours
                        hours.append( datetime(year, month, day, hour))

    output = []
    for item in hours:
        output.append( [
            item.year,
            item.month,
            item.day,
            item.hour,
            item,
            item.strftime("%Y/%m/%d %H:%M")])

    df = pd.DataFrame( output,  columns=["year", "month", "day", "hour", "datetime", "string"]) # add columns

    # Set a flag for holidays and weekends (important for electric periods)
    df['feriado_finde'] = 0
    df.loc[ ( df["datetime"].dt.weekday.isin([5,6]) | df["datetime"].isin(festivos) ) , 'feriado_finde' ] = 1

    # invierno_verano



    # Before returning the output. Filter between the date: 
    df = df.loc[ (df['datetime']>=startdate) & (df['datetime']<=enddate) ]

    return df

if __name__ == '__main__':
    
    startdate = datetime(2021, 1,1,10)
    enddate = datetime(2022,5,1,8)
    ree_periods( startdate, enddate)
    print("END")
