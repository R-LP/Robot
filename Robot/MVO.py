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

data = e_p2.get_data()
benchmark = get_totalMarketCap.get_totalMarketCap()

#%%
data2 = data.resample('D').mean()

returns = data2.pct_change()


corr = returns.corr(method='pearson')

test = returns.fillna(0.0)
test.std()