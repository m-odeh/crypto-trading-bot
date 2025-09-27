import pandas as pd
from finta import TA
#import pandas_ta as TA
from binance.client import Client
import numpy as np
import datetime as dt

client=Client()

def get_historical_ohlc_data(symbol,past_days=None,interval=None):
    
    #Returns historcal klines from past for given symbol and interval
    #past_days: how many days back one wants to download the data
    
    if not interval:
        interval='1h' # default interval 1 hour
    if not past_days:
        past_days=30  # default past days 30.

    start_str=str((pd.to_datetime('today')-pd.Timedelta(str(past_days)+' days')).date())
    symbol=symbol
    #print('symbol =', symbol )
    #columns=['open_time','open', 'high', 'low', 'close', 'volume', 'close_time', 'qav', 'num_trades', 'taker_base_vol', 'taker_quote_vol','is_best_match']
    D=pd.DataFrame(client.get_historical_klines(symbol=symbol,start_str=start_str,interval=interval))
    #print(symbol)
    D=D.reset_index(drop=True)
    D.columns=['open_time','open', 'high', 'low', 'close', 'volume', 'close_time', 'qav', 'num_trades', 'taker_base_vol', 'taker_quote_vol','is_best_match']
    D['open_date_time']=[dt.datetime.fromtimestamp(x/1000) for x in D.open_time]
    D['symbol']=symbol
    D=D[['symbol','open_date_time','open', 'high', 'low', 'close', 'volume', 'num_trades', 'taker_base_vol', 'taker_quote_vol']]

    return D

def get_latest_ohlc_data(symbol):
    
    symbol=symbol
    #print('symbol =', symbol )

    # since it is 60 min, 2 candle 30 min based is the output, last one is the current not close candle and the old one is the confirmed
    #kernal interval is candle/bar time period ie:5 min, 30 min 
    # next option: "10 minutes ago utc"  : get how many candle to look back and retrieve .... changing this = change 
    klines = client.get_historical_klines(symbol, Client.KLINE_INTERVAL_15MINUTE, "30 minutes ago UTC") 
    
    D1=pd.DataFrame(klines)
    D1=D1.reset_index(drop=True)
    D1.columns=['open_time','open', 'high', 'low', 'close', 'volume', 'close_time', 'qav', 'num_trades', 'taker_base_vol', 'taker_quote_vol','is_best_match']
    D1['open_date_time']=[dt.datetime.fromtimestamp(x/1000) for x in D1.open_time]
    D1['symbol']=symbol
    D1=D1[['symbol','open_date_time','open', 'high', 'low', 'close', 'volume', 'num_trades', 'taker_base_vol', 'taker_quote_vol']]

    return D1
