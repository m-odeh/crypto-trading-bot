"""
Crypto Trading Bot
Custom strategy and Trailing stop loss

"""
import requests

from get_signal import *
import pandas as pd 
import time
import ccxt
from binance.client import Client
import datetime
import os.path 
from datetime import timedelta


pairs_list= ['BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'XRPUSDT', 'SOLUSDT',
'DOTUSDT', 'NEARUSDT', 'LINKUSDT', 'ATOMUSDT', 'ALGOUSDT',
'HBARUSDT', 'ICPUSDT', 'EGLDUSDT',
]


"""
pairs_list=['BTCUSDT','ETHUSDT','BNBUSDT','ADAUSDT',
'XRPUSDT','SOLUSDT','DOTUSDT','DOGEUSDT','TRXUSDT',
'AVAXUSDT','SHIBUSDT','LUNAUSDT','CROUSDT','LINKUSDT',
'MATICUSDT','LTCUSDT','FTTUSDT','NEARUSDT','XCNUSDT',
'XLMUSDT','TLMUSDT','XMRUSDT','ETCUSDT','ALGOUSDT',
'ATOMUSDT','FLOWUSDT','UNIUSDT','VETUSDT','XTZUSDT',
'TFUELUSDT','HBARUSDT','APEUSDT','SANDUSDT','KCSUSDT',
'AXSUSDT','FILUSDT','FRAXUSDT','VGXSDT','MANAUSDT',
'THETAUSDT','EGLDUSDT','AAVEUSDT','HEARTUSDT','EOSUSDT',
'HBTCUSDT','ZECUSDT','HNTUSDT','1INCHUSDT','HTUSDT',
'GRTUSDT','BTTUSDT','REQUSDT','APEUSDT','IOTAUSDT',
'SANDUSDT','LUNAUSDT','CRVUSDT','1INCHUSDT','UNIUSDT',
'GRTUSDT','TLMUSDT','REQUSDT','APEUSDT','IOTAUSDT',
'SANDUSDT','LUNAUSDT','CRVUSDT','1INCHUSDT','UNIUSDT',
'GRTUSDT','TLMUSDT','REQUSDT','APEUSDT','IOTAUSDT',
'SANDUSDT','LUNAUSDT','CRVUSDT','1INCHUSDT','UNIUSDT',
'GRTUSDT','TLMUSDT','REQUSDT','APEUSDT','IOTAUSDT',
'SANDUSDT','LUNAUSDT','CRVUSDT','1INCHUSDT','UNIUSDT',
'GRTUSDT','TLMUSDT','REQUSDT','APEUSDT','IOTAUSDT',
'GRTUSDT','TLMUSDT','REQUSDT','APEUSDT','IOTAUSDT']  """


#Bot Parameter Settings
paper_trading = True 
btc_24change_threshold = -5
trail=0.003
balance_usdt =  1000  # 1000 $ virtual starting balance
profit=0.005
wt_overbought=70  # Wave Trend Overbought threshold
wt_oversold= -20  # Wave Trend Oversold threshold


bot_status='buy' 
df_trades=pd.DataFrame()
new_candle_status= 'No'

#Set API Info
api_key='your_actual_api_key' 
api_secret='your_actual_secret'
client = Client(api_key, api_secret) 

key = "https://api.binance.com/api/v3/ticker/price?symbol="

exchange = ccxt.binance({
    'apiKey': api_key,
    'secret': api_secret,
    'enableRateLimit': True,}) 

file_status = os.path.exists('trades_log.csv')
if file_status is False:

    columns=['Time','signal type','Asset','Amount in coin ','Blance in USDT','Price','ATR','target price','stop loss','Profit','btc 24 change','stock_k']
    data_log = pd.DataFrame(columns=columns)
    data_log.columns = columns
    data_log.to_csv('trades_log.csv', mode='a', index=False, header=True)

            

# ct stores current time
ct = datetime.datetime.now()

#print("current time:-", ct)
minutes = ct.strftime('%M')

time_left_minute =  15 - int(minutes)  # time left till the new candle data / start of the bot 
time_left_second =  time_left_minute * 60
print('Time till next new candle = ',time_left_second)

#time.sleep(time_left_second)
print('stat now')


