import ccxt
import pandas as pd
import numpy as np
from datetime import datetime
import time
import pandas as pd

today = str(datetime.now())
today = today.split(" ")[0].replace("-", "")

def pagination_funding_rate(symbol, start, end):
    busdm = ccxt.binanceusdm()
    bybit = ccxt.bybit()
    okx = ccxt.okx()
    
    # convert datetime string to unix timestamp
    str_start = str(start)
    dt = datetime.strptime(str_start, '%Y%m%d')  # parse the date from string
    unix_start = int(time.mktime(dt.timetuple())) * 1000 # convert to Unix timestamp
    str_end = str(end)
    dt = datetime.strptime(str_end, '%Y%m%d')  # parse the date from string
    unix_end = int(time.mktime(dt.timetuple())) * 1000 + 64800000# convert to Unix timestamp
    
    # fetch binance funding rate
    output_bn = []
    query_from = unix_start
    query_to = unix_end
    prev_query_from = query_from
    while query_from < unix_end:
        data_bn = busdm.fetchFundingRateHistory(symbol, limit=1000, since=query_from, 
                                                params={'endTime': query_to})
        output_bn.extend(data_bn)
        t = pd.DataFrame(data_bn)
        query_from = t['timestamp'].max()
        if prev_query_from == query_from: break
        prev_query_from = query_from
    df_bn = pd.DataFrame(output_bn)
    df_bn = df_bn.sort_values('timestamp')
    df_bn.drop_duplicates(subset = ['timestamp'],inplace=True)
    
    # fetch bybit funding rate
    output_bb = []
    query_from = unix_start
    query_to = unix_end
    prev_query_from = query_from
    while query_from < unix_end:
        data_bb = bybit.fetchFundingRateHistory(symbol, limit=1000, since=query_from, 
                                                params={'endTime': query_to})
        output_bb.extend(data_bb)
        t = pd.DataFrame(data_bb)
        query_from = t['timestamp'].max()
        if prev_query_from == query_from: break
        prev_query_from = query_from
    df_bb = pd.DataFrame(output_bb)
    df_bb = df_bb.sort_values('timestamp')
    df_bb.drop_duplicates(subset = ['timestamp'],inplace=True)
    
    # fetch okx funding rate
    output_okx = []
    query_from = unix_start
    query_to = unix_end
    prev_query_from = query_from
    while query_from < unix_end:
        data_okx = okx.fetchFundingRateHistory(symbol, limit=1000, since=query_from, 
                                               params={'endTime': query_to})
        output_okx.extend(data_okx)
        t = pd.DataFrame(data_okx)
        query_from = t['timestamp'].max()
        if prev_query_from == query_from: break
        prev_query_from = query_from
    df_okx = pd.DataFrame(output_okx)
    df_okx = df_okx.sort_values('timestamp')
    df_okx.drop_duplicates(subset = ['timestamp'],inplace=True)
    
    # merge dataframe for binance, bybit and okx platforms
    df_okx.rename(columns={'fundingRate': 'okx_fundingRate'}, inplace=True)
    df_bb.rename(columns={'fundingRate': 'bybit_fundingRate'}, inplace=True)
    df_bn.rename(columns={'fundingRate': 'binance_fundingRate'}, inplace=True)
    df_bn['timestamp'] = df_bn['timestamp'].apply(lambda x: round(x, -3))
    
    col_num = min(len(df_bb), len(df_okx), len(df_bn))
    df_bn = df_bn.iloc[-col_num:]
    df_bn.reset_index(inplace=True)
    df_bb = df_bb.iloc[-col_num:]
    df_bb.reset_index(inplace=True)
    df_okx = df_okx.iloc[-col_num:]
    df_okx.reset_index(inplace=True)
    
    if df_bn['timestamp'].equals(df_bb['timestamp']) and \
       df_bn['timestamp'].equals(df_okx['timestamp']):
        df_okx = df_okx.join(df_bn['binance_fundingRate'])
        df_okx = df_okx.join(df_bb['bybit_fundingRate'])
        print('Merge Success')
    else:
        raise ValueError('Merge failed with initial end date, need to extend an extra day')
        # print('Merge failed with initial end date, now extending an extra day')
        # revised_end = datetime.strptime(today, '%Y%m%d')
        # revised_end += timedelta(days=1)
        # revised_end = str(revised_end)
        # revised_end = revised_end.split(" ")[0].replace("-", "")
        # df = pagination_funding_rate(symbol, start, revised_end)
        # df = df[['symbol', 'timestamp', 'datetime', 'okx_fundingRate', 
        #              'binance_fundingRate', 'bybit_fundingRate']] 
        # return df  
        
    df_okx = df_okx[['symbol', 'timestamp', 'datetime', 'okx_fundingRate', 
                     'binance_fundingRate', 'bybit_fundingRate']]    
    return df_okx


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
                                                      okx_df['okx 30d SMA']).copy()
        okx_df['Long OKX Short Binance 14d Net SMA'] = (okx_df['binance 14d SMA'] - \
                                                      okx_df['okx 14d SMA']).copy()
        okx_df['Long OKX Short Binance 7d Net SMA'] = (okx_df['binance 7d SMA'] - \
                                                      okx_df['okx 7d SMA']).copy()
        okx_df['Long OKX Short Binance 3d Net SMA'] = (okx_df['binance 3d SMA'] - \
                                                      okx_df['okx 3d SMA']).copy()
        okx_df['Long OKX Short Bybit 30d Net SMA'] = (okx_df['bybit 30d SMA'] - \
                                                      okx_df['okx 30d SMA']).copy()
        okx_df['Long OKX Short Bybit 14d Net SMA'] = (okx_df['bybit 14d SMA'] - \
                                                      okx_df['okx 14d SMA']).copy()
        okx_df['Long OKX Short Bybit 7d Net SMA'] = (okx_df['bybit 7d SMA'] - \
                                                      okx_df['okx 7d SMA']).copy()
        okx_df['Long OKX Short Bybit 3d Net SMA'] = (okx_df['bybit 3d SMA'] - \
                                                      okx_df['okx 3d SMA']).copy()
    else:
        okx_df['Short OKX Long Binance 30d Net SMA'] = (-okx_df['binance 30d SMA'] + \
                                                      okx_df['okx 30d SMA']).copy()
        okx_df['Short OKX Long Binance 14d Net SMA'] = (-okx_df['binance 14d SMA'] + \
                                                      okx_df['okx 14d SMA']).copy()
        okx_df['Short OKX Long Binance 7d Net SMA'] = (-okx_df['binance 7d SMA'] + \
                                                      okx_df['okx 7d SMA']).copy()
        okx_df['Short OKX Long Binance 3d Net SMA'] = (-okx_df['binance 3d SMA'] + \
                                                      okx_df['okx 3d SMA']).copy()
        okx_df['Short OKX Long Bybit 30d Net SMA'] = (-okx_df['bybit 30d SMA'] + \
                                                      okx_df['okx 30d SMA']).copy()
        okx_df['Short OKX Long Bybit 14d Net SMA'] = (-okx_df['bybit 14d SMA'] + \
                                                      okx_df['okx 14d SMA']).copy()
        okx_df['Short OKX Long Bybit 7d Net SMA'] = (-okx_df['bybit 7d SMA'] + \
                                                      okx_df['okx 7d SMA']).copy()
        okx_df['Short OKX Long Bybit 3d Net SMA'] = (-okx_df['bybit 3d SMA'] + \
                                                      okx_df['okx 3d SMA']).copy()
        
    okx_df.drop(okx_df.columns[[i for i in range(6, 18)]], axis=1, inplace=True)
    okx_df.dropna(inplace=True)

    return okx_df

# def bulk_query(start, end, symbols, long_okx=True, net_SMA=False):
#     dataframes = []
#     for i in range(1, len(symbols) + 1):
#         dataframe_name = 'df' + str(i)
#         if net_SMA == False:
#             dataframe_name = pagination_funding_rate(symbols[i - 1], start, end).copy()
#         else:
#             dataframe_name = pagination_funding_rate_net_SMA(symbols[i - 1], start, end).copy()
#         dataframes.append(dataframe_name)
#     return dataframes