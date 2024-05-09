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

def get_instagram_follower_count(username):
    # Endpoint URL
    url = f"https://i.instagram.com/api/v1/users/web_profile_info/?username={username}"
    
    # Headers with the user-agent as required
    headers = {
        'User-Agent': 'Instagram 76.0.0.15.395 Android (24/7.0; 640dpi; 1440x2560; samsung; SM-G930F; herolte; samsungexynos8890; en_US; 138226743)'
    }
    
    # Send GET request to Instagram API
    response = requests.get(url, headers=headers)
    
    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
        # Extracting follower count
        follower_count = data['data']['user']['edge_followed_by']['count']
        posts_count = data['data']['user']['edge_owner_to_timeline_media']['count']
        return follower_count, posts_count
    else:
        return f"Failed to retrieve data, status code: {response.status_code}"



def collect():
    df = pd.DataFrame()
    today_date = datetime.date.today()
    formatted_date = today_date.strftime('%Y-%m-%d')
    handles = st.secrets.handles
    for handle in handles:
        followers, posts = get_instagram_follower_count(handle)  
        new_row = {'Account': handle, 'Followers': followers, 'Posts': posts, 'Date': formatted_date}
        df = df.append(new_row, ignore_index=True)
    total = pd.concat([fp, df], ignore_index=True)          
    Followers_Posts.update([total.columns.values.tolist()] + total.fillna(-1).values.tolist())
skey = st.secrets["gcp_service_account"]
credentials = Credentials.from_service_account_info(
    skey,
    scopes=st.secrets.scopes,
    )
client = gspread.authorize(credentials)
InstagramData = client.open('InstagramData')
Followers_Posts = InstagramData.worksheet("Followers&Posts")
df = pd.DataFrame(Followers_Posts.get_all_records())
if st.button("Collect New Data"):
    collect()
df['Date'] = pd.to_datetime(df['Date'])

# Sort the DataFrame by Account and Date
df.sort_values(by=['Account', 'Date'], inplace=True)

# Calculate the difference in followers and posts
df['Follower Increase'] = df.groupby('Account')['Followers'].diff()
df['Posts Increase'] = df.groupby('Account')['Posts'].diff()

# Filter to get entries with an increase in posts and followers
filtered_df = df[(df['Follower Increase'] > 0) & (df['Posts Increase'] > 0)]

# Get the latest entry for each account meeting the condition
latest_filtered_df = filtered_df.groupby('Account').last().reset_index()

# Sort the results by the follower increase
sorted_df = latest_filtered_df.sort_values(by='Follower Increase', ascending=False)

sorted_df[['Account', 'Follower Increase', 'Posts Increase', 'Date']]

