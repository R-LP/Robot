# -*- coding: utf-8 -*-
"""
Created on Wed Sep 27 21:01:05 2017

@author: Roger
"""

"""

Also, d1 = start date
nan = no information about any event.
1 = status bit(positively confirms the event occurence)
"""
#%%
import pandas as pd
import get_totalMarketCap as get_tMC
from datetime import date
import ticker

#ticker = ticker.getTicker()['quote']
#
##%%
#quotes = []
#for i in ticker:
#    quotes.append(i)

#%%
from os import walk

import os
datas_list = os.listdir('Data')
#%%

df = pd.read_csv('2016_BTC_ETH.csv')
df = df.set_index(df['date'], drop=True)
df = df.drop('date', axis=1)

end = date(2017, 1, 1)
start = date(2016, 1, 1)
benchmark = get_tMC.get_totalMarketCap(start, end)

#%%
#Les datas données par Coinbase ne sont pas toujours à la même heure
#Alors que la plupart sont à 16h00, certaines sont à 16h02 ou 15h57
#Pour que nos timestamp correspondent, on corrige ces dates pour les
#remettre à 16h00

newIndex = []
for i in benchmark.index:
    if ((i.to_datetime()).minute != 0):
        print((i.to_datetime()).minute)
        i = (i.to_datetime()).replace(minute=0)
        i = pd.to_datetime(i)
        print((i.to_datetime()).minute)
        
        if((i.to_datetime()).hour != 16):
            i = (i.to_datetime()).replace(hour=16)
            i = pd.to_datetime(i)
            newIndex.append(i)
        else:
            newIndex.append(i)
    else:
        newIndex.append(i)
        
benchmark['newIndex'] = newIndex
benchmarkIndexed = benchmark.set_index(benchmark['newIndex'])
benchmarkIndexed = benchmarkIndexed.drop('newIndex', axis=1)
benchmarkIndexed = benchmarkIndexed.drop('volume', axis=1)

#%%
test2 = benchmarkIndexed.join(df['close'])

#%%
import copy
import numpy as np

df_events = copy.deepcopy(test2)
df_events= df_events.drop('market_cap_($)', axis=1)
df_events = df_events * np.NAN

# Time stamps for the event range
ldt_timestamps = test2.index


for i in range(1, len(ldt_timestamps)):
    # Calculating the returns for this timestamp
    f_symprice_today = test2['close'].ix[ldt_timestamps[i]]
    f_symprice_yest = test2['close'].ix[ldt_timestamps[i - 1]]
    f_marketprice_today = test2['market_cap_($)'].ix[ldt_timestamps[i]]
    f_marketprice_yest = test2['market_cap_($)'].ix[ldt_timestamps[i - 1]]
    f_symreturn_today = (f_symprice_today / f_symprice_yest) - 1
    f_marketreturn_today = (f_marketprice_today / f_marketprice_yest) - 1

    # Event is found if the symbol is down more then 3% while the
    # market is up more then 2%
    if f_symreturn_today <= -0.03 and f_marketreturn_today >= 0.02:
        print(i)
        df_events.ix[ldt_timestamps[i]] = 1


#%%
#On veut maintenant observer l'etat moyen du marché +/- 20 jours autour
#de la news

#On va créer le %variation de nos data
test2['%change'] = (test2['close'] / test2['close'].shift(1)) - 1
test2['%change'] = test2['%change'].fillna(0.0)

#on enleve l'offset qui correspond à la variation du marché
test2['%change_market'] = (test2['market_cap_($)'] / test2['market_cap_($)'].shift(1)) - 1
test2['%change_market'] = test2['%change_market'].fillna(0.0)

test2['%change_nonCorrele'] = test2['%change'] - test2['%change_market']


i_lookback=20
i_lookforward=20
df_events.values[0:i_lookback, :] = np.NaN
df_events.values[-i_lookforward:, :] = np.NaN

#%%
# Number of events
i_no_events = int(np.logical_not(np.isnan(df_events.values)).sum())
assert i_no_events > 0, "Zero events in the event matrix"
na_event_rets = "False"

df_rets = pd.DataFrame(index=test2.index)
df_rets=test2['%change_nonCorrele'].copy()
#%%

# Looking for the events and pushing them to a matrix

for j, dt_date in enumerate(df_events.index):
    if(df_events['close'].loc[dt_date] == 1):
        na_ret = df_rets[j - i_lookback:j + 1 + i_lookforward]
        if type(na_event_rets) == type(""):
            na_event_rets = na_ret
            print('test')
        else:
            na_event_rets = np.vstack((na_event_rets, na_ret))
            print('test2')

#%%
import matplotlib.pyplot as plt
if len(na_event_rets.shape) == 1:
    na_event_rets = np.expand_dims(na_event_rets, axis=0)
    

# Computing daily rets and retuns
na_event_rets = np.cumprod(na_event_rets + 1, axis=1)
na_event_rets = (na_event_rets.T / na_event_rets[:, i_lookback]).T


# Study Params
na_mean = np.mean(na_event_rets, axis=0)
na_std = np.std(na_event_rets, axis=0)
li_time = range(-i_lookback, i_lookforward + 1)

# Plotting the chart
plt.clf()
plt.axhline(y=1.0, xmin=-i_lookback, xmax=i_lookforward, color='k')

plt.errorbar(li_time[i_lookback:], na_mean[i_lookback:],
             yerr=na_std[i_lookback:], ecolor='#AAAAFF',
             alpha=0.1)
plt.plot(li_time, na_mean, linewidth=3, label='mean', color='b')
plt.xlim(-i_lookback - 1, i_lookforward + 1)

plt.title('Market Relative mean return of ' +\
          str(i_no_events) + ' events')

plt.xlabel('Days')
plt.ylabel('Cumulative Returns')

