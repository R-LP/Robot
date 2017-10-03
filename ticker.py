# -*- coding: utf-8 -*-
"""
Created on Tue Sep 26 15:14:58 2017

@author: Roger
"""

import urllib
import json
import datetime

def getTicker():
    currentTime = datetime.datetime.now()
    urlTicker = urllib.request.urlopen('https://poloniex.com/public?command=returnTicker')
    rawTicker = urlTicker.read()
    data = json.loads(rawTicker)
    return {'currentTime':currentTime, 'quote':data} 

