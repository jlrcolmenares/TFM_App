def ree_dates( startdate, enddate):
    """
    Take two date and return a dataframe with the date that are according to REE
    """
    # Initial Assertions
    assert type(startdate) == datetime, 'Must be datetime'
    assert type(enddate) == datetime, 'Must be datetime'
    # Functions
    hours = []
    for year in range(startdate.year,enddate.year):
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
    return df
        