def generate_signals(pairs_list):

    coins=list()
    for pair in pairs_list:

        globals()[f"ohlc_{pair}"] =get_historical_ohlc_data(symbol=pair,interval='15m')
        globals()[f"ohlc_{pair}"]['open']=pd.to_numeric(globals()[f"ohlc_{pair}"]['open'], errors='coerce')
        globals()[f"ohlc_{pair}"]['high']=pd.to_numeric(globals()[f"ohlc_{pair}"]['high'], errors='coerce')
        globals()[f"ohlc_{pair}"]['low']=pd.to_numeric(globals()[f"ohlc_{pair}"]['low'], errors='coerce')
        globals()[f"ohlc_{pair}"]['close']=pd.to_numeric(globals()[f"ohlc_{pair}"]['close'], errors='coerce')
        globals()[f"ohlc_{pair}"]['volume']=pd.to_numeric(globals()[f"ohlc_{pair}"]['volume'], errors='coerce')

        globals()[f"ohlc_{pair}"]['EMA']=TA.EMA(globals()[f"ohlc_{pair}"],14)
        globals()[f"ohlc_{pair}"]['MFI']=TA.MFI(globals()[f"ohlc_{pair}"],14)
        #globals()[f"ohlc_{pair}"]['SAR']=TA.SAR(globals()[f"ohlc_{pair}"])
        #globals()[f"ohlc_{pair}"]['SQZMI']=TA.SQZMI(globals()[f"ohlc_{pair}"],14)
        globals()[f"ohlc_{pair}"]['RSI']=TA.RSI(globals()[f"ohlc_{pair}"],14)  #
        globals()[f"ohlc_{pair}"]['stock_k']=TA.STOCH(globals()[f"ohlc_{pair}"])
        globals()[f"ohlc_{pair}"]['stock_d']=TA.STOCHD(globals()[f"ohlc_{pair}"])
        #globals()[f"ohlc_{pair}"]['VAMA']=TA.VAMA(globals()[f"ohlc_{pair}"],14)
  
        
        wt_df=TA.WTO( globals()[f"ohlc_{pair}"],9,12)
        globals()[f"ohlc_{pair}"]['wt1']=wt_df['WT1.']  #white wave 
        globals()[f"ohlc_{pair}"]['wt2']=wt_df['WT2.']  # blue wave 
        globals()[f"ohlc_{pair}"]['ATR']=TA.ATR(globals()[f"ohlc_{pair}"])

        globals()[f"ohlc_{pair}"]['obv'] = TA.OBV(globals()[f"ohlc_{pair}"])
        obv_increasing = globals()[f"ohlc_{pair}"]['obv'] > globals()[f"ohlc_{pair}"]['obv'].shift(1)

        previous_wt1 = globals()[f"ohlc_{pair}"]['wt1'].shift(1)
        previous_wt2 = globals()[f"ohlc_{pair}"]['wt2'].shift(1)
        crossing_down = (globals()[f"ohlc_{pair}"]['wt1'] <= globals()[f"ohlc_{pair}"]['wt2']) & (previous_wt1 >= previous_wt2) & (globals()[f"ohlc_{pair}"]['wt2'] >= wt_overbought )
        crossing_up = (globals()[f"ohlc_{pair}"]['wt1'] >= globals()[f"ohlc_{pair}"]['wt2']) & (previous_wt1 <= previous_wt2) & (globals()[f"ohlc_{pair}"]['wt2'] <= wt_oversold )
        globals()[f"ohlc_{pair}"]['signal']=np.where(crossing_up & obv_increasing , 'buy',
            (np.where(crossing_down, 'sell', 'watch')))

        globals()[f"ohlc_{pair}"].dropna(inplace=True)
        globals()[f"ohlc_{pair}"].reset_index(drop=True, inplace=True)
        coins.append(globals()[f"ohlc_{pair}"])


def btc_24_status():
    global change_24
    tickers = client.get_ticker()
    
    for i in tickers:
    
        if i['symbol'] == 'BTCUSDT':
            btc_ticker = i
            change_24 =  float(i['priceChangePercent'])




