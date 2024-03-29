import ccxt
import pandas as pd
import numpy as np
from datetime import datetime
import time
import pandas as pd

today = str(datetime.now())
today = today.split(" ")[0].replace("-", "")

def fetch_funding_rate(symbol, market, unix_start, unix_end):
    output = []
    query_from = unix_start
    query_to = unix_end
    prev_query_from = query_from
    while query_from < unix_end:
        data = market.fetchFundingRateHistory(symbol, limit=1000, since=query_from, 
                                                params={'endTime': query_to})
        output.extend(data)
        t = pd.DataFrame(data)
        query_from = t['timestamp'].max()
        if prev_query_from == query_from: break
        prev_query_from = query_from
    df = pd.DataFrame(output)
    df = df.sort_values('timestamp')
    df.drop_duplicates(subset = ['timestamp'],inplace=True)
    return df


def unix_convert(start, end):
    # convert datetime string to unix timestamp
    str_start = str(start)
    dt = datetime.strptime(str_start, '%Y%m%d')  # parse the date from string
    unix_start = int(time.mktime(dt.timetuple())) * 1000 # convert to Unix timestamp
    str_end = str(end)
    dt = datetime.strptime(str_end, '%Y%m%d')  # parse the date from string
    unix_end = int(time.mktime(dt.timetuple())) * 1000 + 64800000# convert to Unix timestamp
    return unix_start, unix_end


def pagination_funding_rate(symbol, start, end):
    binance = ccxt.binanceusdm()
    bybit = ccxt.bybit()
    okx = ccxt.okx()
    
    unix_start, unix_end = unix_convert(start, end)
    
    # fetch funding rate for three market, note that bybit can only auto load two months data
    df_binance = fetch_funding_rate(symbol, binance, unix_start, unix_end)
    
    df_bybit_1 = fetch_funding_rate(symbol, bybit, unix_start, unix_end)
    bybit_earliest = min(df_binance['datetime']).split("T")[0].replace("-", "")
    bybit_latest = min(df_bybit_1['datetime']).split("T")[0].replace("-", "")
    bybit_new_start, bybit_new_end = unix_convert(bybit_earliest, bybit_latest)
    df_bybit_2 = fetch_funding_rate(symbol, bybit, bybit_new_start, bybit_new_end)
    df_bybit = pd.concat([df_bybit_1, df_bybit_2], ignore_index=True, sort=False)
    df_bybit.drop_duplicates(subset = ['timestamp'],inplace=True)
    df_bybit = df_bybit.sort_values(by='timestamp', ascending=True).reindex()
    
    df_okx = fetch_funding_rate(symbol, okx, unix_start, unix_end)
    
    # merge dataframe for binance, bybit and okx platforms
    df_okx.rename(columns={'fundingRate': 'okx_fundingRate'}, inplace=True)
    df_bybit.rename(columns={'fundingRate': 'bybit_fundingRate'}, inplace=True)
    df_binance.rename(columns={'fundingRate': 'binance_fundingRate'}, inplace=True)
    df_binance['timestamp'] = df_binance['timestamp'].apply(lambda x: round(x, -3))
    
    # merge dataframes for three markets into one
    df_binance = df_binance.merge(df_bybit[['timestamp', 'bybit_fundingRate']], on='timestamp', how='left')
    df_binance = df_binance.merge(df_okx[['timestamp', 'okx_fundingRate']], on='timestamp', how='left')
    df_binance = df_binance[['symbol', 'timestamp', 'datetime', 'okx_fundingRate', 
                    'binance_fundingRate', 'bybit_fundingRate']]
    return df_binance

