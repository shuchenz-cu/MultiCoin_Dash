import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
from datetime import timedelta
from MultiCoin_FR_old import pagination_funding_rate_net_SMA, pagination_funding_rate
from datetime import datetime

st.set_page_config(layout='wide')


###
# Notification:
#     Current beta dashboard could successfully run under python 3.11.2 and the packages version listed in requirements.txt.
#     Due to the VPN restriction, it's difficult to publish the dashboard. Please rerun or exit the dashboard manually.
###

# For developer:
#   1. Change to annualize return(Done)
#   2. Add in prediction model results(Processing)
#   3. Check if the symbols is valid in all three markets(Processing, but mostly done)
#   4. Current invalid symbols(not able to retrieve funding rate in one of the three markets but mostly on okx or binance): 
#      'OGN/USDT:USDT', 'XVG/USDT:USDT', 'INJ/USDT:USDT', 'STMX/USDT:USDT', 'TOMO/USDT:USDT', 'AGLD/USDT:USDT', 'MAV/USDT:USDT', 'WLD/USDT:USDT', needing exploration on naming consistency
##################################################  Parameters ##################################################

# Tags:
okx_binance_net_sma = ['Long OKX Short Binance 30d Net SMA', 'Long OKX Short Binance 14d Net SMA',
                        'Long OKX Short Binance 7d Net SMA', 'Long OKX Short Binance 3d Net SMA']
okx_bybit_net_sma = ['Long OKX Short Bybit 30d Net SMA', 'Long OKX Short Bybit 14d Net SMA',
                    'Long OKX Short Bybit 7d Net SMA', 'Long OKX Short Bybit 3d Net SMA']
funding_rate = ['okx_fundingRate', 'binance_fundingRate', 'bybit_fundingRate']

# List of symbols:
symbols = ['BTC/USDT:USDT', 'ETH/USDT:USDT', 'SOL/USDT:USDT', 'XRP/USDT:USDT', 'DOGE/USDT:USDT',
           'COMP/USDT:USDT', 'MATIC/USDT:USDT', 'DOT/USDT:USDT', 'GMT/USDT:USDT', 
           'LINK/USDT:USDT', 'BCH/USDT:USDT', 'KNC/USDT:USDT', 'XLM/USDT:USDT', 'OP/USDT:USDT', 
           'LTC/USDT:USDT', 'MKR/USDT:USDT', 'ADA/USDT:USDT', 'AVAX/USDT:USDT', 'APE/USDT:USDT', 
           'FTM/USDT:USDT', 'SUI/USDT:USDT', 'ARB/USDT:USDT', 'BNB/USDT:USDT', 'THETA/USDT:USDT', 
           'SNX/USDT:USDT', 'APT/USDT:USDT', 'ATOM/USDT:USDT', 'MASK/USDT:USDT', 'GALA/USDT:USDT',
           'NEAR/USDT:USDT', 'EOS/USDT:USDT', 'ZEN/USDT:USDT', 'DYDX/USDT:USDT',  'LDO/USDT:USDT',
           'SAND/USDT:USDT', 'ETC/USDT:USDT', 'AAVE/USDT:USDT', 'CFX/USDT:USDT']



##################################################  Helper Functions  ##################################################
@st.cache_data
def bulk_query(start, end, symbols, long_okx=True, net_SMA=False):
    dataframes = []
    for i in range(1, len(symbols) + 1):
        dataframe_name = 'df' + str(i)
        placeholder = st.empty()
        with placeholder.container():
            st.write("Now getting data for",symbols[i - 1],"Retrieving data", i, "/", len(symbols))
        if net_SMA == False: 
            dataframe_name = pagination_funding_rate(symbols[i - 1], start, end).copy()
        else:
            dataframe_name = pagination_funding_rate_net_SMA(symbols[i - 1], start, end).copy()
        dataframes.append(dataframe_name)
        placeholder.empty()
    return dataframes

# Retrieving funding rate and sma data for the multiple given symbol
def get_data(start):
    data = ''
    try:
        data = bulk_query(start, today, selected, net_SMA=True)
    except:
        revised_end = datetime.strptime(today, '%Y%m%d')
        revised_end += timedelta(days=1)
        revised_end = str(revised_end)
        revised_end = revised_end.split(" ")[0].replace("-", "")
        data = bulk_query(start, revised_end, selected, net_SMA=True)
    return data

################################################## Layouts for dashboard ##################################################

st.title('General Multicoin Visualization Dashboard')

# Select from symbols
selected = st.multiselect('Choose the targeted coin type', symbols,  default=symbols)

# Prepare data for the selected coin
current = datetime.now()
today = str(current)
today = today.split(" ")[0].replace("-", "")
before = current - timedelta(days= 1.5 * 30)
before = str(before)
before = before.split(" ")[0].replace("-", "")
      
df_list = [pd.DataFrame() for _ in range(len(selected))]
st.write("")

if 'btn' not in st.session_state:
    st.session_state.btn = False   # init state
def callback():
    st.session_state['btn'] = True    # change state value


if st.button('Start to gather data', on_click=callback) or st.session_state['btn']:
    with st.spinner("Processing, please be patient"):
        df_list = get_data(before)
        mode_option = st.selectbox('Which mode do you want?', ('Show graphes for a single coin type', 'Cross coin analysis'))
        if mode_option == 'Show graphes for a single coin type':
            
            ## draw SMA graphes
            multiplier = st.number_input('Desired multiplier:', value=1.00)
            tag_options = st.multiselect('Which tag for graphing?', ['okx_binance_net_sma','okx_bybit_net_sma','funding_rate'])
            for idx in range(len(df_list)):
                selected_df = df_list[idx]
                if selected_df.shape == (0,0):
                    st.write(selected[idx], 'failed to retrieve dataframe')
                else:
                    columns_to_multiply = selected_df.columns[3:] # select all numerical value
                    selected_df[columns_to_multiply] = selected_df[columns_to_multiply] * multiplier
                    
                    if 'okx_binance_net_sma' in tag_options:
                        st.plotly_chart(px.line(selected_df.set_index('datetime')[okx_binance_net_sma], title=selected_df.iloc[0]['symbol']+'okx_binance_net_sma'), use_container_width=True)
                    if 'okx_bybit_net_sma' in tag_options:
                        st.plotly_chart(px.line(selected_df.set_index('datetime')[okx_bybit_net_sma], title=selected_df.iloc[0]['symbol']+'okx_bybit_net_sma'), use_container_width=True)
                    if 'funding_rate' in tag_options:
                        st.plotly_chart(px.line(selected_df.set_index('datetime')[funding_rate], title=selected_df.iloc[0]['symbol']+'funding_rate'), use_container_width=True)
                        
            df_display = st.multiselect('Which dataframe to display?', selected, default=selected[0])
            indices = [index for index, value in enumerate(selected) if value in df_display]
            for idx in indices:
                df = df_list[idx]
                columns_to_multiply = df.columns[3:] # select all numerical value
                df[columns_to_multiply] = df[columns_to_multiply] * multiplier
                st.dataframe(df)
        if mode_option == 'Cross coin analysis':
            tag_options = st.multiselect('Which tag for graphing?', df_list[0].columns[3:])
            for tag in tag_options:
                df = pd.DataFrame([i[tag] for i in df_list]).T
                df.columns = selected
                df['datetime'] = df_list[0]['datetime']
                st.plotly_chart(px.line(df, x='datetime',y = df.columns, title = tag), use_container_width=True)