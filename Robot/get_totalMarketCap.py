# -*- coding: utf-8 -*-
"""
Created on Tue Sep 26 16:06:38 2017

@author: Roger
"""

#Note :
# Si on a l'erreur :
#    URLError: <urlopen error EOF occurred in violation of protocol (_ssl.c:749)>
# C'est qu'on a fait trop de requetes au serveur, il faut changer d'IP


#On veut créer un indicateur qui mesure le comportement des cryptos
#L'indicateur sera le market cap des cryptos au complet

import time
import urllib
import json
import matplotlib.pyplot as plt
import pandas as pd
from datetime import date
from datetime import datetime
from matplotlib.ticker import FuncFormatter

#%%


def get_totalMarketCap(start = date(2016, 1, 1), end = date(2017, 9, 25)):
 
    end = str(int(time.mktime(end.timetuple())*1000))
    start = str(int(time.mktime(start.timetuple())*1000)) 
                
    #%%
    urlQuotes = urllib.request.urlopen('https://graphs.coinmarketcap.com/global/marketcap-total/'
                                       + start + '/' + end + '/')
    
    #%%
    data = urlQuotes.read()
    data2 = json.loads(data)
    
    timeStamp = []
    marketValue = []
    volume = []
    for i in data2['market_cap_by_available_supply']:
        timeStamp.append(i[0])
        marketValue.append(i[1])
    
    for i in data2['volume_usd']:
        volume.append(i[1])
    
    df_time = pd.to_datetime(timeStamp, unit='ms')
    df = pd.DataFrame(marketValue, index=df_time)
    df.columns = ['market_cap_($)']
    
    #Les datas données par Coinbase ne sont pas toujours à la même heure
    #Alors que la plupart sont à 16h00, certaines sont à 16h02 ou 15h57
    #Pour que nos timestamp correspondent, on corrige ces dates pour les
    #remettre à 16h00
    
    newIndex = []
    for i in df.index:
        if ((i.to_datetime()).minute != 0):
            i = (i.to_datetime()).replace(minute=0)
            i = pd.to_datetime(i)
            
            if((i.to_datetime()).hour != 16):
                i = (i.to_datetime()).replace(hour=16)
                i = pd.to_datetime(i)
                newIndex.append(i)
            else:
                newIndex.append(i)
        else:
            newIndex.append(i)
            
    df['newIndex'] = newIndex
    benchmarkIndexed = df.set_index(df['newIndex'])
    benchmarkIndexed = benchmarkIndexed.drop('newIndex', axis=1)
    
    benchmarkIndexed['volume'] = volume
    benchmarkIndexed.to_csv('benchmark.csv')
    return benchmarkIndexed
    

def plot_benchmark(benchmark):
    
    fig = plt.figure()    
    ax = fig.add_subplot(111)
    
    #Permet de ploter avec les valeurs de l'axe Y affichées en milliard
    #Au lieu d'avoir des notations scientifiques
    
    def billions(x, pos):
        'The two args are the value and tick position'
        return '$%1.fB' % (x*1e-9)
    
    formatter = FuncFormatter(billions)
    ax.yaxis.set_major_formatter(formatter)
    ax.set(title="Total Market Capitalization", xlabel="date", ylabel="USD")
    benchmark.plot(ax=ax, grid=True)
           