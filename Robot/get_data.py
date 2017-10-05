# -*- coding: utf-8 -*-
"""
Created on Tue Sep 26 15:16:35 2017

@author: Roger
"""

import ticker
import pandas as pd
import return_chart as r_c
from datetime import date 

#%%
end = date(2017, 9, 26)
start = date(2016, 1, 1)

#%%
ticker = ticker.getTicker()
quotes = ticker['quote']
df = pd.DataFrame(quotes)
list_of_currency_pairs=df.columns

#%%

for i in list_of_currency_pairs:
    data = r_c.return_chart(i, start, end)
    df = pd.DataFrame(data)
    date_pd = pd.to_datetime(df['date'], unit='s')
    df = df.set_index(date_pd)
    df.to_csv(i+'.csv')
    