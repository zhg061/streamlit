import streamlit as st
import requests

# TikTok token URL
token_url = 'https://open.tiktokapis.com/v2/oauth/token/'

# Data for obtaining a token
token_data = {
    'grant_type': 'client_credentials',
    'client_key': st.secrets.tiktok_client_key,  # Replace with your actual client key
    'client_secret': st.secrets.tiktok_client_secret  # Replace with your actual client secret
}

# Headers for the request
token_headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Accept': 'application/json',
    'Accept-Language': 'en_US'
}

# Request a new access token
token_response = requests.post(
    token_url,
    headers=token_headers,
    data=token_data
)

# Check the response
response_json = token_response.json()
if token_response.status_code == 200:
    access_token = response_json['access_token']
    st.write("Access Token:", access_token)
    user_info_url = 'https://open.tiktokapis.com/v2/user/info/'

    user_info_headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json'
    }

    user_info_response = requests.get(user_info_url, headers=user_info_headers)

    if user_info_response.status_code == 200:
        user_info = user_info_response.json()
        follower_count = user_info['data']['follower_count']
        st.write("Follower Count:", follower_count)
    else:
        st.write("Error:", user_info_response.json())

else:
    st.write("Error:", response_json)
