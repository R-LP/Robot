# -*- coding: utf-8 -*-
"""
Created on Fri Sep 29 14:27:31 2017

@author: Roger
"""

import get_totalMarketCap as g_tMC
import pandas as pd
benchmark = g_tMC.get_totalMarketCap()

#%%
import event_profiler2 as e_p2
data = e_p2.get_data()
#events = e_p2.find_events_news(data, benchmark)

#%%
import event_profiler2 as e_p2
import imp
imp.reload(e_p2)
initial_capital = 10000
events = e_p2.event_profiler(data, benchmark)

#%%

#On veut un chart avec le benchmark + notre portfolio
#et afficher aussi :
#    standart deviation du retrun, 
#    total return
#    sharpe ratio du return

#Si un jour on doit acheter et vendre simulatément, on pense que le plus
#judicieux est : de ne pas vendre ni d'acheter

import numpy as np
from datetime import timedelta

signal_ordre = events.pivot_table(index=events.index, columns='Pair', 
                                  values = 'Order')
signal_ordre = signal_ordre.reindex(data.index)

shares = round(0.02*initial_capital/data) 
shares = shares.replace(np.inf, 0)

nombre_shares_achetees = shares.multiply(
        signal_ordre.where((signal_ordre == 1) | (signal_ordre == 0)), axis=1)

columns = nombre_shares_achetees.columns
nombre_shares_possedees = nombre_shares_achetees.copy()

for i in range(len(columns)):
    a1 = nombre_shares_achetees[columns[i]]
    a = a1[~np.isnan(a1)]

    delta40 = datetime.timedelta(days = 40)
    time = a.index
    time += delta40
    a = pd.Series(a.values, index = time)
    
    nombre_shares_possedees[columns[i]] = nombre_shares_possedees[
            columns[i]].sub(a, fill_value=0.0)
    
    #Si un jour on achete et on vend simultanément, on choisit de ne pas
    #acheter ni vendre, mais deplacer le signal de vente a 40 jours plus tard
    #On fait une boucle pour le cas ou les 40 jours suivant un 0 est égalent un 0....
    #ATTENTION : beug pendant 2h, il fallait faire un delta de 39 jours et pas 40,
    #car on avait un jour au milieu
    
    d = a1[a1==0]
    while(a1.isin([0]).any()):
        b = a1[a1==0]
        time2 = b.index
        
        delta39 = datetime.timedelta(days =39)
        time2 -= delta39
        
        c = a1.loc[time2]
        timeSuivant = b.index + delta39
        c = pd.Series(c.values, index = timeSuivant)
        a1 = c
        nombre_shares_possedees[columns[i]] = nombre_shares_possedees[
                columns[i]].sub(c, fill_value=0.0)
        
        test = nombre_shares_possedees[columns[i]]
        test = test.fillna(0.0)
        test = test.cumsum()

    

prise_positions = nombre_shares_possedees.copy()

trades = prise_positions.multiply(data)
trades = trades.dropna(how='all')

total_shares = nombre_shares_possedees.fillna(0.0)
total_shares = total_shares.cumsum()

beug = total_shares[total_shares<0]
beug = beug.dropna(how='all')

valeur_holdings = total_shares.multiply(data, axis=1)

#%%

#On prend en compte les frais de courtage de Poloniex :
    #0.15% pour les market makers (vente d'actifs)
    #0.25% pour les market takers (achat d'actifs)
    
portfolio = pd.DataFrame(index=trades.index)
portfolio['cash'] = 0.0

valeur_vente = trades[trades<0].dropna(how='all')
valeur_vente = valeur_vente.sum(axis=1)
valeur_vente = (-1)*valeur_vente

valeur_achat = trades[trades>0].dropna(how='all').sum(axis=1)


portfolio['cash'] = portfolio['cash'].sub(valeur_achat*1.0025, fill_value=0.0)
portfolio['cash'] = portfolio['cash'].add(valeur_vente*0.9985, fill_value=0.0)
portfolio['cash'] = initial_capital + portfolio['cash'].cumsum()
#Note : comme la valeur des achats est déjà négative, on doi faire une addition !!

portfolio = portfolio.reindex(data.index)
portfolio = portfolio.fillna(method='ffill')
portfolio = portfolio.fillna(initial_capital)
portfolio['holdings'] = valeur_holdings.sum(axis=1)

#%


#%%
portfolio['total'] = portfolio['holdings'] + portfolio['cash']

portfolio['returns'] = (portfolio['total']/ portfolio['total'].shift(1)) - 1
portfolio['returns'] = portfolio['returns'].replace(np.nan, 0.0)

portfolio['cumul_returns'] = portfolio['returns'] + 1
portfolio['cumul_returns'] = portfolio['cumul_returns'].cumprod()

meanRet = portfolio['returns'].mean()
stddev = portfolio['returns'].std()
sharpeRatio = sqrt(len(portfolio.index))*meanRet / stddev
total = (portfolio['total'].iloc[-1]/portfolio['total'].iloc[0]) - 1




#%%
import matplotlib.pyplot as plt

fig = plt.figure()
ax1 = fig.add_subplot(111)


portfolio[['cumul_returns']].plot(ax=ax1, grid=True)

#g_tMC.plot_benchmark(benchmark)

#%%

portfolio['returns'].hist(bins=500)

