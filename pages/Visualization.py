# Copyright (c) Streamlit Inc. (2018-2022) Snowflake Inc. (2022)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import time
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta
import pytz
import numpy as np

import streamlit as st
from streamlit.hello.utils import show_code

import matplotlib.pyplot as plt


def create_dataframe():
    skey = st.secrets["gcp_service_account"]
    credentials = Credentials.from_service_account_info(
      skey,
      scopes=st.secrets.scopes,
    )
    client = gspread.authorize(credentials)
    sh = client.open('Summary')
    df = pd.DataFrame(sh.worksheet("Total").get_all_records())
    df['Date'] = pd.to_datetime(df['Date']).dt.date
    df['month'] = pd.to_datetime(df['Date']).dt.month
    return df
def plotting_demo(df):
    st.write("# Total Revenue By Date")
    progress_bar = st.progress(0)
    status_text = st.empty()  
    df = df.groupby('Date')['Price'].sum().reset_index()
    df = df.sort_values(by='Date', ascending=True)
    last_rows = np.array([[df.iloc[0, 0]]])
    chart = st.line_chart(df, x="Date", y="Price")
    # chart = st.line_chart(df.loc[0:0, :], x="Date", y="Price")
    # for i in range(df.shape[0]):
    #     new_rows = df.loc[i:i, :]
    #     status_text.text("%i%% Complete" % int(100*(i+1)/df.shape[0]))
    #     chart.add_rows(new_rows)
    #     progress_bar.progress(i/df.shape[0])
    #     last_rows = new_rows
    #     time.sleep(0.05)

    progress_bar.empty()
    status_text.empty()
    df
    st.write('Total', np.sum(df.Price))
    # Streamlit widgets automatically run the script from top to bottom. Since
    # this button is not connected to any other logic, it just causes a plain
    # rerun.
    # st.button("Re-run")
def customer(df):
    df = df.groupby(['Date', 'id']).sum()
    df = df.reset_index()
    df = df.groupby("Date")["Price"].agg(['mean', 'median', 'max']).reset_index()

    st.title('Customer')

    # Plot multiple lines in one chart
    st.line_chart(df.set_index('Date'))


def my_autopct(pct):
    return '{:.1f}%'.format(pct) if pct >= 3 else ''
def plot_type(df):
    st.write("# Percentage of Revenue By Crystal Type")
    typenumber = st.slider('Top Number of Crystal Types', 0, 30, 5)

    df['Type'] = df['Type'].replace('deal', 'deals')
    df = df[df.Type != "deals"]
    df = df.groupby('Type')['Price'].sum().reset_index()
    df = df.sort_values(by='Price', ascending=False)
    df = df[:typenumber]
    fig1, ax1 = plt.subplots()
    pie = ax1.pie(df['Price'], labels=df['Type'], autopct=my_autopct, startangle=90)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    st.pyplot(fig1)
def plot_shape(df):
    st.write("# Percentage of Revenue By Crystal Shape")
    typenumber = st.slider('Top Number of Crystal Shapes', 0, 30, 5)

    df['Shape'] = df['Shape'].replace('deal', 'deals')
    df = df[df.Shape != "deals"]
    df = df.groupby('Shape')['Price'].sum().reset_index()
    df = df.sort_values(by='Price', ascending=False)
    df = df[:typenumber]
    fig1, ax1 = plt.subplots()
    pie = ax1.pie(df['Price'], labels=df['Shape'], autopct=my_autopct, startangle=90)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    st.pyplot(fig1)

st.set_page_config(page_title="Total Revenue By Date", page_icon="📈")

st.write(
    """"""
)
st.button("Re-run")
df = create_dataframe()
min_date = df['Date'].min()
max_date = df['Date'].max()
selected_date_range = st.sidebar.slider('Select a Date Range', 
min_value=min_date, 
max_value=max_date, 
value=(max_date - timedelta(days=30), max_date),
format="MM/DD/YY")

df = df[(df['Date'] >= selected_date_range[0]) & (df['Date'] <= selected_date_range[1])]
plotting_demo(df)
customer(df)
plot_type(df)
plot_shape(df)


