import requests
import streamlit as st
import pandas as pd
import pyarrow as pa
from datetime import datetime, timedelta
from google.oauth2.service_account import Credentials
import gspread
import os
import numpy as np


def printPDF(username, folder):
    # Directory to search in
    folder_path = './files/invoices/' + folder

    # List all files in the directory and filter by the search string
    matching_file = [filename for filename in os.listdir(folder_path) if username in filename][0]

    # # Print the PDF
    os.startfile(folder_path + "/" + matching_file, 'print')
    st.stop()
def remove_special_characters(input_string):
    # Define a set of characters to be removed
    special_chars = ' ,._`;\''
    # Use str.strip() to remove leading and trailing occurrences of specified characters
    cleaned_string = input_string.strip(special_chars)
    return cleaned_string
def select_sheet():
    skey = st.secrets["gcp_service_account"]
    credentials = Credentials.from_service_account_info(
      skey,
      scopes=st.secrets.scopes,
    )
    client = gspread.authorize(credentials)
    workbookoption = st.radio('Select a workbook to begin:', (workbook for workbook in st.secrets.gcp_service_account.spreadsheets))
    workbook = client.open(workbookoption)
    
    sheets = workbook.worksheets()
    option = st.radio('Select a sheet:', (sheet.title for sheet in sheets[-5:]), index=len(sheets[-5:])-1)
    
    folder = option
    folder = folder.replace("/", "")
    if st.button("Confirm & Load Data"):
        sheet_import = workbook.worksheet(option)
        weekly_records = sheet_import.get_all_records()
        weekly = pd.DataFrame.from_dict(weekly_records)
        weekly['Username'] = weekly['Username'].apply(remove_special_characters)
        if weekly['Price'].dtype == 'object':
            weekly['Price'] = weekly['Price'].str.replace('$', '')
        date_format = "%m/%d/%Y"
        min_date = datetime.strptime(weekly['Date'].max(), date_format).date()
        max_date = datetime.strptime(datetime.now().date().strftime(date_format), date_format).date()
        
        usernames = get_invoice(min_date, max_date)
        for username in usernames:
            if weekly[weekly['Username'] == username].shape[0] > 0 and weekly[weekly['Username'] == username]['BoxClosed'].iloc[0] == '':
                st.write(username, " just paid")
            weekly.loc[weekly['Username'] == username, 'BoxClosed'] = 1
        sheet_import.update([weekly.columns.values.tolist()] + weekly.fillna(-1).values.tolist())


def get_invoice(min_date, max_date):
  # PayPal API endpoint for obtaining an access token
  token_url = 'https://api-m.paypal.com/v1/oauth2/token'
  # Data for obtaining a token
  token_data = {
      'grant_type': 'client_credentials'
  }
  token_headers = {'Accept': 'application/json',
                   'Accept-Language': 'en_US'}
  # Request a new access token
  token_response = requests.post(
      token_url,
      headers=token_headers,
      auth=(st.secrets.client_id, st.secrets.client_secret),
      data=token_data)
  # Check the response
  if token_response.status_code == 200:
      access_token = token_response.json()['access_token']
      get_invoice_url = 'https://api-m.paypal.com/v2/invoicing/invoices'
      # Use the new access token in your API request
      headers = {
          'Content-Type': 'application/json',
          'Authorization': f'Bearer {access_token}',
          'Prefer': 'return=representation'
      }
      params = (
            ('total_required', 'false'),
            ('page_size', 50)
        )
      get_invoice_response = requests.get(get_invoice_url, headers=headers, params=params)
      # Check the response
      if get_invoice_response.status_code == 200:
            json_data = get_invoice_response.json()['items']
            # json_data[0]["primary_recipients"][0]["billing_info"]["name"].keys()
            df = pd.DataFrame(json_data)
            table = pa.Table.from_pandas(df)
            df = table.to_pandas()
            df['username'] = df['primary_recipients'].apply(lambda x: x[0]['billing_info']["name"]['surname'])
            df['payment_amount'] = df['amount'].apply(lambda x: x['value'])
            df['invoice_date'] = df['detail'].apply(lambda x: x['invoice_date'])
            df['invoice_date'] = pd.to_datetime(df['invoice_date']).dt.date
            df = df[(df['invoice_date'] >= min_date) & (df['invoice_date'] <= max_date)]
            df = df[['status', 'username', 'payment_amount', 'invoice_date']]
            df
            return df[df.status == 'PAID'].username
      else:
          st.write("Failed to create invoice for: ", Username)
          st.write("Status Code:", create_invoice_response.status_code)
          st.write("Error Message:", create_invoice_response.text)
          return []
  else:
      st.write("Failed to obtain a new access token.")
      st.write("Status Code:", token_response.status_code)
      st.write("Error Message:", token_response.text)
      return []
select_sheet()




#NB. Original query string below. It seems impossible to parse and
#reproduce query strings 100% accurately so the one below is given
#in case the reproduced version is not "correct".
# response = requests.get('https://api-m.sandbox.paypal.com/v2/invoicing/invoices?total_required=true', headers=headers)
