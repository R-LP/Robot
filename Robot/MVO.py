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
data = data.dropna(how='all', axis=1)

#%%
data2 = data.resample('D').mean()

returns = data2.pct_change()

#%%
returns = returns.replace(inf, nan)
expected_returns = returns.add(1).prod()

k = 365

mean_returns = returns.mean()
cov_matrix = returns.cov()

volatility = returns.std()

start = data.index[0]
end = data.index[-1]
loc_start = benchmark.index.get_loc(start, method='nearest')
loc_end = benchmark.index.get_loc(end, method='pad')
return_bench = (benchmark.iloc[loc_end,0]/benchmark.iloc[loc_start,0]) - 1
 
target_returns = return_bench * 1.20

#%%
import numpy as np
import matplotlib.pyplot as plt

num_portfolios = 500000
 
#set up array to hold results
results = np.zeros((3+len(returns.columns),num_portfolios))
 
 
for i in range(num_portfolios):
    #select random weights for portfolio holdings
    weights = np.random.random(len(returns.columns))
    #rebalance weights to sum to 1
    weights /= np.sum(weights)
 
    #calculate portfolio return and volatility
    portfolio_return = np.sum(mean_returns * weights) * k
    portfolio_std_dev = np.sqrt(np.dot(weights.T,np.dot(cov_matrix, weights))) * np.sqrt(k)
 
    #store results in results array
    results[0,i] = portfolio_return 
    results[1,i] = portfolio_std_dev
    #store Sharpe Ratio (return / volatility) - risk free rate element excluded for simplicity
    results[2,i] = results[0,i] / results[1,i]
    #store the weights of each crypto
    results[3:,i] = weights
 
#convert results array to Pandas DataFrame
results_frame = pd.DataFrame(results.T, 
                             columns = ['ret','stdev','sharpe'] + list(returns))

#locate position of portfolio with highest Sharpe Ratio
max_sharpe_port = results_frame.iloc[results_frame['sharpe'].idxmax()]
#locate positon of portfolio with minimum standard deviation
min_vol_port = results_frame.iloc[results_frame['stdev'].idxmin()]

#create scatter plot coloured by Sharpe Ratio
fig = plt.plot()
plt.scatter(results_frame.stdev,results_frame.ret,c=results_frame.sharpe,cmap='RdYlGn')
plt.xlabel('Volatility')
plt.ylabel('Returns')
plt.colorbar()

#plot red star to highlight position of portfolio with highest Sharpe Ratio
plt.scatter(max_sharpe_port[1],max_sharpe_port[0],marker=(5,1,0),color='r',s=1000)
#plot green star to highlight position of minimum variance portfolio
plt.scatter(min_vol_port[1],min_vol_port[0],marker=(5,1,0),color='g',s=1000)


plt.show()