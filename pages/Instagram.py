from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time
import streamlit as st
from google.oauth2.service_account import Credentials
import pandas as pd
import gspread
import datetime
import requests
import requests



def get_instagram_follower_count(username):
    # Endpoint URL
    url = f"https://graph.facebook.com/{st.secrets.version}/{st.secrets.igUserId}?fields=business_discovery.username({username}){{{st.secrets.fields}}}&access_token={st.secrets.access_token}"
    # Send GET request to Instagram API
    response = requests.get(url)
    # st.write(url, response.json())
    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
        # Extracting follower count
        follower_count = data['business_discovery']['followers_count']
        posts_count = data['business_discovery']['media_count']
        return follower_count, posts_count
    else:
        st.error(f"Failed to retrieve data, status code: {response.status_code}")




skey = st.secrets["gcp_service_account"]
credentials = Credentials.from_service_account_info(
    skey,
    scopes=st.secrets.scopes,
    )
client = gspread.authorize(credentials)
InstagramData = client.open('InstagramData')
Followers_Posts = InstagramData.worksheet("Followers&Posts")
df = pd.DataFrame(Followers_Posts.get_all_records())

def collect():
    new = pd.DataFrame()
    today_date = datetime.date.today()
    formatted_date = today_date.strftime('%Y-%m-%d')
    handles = st.secrets.handles
    status_text = st.empty() 
    progress_bar = st.progress(0)
    for i in range(len(handles)):
        status_text.text("%i%% Complete" % int(100*(i+1)/len(handles)))
        progress_bar.progress((i+1)/len(handles))
        followers, posts = get_instagram_follower_count(handles[i]) 
        new_row = {'Account': handles[i], 'Followers': followers, 'Posts': posts, 'Date': formatted_date}
        new = new.append(new_row, ignore_index=True)
    status_text.empty()
    progress_bar.empty()
    total = pd.concat([df, new], ignore_index=True)          
    Followers_Posts.update([total.columns.values.tolist()] + total.fillna(-1).values.tolist())

if st.button("Collect New Data"):
    collect()
df['Date'] = pd.to_datetime(df['Date'])

# Sort the DataFrame by Account and Date
df.sort_values(by=['Account', 'Date'], inplace=True)

# Calculate the difference in followers and posts
df['Follower Increase'] = df.groupby('Account')['Followers'].diff()
df['Posts Increase'] = df.groupby('Account')['Posts'].diff()
df[df.Account=='crystal.clear.cc']
df[df.Account=='crystal.clear.select']
# Filter to get entries with an increase in posts and followers
filtered_df = df[(df['Follower Increase'] > 0) & (df['Posts Increase'] > 0)]
# Get the latest entry for each account meeting the condition
latest_filtered_df = filtered_df.groupby('Account').last().reset_index()
# Sort the results by the follower increase
sorted_df = latest_filtered_df.sort_values(by='Follower Increase', ascending=False)

sorted_df[['Account', 'Follower Increase', 'Posts Increase', 'Date']]

