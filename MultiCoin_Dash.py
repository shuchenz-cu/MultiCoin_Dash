import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
from datetime import timedelta
from MultiCoin_FR import pagination_funding_rate_net_SMA, pagination_funding_rate
from datetime import datetime
##################################################  Parameters ##################################################

### Tags
okx_binance_net_sma = ['Long OKX Short Binance 30d Net SMA', 'Long OKX Short Binance 14d Net SMA',
                        'Long OKX Short Binance 7d Net SMA', 'Long OKX Short Binance 3d Net SMA']
okx_bybit_net_sma = ['Long OKX Short Bybit 30d Net SMA', 'Long OKX Short Bybit 14d Net SMA',
                    'Long OKX Short Bybit 7d Net SMA', 'Long OKX Short Bybit 3d Net SMA']
funding_rate = ['okx_fundingRate', 'binance_fundingRate', 'bybit_fundingRate']
### List of symbols
symbols = ['BTC/USDT:USDT', 'XRP/USDT:USDT', 'SOL/USDT:USDT', 'DOT/USDT:USDT']


##################################################  Helper Functions  ##################################################
@st.experimental_memo
def bulk_query(start, end, symbols, long_okx=True, net_SMA=False):
    dataframes = []
    for i in range(1, len(symbols) + 1):
        dataframe_name = 'df' + str(i)
        if net_SMA == False: 
            dataframe_name = pagination_funding_rate(symbols[i - 1], start, end).copy()
        else:
            dataframe_name = pagination_funding_rate_net_SMA(symbols[i - 1], start, end).copy()
        dataframes.append(dataframe_name)
    return dataframes

def get_data():
    data = ''
    try:
        data = bulk_query(20230515, today, selected, net_SMA=True)
    except:
        revised_end = datetime.strptime(today, '%Y%m%d')
        revised_end += timedelta(days=1)
        revised_end = str(revised_end)
        revised_end = revised_end.split(" ")[0].replace("-", "")
        data = bulk_query(20230515, revised_end, selected, net_SMA=True)
    return data
    
    
################################################## Layouts for dashboard ##################################################
st.title('MultiCoin Visualization Dashboard')

if 'btn_clicked' not in st.session_state:
    st.session_state['btn_clicked'] = False   # init state
def callback():
    st.session_state['btn_clicked'] = True    # change state value


# Select from symbols
selected = st.multiselect('Choose the targeted coin type', symbols)

# Prepare data for the selected coin
today = str(datetime.now())
today = today.split(" ")[0].replace("-", "")        
        
df_list = [pd.DataFrame() for _ in range(len(selected))]

st.write("")
if st.button('Start to gather data', on_click=callback) or st.session_state["btn_clicked"]:
    with st.spinner("Data gathering, please be patient"):
        df_list = get_data()
        
        mode_option = st.selectbox('Which mode do you want?', ('Show graphes for a single coin type', 'Cross coin analysis'))
        if mode_option == 'Show graphes for a single coin type':
            coin_option = st.selectbox('Which coin for analysis?', selected)
            idx = selected.index(coin_option)
            selected_df = df_list[idx]
            st.dataframe(selected_df)
            
            ## draw SMA graphes
            tag_options = st.multiselect('Which tag for graphing?', ['okx_binance_net_sma','okx_bybit_net_sma','funding_rate'])
            if 'okx_binance_net_sma' in tag_options:
                st.plotly_chart(px.line(selected_df.set_index('datetime')[okx_binance_net_sma], title=coin_option+'okx_binance_net_sma'))
            if 'okx_bybit_net_sma' in tag_options:
                st.plotly_chart(px.line(selected_df.set_index('datetime')[okx_bybit_net_sma], title=coin_option+'okx_bybit_net_sma'))
            if 'funding_rate' in tag_options:
                st.plotly_chart(px.line(selected_df.set_index('datetime')[funding_rate], title=coin_option+'funding_rate'))
        if mode_option == 'Cross coin analysis':
            tag_options = st.multiselect('Which tag for graphing?', df_list[0].columns[3:])
            for tag in tag_options:
                df = pd.DataFrame([i[tag] for i in df_list]).T
                df.columns = selected
                df['datetime'] = df_list[0]['datetime']
                st.plotly_chart(px.line(df, x='datetime',y = df.columns, title = tag))