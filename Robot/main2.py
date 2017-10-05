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

for i in range(1, len(ldt_timestamps)):
    
    date = ldt_timestamps[i]
    pair = events['Pair'].iloc[i]    
    shares = events['Number of Shares'].iloc[i]
    order = events['Order'].iloc[i]
    
    if order == 'BUY':
        k=1
    elif order == 'SELL':
        k=-1
    else:
        print('erreur')
    positions = positions.set_value(index=date, col=pair, value=shares*k)
    

portfolio = pd.DataFrame(index=data.index).fillna(0.0)



#%%
ldt_timestamps = data.index
portfolio = positions.multiply(data, axis = 0).fillna(0.0)

returns = pd.DataFrame(index = ldt_timestamps)
returns["cash"] = 0.0
returns['cash'].iloc[0] = initial_capital



for i in range(1, len(ldt_timestamps)):
    returns['cash'].iloc[i] = returns['cash'].iloc[i-1] - portfolio.iloc[i].sum()


#%%

test2 = returns.join(positions)
test2 = test2.fillna(method='ffill')

test2 = test2.drop('cash', axis=1)
test2 = test2.fillna(0.0)

test3 = test2.multiply(data, axis = 0)

returns['holdings'] = 0.0

for i in range(1, len(ldt_timestamps)):
    returns['holdings'].iloc[i] = test3.iloc[i].sum()


#%%
returns['total'] = returns['holdings'] + returns['cash']

returns['returns'] = (returns['total']/ returns['total'].shift(1)) - 1

meanRet = returns['returns'].mean()
stddev = returns['returns'].std()
sharpeRatio = meanRet / stddev




#%%
import matplotlib.pyplot as plt

fig = plt.figure()
ax1 = fig.add_subplot(111)

returns[['total', 'holdings']].plot(ax=ax1)

g_tMC.plot_benchmark(benchmark)



#%%

positions = positions.fillna(0)
positions.values.sum()/100

#%%

portfolio = pd.DataFrame(index=data.index).fillna(0.0)
   
portfolio[0]['cash'] = initial_capital


positions = pd.DataFrame(index=signals.index).fillna(0.0)
positions['ETH'] = 100 * signals['signal']
portfolio = positions.multiply(df2.close, axis=0)
pos_diff = positions.diff()
portfolio['holdings'] = (positions.multiply(df2.close, axis = 0))
portfolio['cash'] = initial_capital - (pos_diff.multiply(df2.close, axis = 0)).cumsum()
portfolio['total'] = portfolio['cash'] + portfolio['holdings']
portfolio['returns'] = portfolio['total'].pct_change().cumsum()