def pagination_funding_rate_net_SMA(symbol, start, end, long_okx=True):
    okx_df = pagination_funding_rate(symbol, start, end)
    
    def SMA(values, n):
        return pd.Series(values).rolling(n).mean()
    
    okx_df['binance 30d SMA'] = SMA(okx_df['binance_fundingRate'], 30 * 3)
    okx_df['binance 14d SMA'] = SMA(okx_df['binance_fundingRate'], 14 * 3)
    okx_df['binance 7d SMA'] = SMA(okx_df['binance_fundingRate'], 7 * 3)
    okx_df['binance 3d SMA'] = SMA(okx_df['binance_fundingRate'], 3 * 3)

    okx_df['bybit 30d SMA'] = SMA(okx_df['bybit_fundingRate'], 30 * 3)
    okx_df['bybit 14d SMA'] = SMA(okx_df['bybit_fundingRate'], 14 * 3)
    okx_df['bybit 7d SMA'] = SMA(okx_df['bybit_fundingRate'], 7 * 3)
    okx_df['bybit 3d SMA'] = SMA(okx_df['bybit_fundingRate'], 3 * 3)

    okx_df['okx 30d SMA'] = SMA(okx_df['okx_fundingRate'], 30 * 3)
    okx_df['okx 14d SMA'] = SMA(okx_df['okx_fundingRate'], 14 * 3)
    okx_df['okx 7d SMA'] = SMA(okx_df['okx_fundingRate'], 7 * 3)
    okx_df['okx 3d SMA'] = SMA(okx_df['okx_fundingRate'], 3 * 3)
    
    if long_okx == True:
        okx_df['Long OKX Short Binance 30d Net SMA'] = (okx_df['binance 30d SMA'] - \
                                                      okx_df['okx 30d SMA']).copy() * 3 * 365
        okx_df['Long OKX Short Binance 14d Net SMA'] = (okx_df['binance 14d SMA'] - \
                                                      okx_df['okx 14d SMA']).copy() * 3 * 365
        okx_df['Long OKX Short Binance 7d Net SMA'] = (okx_df['binance 7d SMA'] - \
                                                      okx_df['okx 7d SMA']).copy() * 3 * 365
        okx_df['Long OKX Short Binance 3d Net SMA'] = (okx_df['binance 3d SMA'] - \
                                                      okx_df['okx 3d SMA']).copy() * 3 * 365
        okx_df['Long OKX Short Bybit 30d Net SMA'] = (okx_df['bybit 30d SMA'] - \
                                                      okx_df['okx 30d SMA']).copy() * 3 * 365
        okx_df['Long OKX Short Bybit 14d Net SMA'] = (okx_df['bybit 14d SMA'] - \
                                                      okx_df['okx 14d SMA']).copy() * 3 * 365
        okx_df['Long OKX Short Bybit 7d Net SMA'] = (okx_df['bybit 7d SMA'] - \
                                                      okx_df['okx 7d SMA']).copy() * 3 * 365
        okx_df['Long OKX Short Bybit 3d Net SMA'] = (okx_df['bybit 3d SMA'] - \
                                                      okx_df['okx 3d SMA']).copy() * 3 * 365
    else:
        okx_df['Short OKX Long Binance 30d Net SMA'] = (-okx_df['binance 30d SMA'] + \
                                                      okx_df['okx 30d SMA']).copy() * 3 * 365
        okx_df['Short OKX Long Binance 14d Net SMA'] = (-okx_df['binance 14d SMA'] + \
                                                      okx_df['okx 14d SMA']).copy() * 3 * 365
        okx_df['Short OKX Long Binance 7d Net SMA'] = (-okx_df['binance 7d SMA'] + \
                                                      okx_df['okx 7d SMA']).copy() * 3 * 365
        okx_df['Short OKX Long Binance 3d Net SMA'] = (-okx_df['binance 3d SMA'] + \
                                                      okx_df['okx 3d SMA']).copy() * 3 * 365
        okx_df['Short OKX Long Bybit 30d Net SMA'] = (-okx_df['bybit 30d SMA'] + \
                                                      okx_df['okx 30d SMA']).copy() * 3 * 365
        okx_df['Short OKX Long Bybit 14d Net SMA'] = (-okx_df['bybit 14d SMA'] + \
                                                      okx_df['okx 14d SMA']).copy() * 3 * 365
        okx_df['Short OKX Long Bybit 7d Net SMA'] = (-okx_df['bybit 7d SMA'] + \
                                                      okx_df['okx 7d SMA']).copy() * 3 * 365
        okx_df['Short OKX Long Bybit 3d Net SMA'] = (-okx_df['bybit 3d SMA'] + \
                                                      okx_df['okx 3d SMA']).copy() * 3 * 365
        
    okx_df.drop(okx_df.columns[[i for i in range(6, 18)]], axis=1, inplace=True)
    okx_df['okx_fundingRate'] = okx_df['okx_fundingRate'] * 3 * 365
    okx_df['binance_fundingRate'] = okx_df['binance_fundingRate'] * 3 * 365
    okx_df['bybit_fundingRate'] = okx_df['bybit_fundingRate'] * 3 * 365

    return okx_df
    