while(True):

    ct = datetime.datetime.now()
    #print("current time:-", ct)
    minutes = ct.strftime('%M')

    #time in minute / 15 = reminder ,15-  ramainder = time left 
    time_passed_on_candle = int(minutes) % 15  # time past on last candle
    print('time_passed_on_candle = ' , time_passed_on_candle)

    time_left_minute = 15 - time_passed_on_candle # for 15 min candle  15
    #time_left_minute =  60 - int(minutes)  # time left till the new candle data / start of the bot 
    time_left_second =  time_left_minute * 60
    print('time_left_minute = ' , time_left_minute)
    print("\n" + "-" * 10)

    if  time_left_minute >= 14:

       
        print(" Getting new df data for candle at : " , datetime.datetime.now())
        generate_signals(pairs_list) 
        
        btc_24_status()
        print("BTC 24 change =",change_24 )

        for pair in pairs_list:
            df=globals()[f"ohlc_{pair}"] 
            df=df.drop(df.index[-1])
            
            #print(df.iloc[-2]['signal'])
            #if df['signal'][i]== 'buy':
            if (df.iloc[-1]['signal']== 'buy' ) & (time_left_minute >=14 ) :

                if change_24 > btc_24change_threshold : 

                    # buy
                    current_candle_date = datetime.datetime.now()
                    current_candle_date = current_candle_date.replace(second=0, microsecond=0)

                    df_trades = pd.concat([df_trades, df.iloc[[-1]]])
                    print(df.iloc[-1])
                    print("\n" + "-" * 10)

                    purchase_date = df.iloc[-1]['open_date_time']

                    ATR= df.iloc[-1]['ATR']
                    purchase_price = df.iloc[-1]['close']
                    profit_target = purchase_price + ( purchase_price * profit)
                    stop_loss= purchase_price -  2*ATR
                    trail_trigger = purchase_price +( purchase_price * trail )
                    ticker = df['symbol'].replace('USDT','/USDT')
                    buy_stock_k=df.iloc[-1]['stock_k']
                    buy_stock_d=df.iloc[-1]['stock_d']
                    old_stock_k = df.iloc[-1]['stock_k']
                    new_stock_k = old_stock_k


                    if paper_trading == True:
                        # ========= paper trading  ================
                        ordered_qt = balance_usdt / purchase_price
                        asset_bought = (df.iloc[-1]['symbol']).replace('USDT','')
                        bag = ordered_qt
                        # ========= End Paper trading ==============
                        
                    else:
                        # ============== Real Trading ==================
                        balance = exchange.fetch_balance()
                        balance_usdt = ( balance['total']['USDT'] ) 
                        amount = (balance_usdt/purchase_price) 
                        order = exchange.create_order(ticker, 'limit' , 'buy', amount, purchase_price)  
                        asset_bought=(df['symbol']).replace('USDT','')
                        time.sleep(3)
                        balance = exchange.fetch_balance()
                        bag= balance['free'][asset_bought]  
                        # ============== End Real Trading ==============


                    time.sleep(10)

                    # save to csv

                    data1 = {'Time':datetime.datetime.now(),'signal type': 'Buy' ,'Asset_bought': asset_bought,'Amount in coin ': bag ,
                             'Blance in USDT':balance_usdt ,'price' : purchase_price,'ATR':ATR ,'target price' : profit_target, 
                             'stop loss' : stop_loss , 'Profit':'***','btc 24 change': change_24, 'stock_k': df.iloc[-1]['stock_k'],
                             'signal':df.iloc[-1]['signal'] }
                             
                    data_log = pd.DataFrame(data1,index=[0])
                    data_log.to_csv('trades_log.csv', mode='a', index=False, header=False)
                    #print(bot_status)
                    bot_status = 'sell'
                    #print(bot_status)

                    start_time = datetime.datetime.now()
                    max_time = start_time + timedelta(hours=4)
                    max_time = max_time.hour


                    while(bot_status == 'sell'):

                        #try:

                            time_now = datetime.datetime.now()
                            url = key+pair
                            time.sleep(30)
                            data = requests.get(url)
                            data = data.json()
                            current_price = float(data['price'])

                            print('========================')
                            print('Time : ',time_now.hour,':',time_now.minute)
                            print('Asset Bought', asset_bought)
                            print('Start time', start_time)
                            print('Max time', max_time)
                            print('Purchase price', purchase_price)
                            print('Stop loss', stop_loss)
                            print('Target price', profit_target)
                            print('Trail trigger', trail_trigger)
                            print('current price', current_price)
                            time.sleep(10)

                            current_time = datetime.datetime.now()
                            current_time = current_time.hour

                            if current_price >= trail_trigger:
                                
                                trail_trigger = current_price + (current_price * trail)
                                stop_loss = current_price - (current_price * trail)

                            if (current_price <= stop_loss) or (current_time == max_time):
    
                                if paper_trading:
                                    # ========= Paper Trading Sell ================
                                    balance_usdt_new = bag * current_price 
                                    profit_perc = ((balance_usdt_new - balance_usdt) / balance_usdt) * 100
                                    balance_usdt = balance_usdt_new
                                    # ========= End Paper Trading ==============
                                else:
                                    # ========= Real Trading Sell ================
                                    order = exchange.create_order(ticker, 'market', 'sell', bag, current_price)
                                    time.sleep(3)
                                    balance = exchange.fetch_balance()
                                    balance_usdt_new = balance['total']['USDT']
                                    profit_perc = ((balance_usdt_new - balance_usdt) / balance_usdt) * 100
                                    balance_usdt = balance_usdt_new
                                    # ========= End Real Trading ==============
                                
                                # Logging (same for both modes)
                                data1 = {'Time':datetime.datetime.now(),'signal type': 'Sell' ,'Asset_sold': asset_bought, 
                                         'Amount in coin ': bag ,'Balance in USDT':balance_usdt_new, 'Price' : current_price,
                                         'ATR':ATR, 'target price' : profit_target, 'stop loss' : stop_loss,
                                         'Profit': profit_perc, 'btc 24 change': change_24}
                                
                                data_log = pd.DataFrame(data1, index=[0])
                                data_log.to_csv('trades_log.csv', mode='a', index=False, header=False)
                                
                                bot_status = 'buy'
                                print("bot status", bot_status)
                                break
                        #except:
                         #   print('Max retries exceeded error')
                    break

    else:
        time_now = datetime.datetime.now()
        print('new_candle_status= No ')
        print('Time : ' , time_now)
        time.sleep(time_left_second)


