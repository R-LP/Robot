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
initial_capital = 10000
events = e_p2.event_profiler(data, benchmark, initial_capital)

#%%

#On veut un chart avec le benchmark + notre portfolio
#et afficher aussi :
#    standart deviation du retrun, 
#    total return
#    sharpe ratio du return


positions = pd.DataFrame(columns = data.columns)
positions = positions.fillna(0)
ldt_timestamps = events.index
holdings_shares = pd.DataFrame(columns = data.columns, index=data.index).fillna(0.0)

#%%
for i in range(len(ldt_timestamps)):
    
    date = ldt_timestamps[i]
    pair = events['Pair'].iloc[i]    
    shares = events['Number of Shares'].iloc[i]
    order = events['Order'].iloc[i]
    
    if order == 'BUY':
        k = 1
        l = holdings_shares.index.get_loc(date, method='bfill')
        #Ici on a 40 parce que le modele suggere de sell au bout de 40 jours
        #on a un 6x car notre timestamp a 6 echantillons par jour
        for j in range(40*6):
            if l+j < len(holdings_shares):
                holdings_shares[pair].iloc[l+j] += shares
    elif order == 'SELL':
        k=-1
    else:
        print('erreur')
        
    positions = positions.set_value(index=date, col=pair, value=shares*k)
    

portfolio = pd.DataFrame(index=data.index).fillna(0.0)


#%%
holdings_shares2 = holdings_shares.multiply(data, axis=0)
holdings_shares2 = holdings_shares2.fillna(0.0)

#%%
ldt_timestamps = data.index
portfolio = positions.multiply(data, axis = 0).fillna(0.0)

returns = pd.DataFrame(index = ldt_timestamps)
returns["cash"] = 0.0
returns['cash'].iloc[0] = initial_capital

test = pd.DataFrame(index=ldt_timestamps, columns=data.columns)

#On veut vérifier qu'il n'y ait pas de jour où on achete et vende  :

#Liste avec seulement les lignes dont toutes les valeurs ne sont pas strictement negatives
ab = portfolio[~(portfolio <= 0).all(1)]

#Afficher que les resultats faux, ie. il n'y a pas seulement des valeurs
#postives ou nulles, ie y a des valeurs negatives et positives
test = ab[~(ab >= 0).all(1)]


#%%

#On prend en compte les frais de courtage de Poloniex :
    #0.15% pour les market makers (vente d'actifs)
    #0.25% pour les market takers (achat d'actifs)
    
fees = 0

for i in range(1, len(ldt_timestamps)):
    returns['cash'].iloc[i] =  returns['cash'].iloc[i-1]
    

    if not(ldt_timestamps[i] in test.index):    
        if portfolio.iloc[i].sum() <= 0:
            fees += (-1)*portfolio.iloc[i].sum()*0.0015
            returns['cash'].iloc[i] -= portfolio.iloc[i].sum()*0.9985
        elif portfolio.iloc[i].sum() > 0:
            fees += portfolio.iloc[i].sum()*0.0025
            returns['cash'].iloc[i] -= portfolio.iloc[i].sum()*1.0025
        
    elif ldt_timestamps[i] in test.index:        
        for j in range(len(portfolio.columns)):
            if portfolio.iloc[i,j] <= 0:
                fees += (-1)*portfolio.iloc[i].sum()*0.0015
                returns['cash'].iloc[i] -= portfolio.iloc[i,j]*0.9985
            elif portfolio.iloc[i,j] >= 0:
                fees += portfolio.iloc[i].sum()*0.0025
                returns['cash'].iloc[i] -= portfolio.iloc[i,j]*1.0025
            else:
                print('y a encore une couille')
    else:
        print('y a une couille')
    

#%%

returns['holdings'] = 0.0

for i in range(len(ldt_timestamps)):
    returns['holdings'].iloc[i] = holdings_shares2.iloc[i].sum()


#%%
returns['total'] = returns['holdings'] + returns['cash']

returns['returns'] = (returns['total']/ returns['total'].shift(1)) - 1

meanRet = returns['returns'].mean()
stddev = returns['returns'].std()
sharpeRatio = meanRet / stddev

total = (returns['total'].iloc[-1]/returns['total'].iloc[0]) - 1




#%%
import matplotlib.pyplot as plt

fig = plt.figure()
ax1 = fig.add_subplot(111)

returns[['total']].plot(ax=ax1, grid=True)

g_tMC.plot_benchmark(benchmark)

