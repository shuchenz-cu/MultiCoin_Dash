import pandas as pd
from datetime import timedelta
import streamlit as st
from MultiCoin_FR import pagination_funding_rate_net_SMA, pagination_funding_rate
from datetime import datetime


##################################################  Parameters ##################################################

# List of symbols:
symbols = ['BTC/USDT:USDT', 'ETH/USDT:USDT', 'SOL/USDT:USDT', 'XRP/USDT:USDT', 'DOGE/USDT:USDT',
           'COMP/USDT:USDT', 'MATIC/USDT:USDT', 'DOT/USDT:USDT', 'GMT/USDT:USDT', 
           'LINK/USDT:USDT', 'BCH/USDT:USDT', 'KNC/USDT:USDT', 'XLM/USDT:USDT', 'OP/USDT:USDT', 
           'LTC/USDT:USDT', 'MKR/USDT:USDT', 'ADA/USDT:USDT', 'AVAX/USDT:USDT', 'APE/USDT:USDT', 
           'FTM/USDT:USDT', 'SUI/USDT:USDT', 'ARB/USDT:USDT', 'BNB/USDT:USDT', 'THETA/USDT:USDT', 
           'SNX/USDT:USDT', 'APT/USDT:USDT', 'ATOM/USDT:USDT', 'MASK/USDT:USDT', 'GALA/USDT:USDT',
           'NEAR/USDT:USDT', 'EOS/USDT:USDT', 'ZEN/USDT:USDT', 'DYDX/USDT:USDT',  'LDO/USDT:USDT',
           'SAND/USDT:USDT', 'ETC/USDT:USDT', 'AAVE/USDT:USDT', 'CFX/USDT:USDT']

# Prepare data for the selected coin
current = datetime.now()
today = str(current)
today = today.split(" ")[0].replace("-", "")
three_months_ago = current - timedelta(days=3 * 30)
three_months_ago = str(three_months_ago)
three_months_ago = three_months_ago.split(" ")[0].replace("-", "")


##################################################  Helper Functions  ##################################################
def bulk_query(start, end, symbols, long_okx, net_SMA):
    dataframes = []
    for i in range(1, len(symbols) + 1):
        placeholder = st.empty()
        with placeholder.container():
            st.write("Now getting data for",symbols[i - 1],"Retrieving data", i, "/", len(symbols))
        dataframe_name = 'df' + str(i)
        if net_SMA == False: 
            dataframe_name = pagination_funding_rate(symbols[i - 1], start, end).copy()
        else:
            dataframe_name = pagination_funding_rate_net_SMA(symbols[i - 1], start, end).copy()
        dataframes.append(dataframe_name)
        placeholder.empty()
    return dataframes

# Retrieving funding rate and sma data for the multiple given symbol
def get_data(net_SMA):
    data = ''
    try:
        data = bulk_query(three_months_ago, today, symbols, long_okx=True, net_SMA=True)
        df_0 = data[0]
        for idx in range(1, len(data)):
            df_0 = pd.concat([df_0, data[idx]], ignore_index=True, sort=False)
        return df_0
    except:
        revised_end = datetime.strptime(today, '%Y%m%d')
        revised_end += timedelta(days=1)
        revised_end = str(revised_end)
        revised_end = revised_end.split(" ")[0].replace("-", "")
        data = bulk_query(three_months_ago, revised_end, symbols)
        
def download_csv():
    data = get_data(net_SMA=True)
    data.to_csv('recent_three_months_data.csv')