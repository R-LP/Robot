# -*- coding: utf-8 -*-
"""
Created on Thu Oct  5 11:37:22 2017

@author: Roger
"""
#%%

import event_profiler2 as e_p2
import imp
imp.reload(e_p2)
import get_totalMarketCap

data = e_p2.get_data(name='BTC_MAID')
benchmark = get_totalMarketCap.get_totalMarketCap()

#%%
import pandas as pd
returns = pd.DataFrame()
returns['benchmark'] = (
        benchmark['market_cap_($)'] / benchmark['market_cap_($)'].shift(1)) -1
        
returns['data'] = (data / data.shift(1)) - 1
returns = returns.fillna(0)
returns = returns.drop(returns.index[0])

x1 = returns['data'].values
y = returns['benchmark'].values


#%%

import statsmodels.api as sm

X = sm.add_constant(x1)
model = sm.OLS(y, X).fit()
predictions = model.predict(X)
model.summary()

#%%
from matplotlib import pyplot as plt
plt.plot(x1,y, 'r.')
ax = plt.axis()


## Initialize `x`
x = np.linspace(ax[0], ax[1] + 0.01)
#
## Plot the regression line
plt.plot(x, model.params[0] + model.params[1] * x, 'b', lw=2)
#
## Customize the plot
plt.grid(True)
plt.axis('tight')
plt.xlabel('Data')
plt.ylabel('Market')

# Show the plot
plt.show()