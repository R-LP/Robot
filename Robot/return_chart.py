import urllib
import json
import time

def return_chart(currencyPair, start, end, *period):
    
    # if no period is given, the default period will be 14400 seconds 
    if not period:
        period = str(14400)
    else:
        period = str(period[0])
    
    end = str(time.mktime(end.timetuple()))
    start = str(time.mktime(start.timetuple()))
    urlQuotes = urllib.request.urlopen('https://poloniex.com/public?command=returnChartData&currencyPair=' + currencyPair
                                           + '&start=' + start
                                           + '&end=' + end
                                           + '&period=' + period)
                                     
    rawQuotes = urlQuotes.read()
    ## permet de lire correctement les data au format JSON
    data = json.loads(rawQuotes)
    
    return data


  