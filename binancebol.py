import pandas as pd
import datetime as dt
from binance.client import Client
import time
import numpy
import requests

import winsound

filename = 'alert_sound.wav'




while True:
    try:
        client = Client()

        symbo1_trade='BTCUSDT'

        length=20
        width=2
    except:
        print("Binance Client error")
    def bollingerband(symbol, bandunit, intervalunit, interval):

        if intervalunit=='3T' or intervalunit=='30T' or intervalunit=='1T':
           start_str='500 minutes ago UTC'
           interval_data='1m'


        if intervalunit=='1H' or intervalunit=='3H' or intervalunit=='1D':
           start_str='500 hours ago UTC'
           interval_data='1h'

        if intervalunit=='1W':
           start_str='500 days ago UTC'
           interval_data='1d'

        if intervalunit!='1MON  TH': 
            D = pd.DataFrame(
                client.get_historical_klines(symbol=symbol, start_str=start_str, interval=interval_data))
            D.columns = ['open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'qav', 'num_trades',
                         'taker_base_vol', 'taker_quote_vol', 'is_best_match']
            D['open_date_time'] = [dt.datetime.fromtimestamp(x / 1000) for x in D.open_time]
            D['symbol'] = symbol
            D = D[['symbol', 'open_date_time', 'open', 'high', 'low', 'close', 'volume', 'num_trades', 'taker_base_vol',
                   'taker_quote_vol']]


        if intervalunit=='1MONTH':
           intervalunit='M'

           D = pd.DataFrame(
                client.get_historical_klines("BTCUSDT", Client.KLINE_INTERVAL_1MONTH, "1 Jan, 2017"))
           D.columns = ['open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'qav', 'num_trades',
                         'taker_base_vol', 'taker_quote_vol', 'is_best_match']
           D['open_date_time'] = [dt.datetime.fromtimestamp(x / 1000) for x in D.open_time]
           D['symbol'] = symbol
           D = D[['symbol', 'open_date_time', 'open', 'high', 'low', 'close', 'volume', 'num_trades', 'taker_base_vol',
                   'taker_quote_vol']]


        df = D.set_index("open_date_time")

        df['close'] = df['close'].astype(float)

        df = df['close']


        df1 = df.resample(intervalunit).agg({

            "close": "last"
        })



        unit = bandunit

        band1 = unit * numpy.std(df1['close'][len(df1) - interval:len(df1)])

        bb_center = numpy.mean(df1['close'][len(df1) - interval:len(df1)])

        band_high = bb_center + band1

        band_low = bb_center - band1

        return band_high, bb_center , band_low
    try:
        bb_1m=bollingerband(symbo1_trade, width , '1T',length)


        print('1 minute high center low: ', bb_1m)    
        marketprice='https://api.binance.com/api/v1/ticker/24hr?symbol='+symbo1_trade
        res = requests.get(marketprice)
        data = res.json()
        lastprice=data['lastPrice']

        print('Last Price: ',lastprice)

        if float(lastprice) > bb_1m[0] :
            print("볼린져밴드 상단돌파")
            winsound.PlaySound(filename, winsound.SND_FILENAME)

            time.sleep(60)
        if bb_1m[2] > float(lastprice):
            print("볼린져밴드 하단돌파")
            winsound.PlaySound(filename, winsound.SND_FILENAME)
            time.sleep(60)
        
        time.sleep(1)
    except:
        print("Timeout error")
