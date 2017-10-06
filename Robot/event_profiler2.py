# -*- coding: utf-8 -*-
"""
Created on Wed Sep 27 21:01:05 2017

@author: Roger
"""

#%%
import pandas as pd
import get_totalMarketCap as get_tMC
from datetime import date
import os
import copy
import numpy as np
import datetime
from random import *


#%%
#
def get_data(rand=False, name=False):
    
    datas_list = os.listdir('Data')
    df = pd.DataFrame()
    
    k=0
    for i in datas_list:
        df2 = pd.read_csv('Data\\'+i)
        df2 = df2.set_index(df2['date'])
        i = i.replace(".csv", "")
        df3 = df2['close'].to_frame(i)
        df = df.merge(df3, left_index=True, right_index=True, how='outer')
        datas_list[k] = i
        k+=1
    df.index = pd.to_datetime(df.index)
    
    if rand:
        numero_data = set()
        for i in range(rand):
            num = randint(0, len(datas_list)-1)
            while (num in numero_data):
                num = randint(0, len(datas_list)-1)
            numero_data.add(num)
        return df.ix[:, numero_data]
    
    if name:
        return df.loc[:, name]
        
    else:
        return df


#%%
#test2 = benchmarkIndexed.join(df)

def event_profiler(dataset, benchmark):
    
    s_market_sym = 'market_cap_($)'

    # Time stamps for the event range    
    benchmark2 = benchmark.reindex(dataset.index, method='pad')
    benchmark2 = benchmark2.fillna(method='pad', limit=2)
    
    data = dataset.join(benchmark2)
    
    ldt_timestamps = data.index    
    cols = ['Date', 'Pair', 'Order']
    
    size = int(round(len(ldt_timestamps) * len(dataset.columns) / 3))
    df_events = pd.DataFrame(columns=cols, index=range(size))
    
    k = 0
    print('Finding events in progress', end='')
    for s_sym in dataset.columns:
        print('.', end='')
        for i in range(1, len(ldt_timestamps)):
            # Calculating the returns for this timestamp
            f_symprice_today = data[s_sym][ldt_timestamps[i]]
            f_symprice_yest = data[s_sym][ldt_timestamps[i - 1]]
            f_marketprice_today = data[s_market_sym][ldt_timestamps[i]]
            f_marketprice_yest = data[s_market_sym][ldt_timestamps[i - 1]]
            f_symreturn_today = (f_symprice_today / f_symprice_yest) - 1
            f_marketreturn_today = (f_marketprice_today / f_marketprice_yest) - 1
        
            # Event is found if the symbol is down more then 3% while the
            # market is up more then 2%
            if f_symreturn_today <= -0.03 and f_marketreturn_today >= 0.02:
                
                #Open trade
                df_events.iloc[k] = [ldt_timestamps[i], s_sym, 'BUY']               
                k+=1
                
                #Close trade
                timeClose = datetime.timedelta(days = 40)
                time = ldt_timestamps[i]
                time += timeClose
                df_events.iloc[k] = [time, s_sym, 'SELL']
                k+=1
            
    print('Success !')
    
    df_events = df_events.dropna()
    df_events = df_events.set_index('Date')
    df_events = df_events.drop('Date')
    df_events.index = pd.to_datetime(df_events.index)
    df_events = df_events.sort_index()
    
    df_events.to_csv('Orders.csv')
    df_events.replace(['SELL', 'BUY'], [-1, 1], inplace=True) 
    
    return df_events

#%%

def events_study(events, dataset, benchmark):
    #On veut maintenant observer l'etat moyen du marché +/- 20 jours autour
    #de la news
    
    s_market_sym = 'market_cap_($)'
    test2 = benchmark.join(dataset)
    df_events = events.copy()
    #On va créer le %variation de nos data
    df_rets = test2.copy()
    df_rets = (df_rets / df_rets.shift(1)) - 1
    df_rets = df_rets.fillna(0.0)
    
    #%%
    df_rets = df_rets.sub(df_rets['market_cap_($)'].values, axis=0)
    del df_rets[s_market_sym]
    
    #%%
    i_lookback=20
    i_lookforward=100
    df_events.values[0:i_lookback, :] = np.NaN
    df_events.values[-i_lookforward:, :] = np.NaN
    
    #%%
    import matplotlib.pyplot as plt
    # Number of events
    i_no_events = int(np.logical_not(np.isnan(df_events.values)).sum())
    assert i_no_events > 0, "Zero events in the event matrix"
    na_event_rets = "False"
    
    # Looking for the events and pushing them to a matrix
    for i, s_sym in enumerate(df_events.columns):
        for j, dt_date in enumerate(df_events.index):
            if df_events[s_sym][dt_date] == 1:
                na_ret = df_rets[s_sym][j - i_lookback:j + 1 + i_lookforward]
                if type(na_event_rets) == type(""):
                    na_event_rets = na_ret
                else:
                    na_event_rets = np.vstack((na_event_rets, na_ret))
    
    if len(na_event_rets.shape) == 1:
        na_event_rets = np.expand_dims(na_event_rets, axis=0)
    
    #%%
    # Computing daily rets and retuns
    na_event_rets = np.cumprod(na_event_rets + 1, axis=1)
    
    #%%
    from numpy import inf
    from numpy import nan
    
    na_event_rets = na_event_rets[~np.isnan(na_event_rets).any(axis=1)]
    na_event_rets = na_event_rets[~np.isinf(na_event_rets).any(axis=1)]
    
    #%%
    na_event_rets = (na_event_rets.T / na_event_rets[:, i_lookback]).T
    
    #%%
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
    plt.ylim(0.9, 1.5)
    
    
    plt.title('Market Relative mean return of ' +\
            str(i_no_events) + ' events')
    
    plt.xlabel('Days')
    plt.ylabel('Cumulative Returns')
    
    
    
#%%
def find_events_news(dataset, benchmark):
    
    s_market_sym = 'market_cap_($)'
    print('Hello trou d\'ulc !')
    
    # Time stamps for the event range    
    data = benchmark.join(dataset)
    ldt_timestamps = data.index
    
    df_events = copy.deepcopy(data)
    df_events = df_events * np.NAN
    
    df_events = df_events.drop('volume', axis=1)
    df_events = df_events.drop(s_market_sym, axis=1)
    
    print('Finding events in progress', end='')
    for s_sym in df_events.columns:
        print('.', end='')
        for i in range(1, len(ldt_timestamps)):
            # Calculating the returns for this timestamp
            f_symprice_today = data[s_sym][ldt_timestamps[i]]
            f_symprice_yest = data[s_sym][ldt_timestamps[i - 1]]
            f_marketprice_today = data[s_market_sym][ldt_timestamps[i]]
            f_marketprice_yest = data[s_market_sym][ldt_timestamps[i - 1]]
            f_symreturn_today = (f_symprice_today / f_symprice_yest) - 1
            f_marketreturn_today = (f_marketprice_today / f_marketprice_yest) - 1
        
            # Event is found if the symbol is down more then 3% while the
            # market is up more then 2%
            if f_symreturn_today <= -0.04 and f_marketreturn_today >= 0.03:
                df_events[s_sym][ldt_timestamps[i]] = 1
                
            
       # df_events['BTC_AMP'][ldt_timestamps[2]] = 1
      #  print(df_events['BTC_AMP'][ldt_timestamps[2]])
    print('Success !')
    return df_events