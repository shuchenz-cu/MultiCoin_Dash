import streamlit as st
import pandas as pd
import plotly.express as px
from GetData import download_csv
from datetime import datetime
import os
import datetime
st.set_page_config(layout='wide')

file_path = 'recent_three_months_data.csv'

if 'btn' not in st.session_state:
    st.session_state.btn = False   # init state
def callback():
    st.session_state['btn'] = True    # change state value
    
@st.cache_data(show_spinner=False)
def check_csv_file_exists(file_path):
    if os.path.exists(file_path):
        creation_timestamp = os.path.getctime(file_path)
        creation_date = datetime.datetime.fromtimestamp(creation_timestamp).date()
        today = datetime.datetime.today().date()
        if creation_date == today:
            st.write(f"The CSV file '{file_path}' exists and is created today.")
        else:
            st.write(f"The CSV file '{file_path}' does not exist or is expired. Now starting to download data.")
            with st.spinner("Downloading, please be patient"):
                download_csv()
    else:
        st.write(f"The CSV file '{file_path}' does not exist or is expired. Now starting to download data.")
        with st.spinner("Downloading, please be patient"):
            download_csv()
            
# Tags:
okx_binance_net_sma = ['Long OKX Short Binance 30d Net SMA', 'Long OKX Short Binance 14d Net SMA',
                        'Long OKX Short Binance 7d Net SMA', 'Long OKX Short Binance 3d Net SMA']
okx_bybit_net_sma = ['Long OKX Short Bybit 30d Net SMA', 'Long OKX Short Bybit 14d Net SMA',
                    'Long OKX Short Bybit 7d Net SMA', 'Long OKX Short Bybit 3d Net SMA']
funding_rate = ['okx_fundingRate', 'binance_fundingRate', 'bybit_fundingRate']
            
# Loading data
st.title('MultiCoin Visualization Dashboard(Three Months)')
st.warning('Warning: due to memory usage limitation, the dashboard could only load 8 plots with each has the duration of 3 months', icon="⚠️")

if st.button('Download Current Recent Three Months Data', on_click=callback) or st.session_state['btn']:
    check_csv_file_exists(file_path)
    full_data = pd.read_csv('recent_three_months_data.csv', index_col=0)
    symbols = full_data['symbol'].unique()
    selected = st.multiselect('Choose the targeted coin type', symbols,  default=symbols[:3])
    mode_option = st.selectbox('Which mode do you want?', ('Show graphes for a single coin type', 'Cross coin analysis'))
    
    if mode_option == 'Show graphes for a single coin type':
        multiplier = st.number_input('Desired multiplier:', value=1.00)
        tag_options = st.multiselect('Which tag for graphing?', ['okx_binance_net_sma','okx_bybit_net_sma','funding_rate'])
        
        for idx in range(len(selected)):
            selected_df = full_data[full_data['symbol'] == selected[idx]].reset_index()
            columns_to_multiply = selected_df.columns[4:] # select all numerical value
            selected_df[columns_to_multiply] = selected_df[columns_to_multiply] * multiplier
            if 'okx_binance_net_sma' in tag_options:
                earliest_row_bn = selected_df[selected_df['Long OKX Short Binance 3d Net SMA'].notnull()].first_valid_index()
                st.plotly_chart(px.line(selected_df.set_index('datetime').iloc[earliest_row_bn:][okx_binance_net_sma],
                                        title=selected_df.iloc[0]['symbol']+'okx_binance_net_sma'), use_container_width=True)
            if 'okx_bybit_net_sma' in tag_options:
                earliest_row_bb = selected_df[selected_df['Long OKX Short Bybit 3d Net SMA'].notnull()].first_valid_index()
                st.plotly_chart(px.line(selected_df.set_index('datetime').iloc[earliest_row_bb:][okx_bybit_net_sma],
                                        title=selected_df.iloc[0]['symbol']+'okx_bybit_net_sma'), use_container_width=True)
            if 'funding_rate' in tag_options:
                st.plotly_chart(px.line(selected_df.set_index('datetime')[funding_rate], 
                                        title=selected_df.iloc[0]['symbol']+'funding_rate'), use_container_width=True)
                    
        # Show dataframe chart
        display_list = st.multiselect('Which dataframe to display?', selected, default=selected[0])
        for coin in display_list:
            df = full_data[full_data['symbol'] == coin]
            columns_to_multiply = df.columns[3:] # select all numerical value
            df[columns_to_multiply] = df[columns_to_multiply] * multiplier
            st.dataframe(df)
            
    if mode_option == 'Cross coin analysis':
        tag_options = st.multiselect('Which tag for graphing?', full_data.columns[4:])
        for tag in tag_options:
            table = []
            for coin in selected:
                table.append(list(full_data[full_data['symbol'] == coin][tag]))
            df = pd.DataFrame(table).T
            df.columns = selected
            df['datetime'] = full_data[full_data['symbol'] == full_data['symbol'].unique()[0]]['datetime']
            st.plotly_chart(px.line(df.dropna(), x='datetime',y = df.columns, title = tag), use_container_width=True)