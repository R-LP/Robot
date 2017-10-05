# -*- coding: utf-8 -*-
"""
Created on Thu Oct  5 18:02:40 2017

@author: Roger
"""

#%%
import event_profiler2 as e_p2
import imp
imp.reload(e_p2)
import get_totalMarketCap
import pandas as pd

data = e_p2.get_data()
benchmark = get_totalMarketCap.get_totalMarketCap()

#%%

data = data.iloc[:round(len(data.index)/2)]

#%%
data2 = data.resample('D').mean()
data2.index = pd.to_datetime(data2.index)

returns = data2.pct_change()
returns = returns.replace(inf, nan)
expected_returns = returns.add(1).prod()

corr = returns.corr(method='pearson')

volatility = returns.std()

start = data2.index[0]
end = data2.index[-1]


loc_start = benchmark.index.get_loc(start, method='nearest')
loc_end = benchmark.index.get_loc(end, method='pad')

return_bench = (benchmark.iloc[loc_end,0]/benchmark.iloc[loc_start,0]) - 1
 
target_returns = return_bench * 1.20

#%%

