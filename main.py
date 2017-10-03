# -*- coding: utf-8 -*-
"""
Created on Tue Sep 26 14:54:12 2017

@author: Roger
"""

import pandas as pd
import numpy as np
from multiprocessing import Process
#%%


#%%

#%%

def main():
    def MM_strategie(shortWindow, longWindow, df2):
        
        signals = pd.DataFrame(index=df2.index)
        signals['signal'] = 0.0
        signals['short_mvg']=df2['close'].rolling(window=shortWindow, min_periods=1).mean()
        signals['long_mvg']=df2['close'].rolling(window=longWindow, min_periods=1).mean()
        signals['signal'][longWindow:] = np.where(signals['short_mvg'][longWindow:] >
                                                  signals['long_mvg'][longWindow:], 1.0, 0.0)
        signals['position'] = signals['signal'].diff()
        
        initial_capital = 100.0
        positions = pd.DataFrame(index=signals.index).fillna(0.0)
        positions['ETH'] = 100 * signals['signal']
        portfolio = positions.multiply(df2.close, axis=0)
        pos_diff = positions.diff()
        portfolio['holdings'] = (positions.multiply(df2.close, axis = 0))
        portfolio['cash'] = initial_capital - (pos_diff.multiply(df2.close, axis = 0)).cumsum()
        portfolio['total'] = portfolio['cash'] + portfolio['holdings']
        portfolio['returns'] = portfolio['total'].pct_change().cumsum()
        
        return(portfolio['returns'])
    
    ##%%
    #import return_chart as r_c
    #from datetime import date 
    #
    #end = date(2016, 12, 31)
    #start = date(2016, 1, 1)
    #
    #data = r_c.return_chart('BTC_ETH', start, end)
    #df = pd.DataFrame(data)
    #date_pd = pd.to_datetime(df['date'], unit='s')
    #df = df.set_index(date_pd)
    #df.to_csv('2016_BTC_ETH.csv')
    
    #%%    
    df2 = pd.read_csv('2016_BTC_ETH.csv')
    
    
    #%%
    max_returns={'value':0, 'shortWindow':0, 'longWindow':0}
    
    shortWindowMax = 1080
    longWindowMax = 1080
    se = []
    
    
    for i in range(1, longWindowMax+1):
        print(i)
        longWindow = i
        for j in range(1, shortWindowMax+1):
            shortWindow = j
            returns = MM_strategie(shortWindow, longWindow, df2)
            returns = returns.iloc[len(returns)-1]
            
            se.append([shortWindow,longWindow, returns])
        
            if (returns > max_returns['value']):
                max_returns['value'] = returns
                max_returns['shortWindow'] = shortWindow
                max_returns['longWindow'] = longWindow
                print(max_returns)
    #%%
