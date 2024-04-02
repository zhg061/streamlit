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

from streamlit.hello.utils import show_code
import time
import requests
import copy
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta
import pytz
import numpy as np
import json


import streamlit as st

from docx import Document
from docx.shared import Inches
import os
from fpdf import FPDF
crystal_names = [
        'garden quartz','smokey quartz','dragon fruite quartz''clear quartz',
        'fire quartz','strawberry quartz','quartz','amethyst','citrine','rose quartz',
        'red tiger eye','tiger eye','rutile','lapis lazuli','turquoise','amber',
        'agate','jade','onyx','opal','sapphire','emerald','ruby','garnet','topaz',
        'aquamarine','peridot','moonstone','ammonite','prehnite','bloodstone',
        'jasper','fluorite','sodalite','chalcedony','labradorite','malachite',
        'morganite','kyanite','honey calcite','calcite','rhodonite','amazonite',
        'hematite','pyrite','obsidian','carnelian','serpentine','larimar',
        'howlite','sunstone','tanzanite','iolite','zircon','spinel','tourmaline',
        'chrysocolla','lepidolite','smoky quartz','beryl','azurite','volcano agate',
        'volcano ash','sphalerite','ocean jasper','pink agate','white druzy agate',
        'flower agate''agate','yooperlite','sphalerite','petrified wood','septarian',
        'shiva shells','deal', 'epidote', 'blue lace'
    ]
shapes=['tower', 'pen', 'mushroom', 'bowl', 'palm stones', 'tumble', 'sphere',
      'mini sphere', 'bracelet', 'necklace', 'pendant', 'ring', 'raw', 'free form',
      'elephant', 'santa', 'carving', 'conch', 'point', 'moon', 'worry stone',
      'string', 'turtle', 'slab', 'cupcake', 'dragon', 'skull', 'pikachu', 'hair clip',
      'body', 'heart', 'tree', 'frame', 'massager', 'bear', 'flower', 'rose', 'star',
      'lizard', 'light', 'pot', 'butterfly', 'wing', 'sunflower', 'frog', 'lotus', 'deal',
      'shell']
# Set the New York time zone
new_york_timezone = pytz.timezone('America/New_York')
# Get the current time in the New York time zone
ny_time = datetime.now(new_york_timezone)
# Format today's date
today_date = ny_time.strftime("%Y-%m-%d")
new_date = ny_time + timedelta(days=2)
due_date = new_date.strftime("%Y-%m-%d")
invoice_data = {
        "detail":
         {
             "invoice_date": today_date,
             "currency_code": "USD",
             "note": "We appreciate your business and please come again!",
             "payment_term": { "due_date": due_date }
          },
        "invoicer":
         {
             "name":
              {
                  "surname": "Crystal Clear"
              },
             "email_address": st.secrets.email,
             "website": st.secrets.website,
        },
        "primary_recipients": [
            { "billing_info":
             { "name": { "given_name": "", "surname": "" },
               "email_address": "lucyguo0803@gmail.com"
             }
        }],
        "items": [],
        "configuration": { "partial_payment": { "allow_partial_payment": False }},
        "amount": { "breakdown":
                      {
                          "shipping": { "amount": { "currency_code": "USD", "value": "10.00" }},
                          #  "discount": { "invoice_discount": { "percent": "5" } }
                      }
                  }
        }
def generate_pdf_invoice(df, Username, folder, user_name_dict):
    font="Courier"
    pdf = FPDF()
    pdf.set_left_margin(20)   # Adjust as needed
    pdf.set_right_margin(15)  # Adjust as needed

    pdf.add_page()
    pdf.set_font("Courier", size=12)

    # pdf.set_xy(0, pdf.get_y())  # Reset X position to leftmost
    pdf.multi_cell(0, 10, txt='', align='C')  # Add a centered line for the picture

    pdf.image('./files/brand_logo.jpg', x=pdf.w/2-30, y=pdf.get_y(), w=60)
    pdf.set_xy(20, pdf.get_y() + 60)  # Move down after the picture

    pdf.set_font(font, style='B', size=16)
    pdf.multi_cell(0, 10, txt='Invoice')
    pdf.set_font(font, size=12)  # Reset font size after heading
    name = user_name_dict[Username]+"(" + Username + ")"
    if (user_name_dict[Username]==""):
      name=Username
    content = [
        f"Dear {name},",
        "Please find the attached invoice for your recent purchase from Crystal Clear.",
        # Add other paragraphs and table content here
    ]
    for para in content:
        pdf.multi_cell(0, 10, txt=para)

    # Add empty paragraphs
    for _ in range(1):
        pdf.multi_cell(0, 10, txt='')

    # Create and format table
    table = [
        ["Product Name", "Date", "Price"],
    ]
    # Change: actual price
    total = 0
    discount = 0
    for i in range(df.shape[0]):
        original_price = df.iloc[i].Price
        price = original_price# * 0.75
        # if (df.iloc[i].Date == "12/21/2023"):
        #   price = original_price * 0.65
        #   discount += original_price * 0.35
        #   table.append([df.iloc[i].Product, df.iloc[i].Date,
        #                 f'${price:,.2f}(originally ${original_price:,.2f})'])
        # else:
        table.append([df.iloc[i].Product, df.iloc[i].Date,
                        f'${original_price:,.2f}'])
        total += price
    # Change: discount
    table.append(["", "Subtotal:", f'${np.sum(df.Price):,.2f}'])
    table.append(["", "Shipping:", f'${np.sum(df.Shipping):,.2f}'])
    # Add total price to the table
    table.append(["", "Total:", f'${total+np.sum(df.Shipping):,.2f}'])
    # Set table style
    col_width = pdf.w / 3.5
    row_height = 10
    for i, row in enumerate(table):
        for item in row:
            # Change
            if ((i >= len(table) - 2) or (i==0)):
              pdf.set_font(font, style='B', size=12)
              pdf.cell(col_width, row_height, txt=item, border=0, align='C')
              pdf.set_font(font, size=12)
            # Change
            elif (i == len(table) - 3):
              pdf.set_font(font, style='B', size=12)
              pdf.cell(col_width, row_height, txt=item, border='T', align='C')
            else:
              pdf.cell(col_width, row_height, txt=item, border=0, align='C')
        pdf.ln(row_height)
    content = [
        'We appreciate your business and please come again!',
        'Sincerely,',
        'Crystal Clear'
    ]
    # Get the current Y position
    current_y = pdf.get_y()
    if (current_y < pdf.h - 70):
        # Set the Y position to the bottom of the page
        pdf.set_y(pdf.h - 60)  # Adjust the value (20 in this case) as needed
        # Add the content
        for para in content:
            pdf.multi_cell(0, 10, txt=para)
    # Save the PDF
    pdf.output("./files/invoices/" + folder + "/" + name + "$" + str(total+np.sum(df.Shipping)) + ".pdf")

def send_invoice(df, Username, user_name_dict, user_email_dict):
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
      create_invoice_url = 'https://api-m.paypal.com/v2/invoicing/invoices'
      # Use the new access token in your API request
      headers = {
          'Content-Type': 'application/json',
          'Authorization': f'Bearer {access_token}',
          'Prefer': 'return=representation'
      }
      invoice = copy.deepcopy(invoice_data)
      invoice['primary_recipients'][0]['billing_info']['name']['surname']=Username
      invoice['primary_recipients'][0]['billing_info']['name']['given_name']=user_name_dict[Username]
      # change
      invoice["primary_recipients"][0]["billing_info"]["email_address"] = user_email_dict[Username]
      for i in range(df.shape[0]):
        # change
        # if (df.iloc[i].Date == "12/21/2023"):
        #   invoice['items'].append(
        #       { "name": df.iloc[i].Product,
        #       "description": df.iloc[i].Date,
        #         "quantity": "1",
        #         "unit_amount": { "currency_code": "USD", "value": str(df.iloc[i].Price) },
        #         "discount": {
        #             "percent": "35",
        #                     #  "amount": {"currency_code": "USD", "value": "2.5"}
        #                     },
        #         "unit_of_measure": "QUANTITY" })
        # else:
        invoice['items'].append(
            { "name": df.iloc[i].Product,
            "description": df.iloc[i].Date,
            "quantity": "1",
            "unit_amount": { "currency_code": "USD", "value": str(df.iloc[i].Price) },
            "unit_of_measure": "QUANTITY" })
      Shipping=np.sum(df.Shipping)
      invoice["amount"]["breakdown"]["shipping"]["amount"]["value"]=str(Shipping)
      json_data = json.dumps(invoice)
      # Make the API request to create an invoice
      create_invoice_response = requests.post(create_invoice_url, headers=headers, data=json_data)
      # Check the response
      if create_invoice_response.status_code == 201:
          invoice_id = create_invoice_response.json()["id"]
          headers = {
              'Authorization': f'Bearer {access_token}',
              'Content-Type': 'application/json',
          }
          data = '{ "send_to_invoicer": true }'
          response = requests.post(f'https://api-m.paypal.com/v2/invoicing/invoices/{invoice_id}/send', headers=headers, data=data)
          if response.status_code == 200:
            st.write("Invoice sent successfully for: ", Username)
          else:
            st.write("Failed to send invoice for: ", Username)
            st.write("Status Code:", response.status_code)
            st.write("Error Message:", response.text)
      else:
          st.write("Failed to create invoice for: ", Username)
          st.write("Status Code:", create_invoice_response.status_code)
          st.write("Error Message:", create_invoice_response.text)
  else:
      st.write("Failed to obtain a new access token.")
      st.write("Status Code:", token_response.status_code)
      st.write("Error Message:", token_response.text)
def remove_special_characters(input_string):
    # Define a set of characters to be removed
    special_chars = ' ,._`;\''
    # Use str.strip() to remove leading and trailing occurrences of specified characters
    cleaned_string = input_string.strip(special_chars)
    return cleaned_string
def fillTypes(types, weekly):
    for index, row in weekly.iterrows():
      if (row['Type'] == ''):
        input = row['Product'].lower()
        for c_type in types:
          if c_type in input:
            weekly.iloc[index, 5] = c_type
            break
        if weekly.iloc[index, 5] == '':
          weekly.iloc[index, 5] = 'deal'
    return weekly
def fillShapes(shapes, weekly):
    for index, row in weekly.iterrows():
      if (row['Shape'] == ''):
        input = row['Product'].lower()
        for c_shape in shapes:
          if c_shape in input:
            weekly.iloc[index, 6] = c_shape
            break
        if weekly.iloc[index, 6] == '':
          weekly.iloc[index, 6] = 'deal'
    return weekly
def updateShipping(name, price, weekly):
    weekly[weekly.Username == name].Shipping[0]=price
    index_to_modify = weekly.loc[weekly.Username == name].index[0]
    weekly.loc[index_to_modify, 'Shipping'] = price
    return weekly
def load_data(sheet_import):
    weekly_records = sheet_import.get_all_records()
    weekly = pd.DataFrame.from_dict(weekly_records)
    # testing
    for i in ['Product', 'Username']:
      if (weekly[i] == "").any():
          st.error(f"Error: Empty values detected in the {i} column!")
          st.stop()    
    if weekly['Price'].dtype == 'object':
        weekly['Price'] = weekly['Price'].str.replace('$', '')#.str.replace('.00', '')
    weekly['Price'] = weekly['Price'].astype(float)
    # weekly['Username'] = weekly['Username'].str.replace(' ', '')
    if 'Username' in weekly.columns:
        weekly['Username'] = weekly['Username'].apply(remove_special_characters)
    weekly['Product'] = weekly['Product'].apply(remove_special_characters)
    if 'Shipping' not in weekly.columns:
        weekly['Shipping'] = 0
    else:
        weekly['Shipping'].replace('', pd.NA, inplace=True)  # Only needed if you have empty strings
        weekly['Shipping'].fillna(0, inplace=True)
    # testing
    for j in ['Price', 'Shipping']:
        if (weekly[j] < 0).any():
          st.error(f"Error: Negative {j} detected! Please go back to your Google Sheet and make changes.")
          st.stop()
    weekly['Date'] = weekly['Date'].apply(lambda x: x + '/2023' if len(x) <= 8 else x)
    dates = pd.to_datetime(weekly['Date'])
    weekly['Weekday'] = dates.dt.weekday
    st.title("Invoice Summary:")
    st.write("Total Amount", np.sum(weekly.Price))
    # Merge the two DataFrames on "Username"
    if 'Username' in weekly.columns:
        weekly_sum_price = weekly.groupby("Username")["Price"].sum().reset_index()
        weekly_sum_ship = weekly.groupby("Username")["Shipping"].sum().reset_index()
        result1 = pd.merge(weekly_sum_price, weekly_sum_ship, on="Username")
        # Group by "Username" and aggregate list of "product"
        weekly_agg_products = weekly.groupby("Username")["Product"].agg(list).reset_index()
        result = pd.merge(result1, weekly_agg_products, on="Username")
        result
    weekly = fillTypes(crystal_names, weekly)
    weekly = fillShapes(shapes, weekly)
    sheet_import.update([weekly.columns.values.tolist()] + weekly.fillna(-1).values.tolist())
    return weekly
def generate_unique_random_number(df, column_name, start=100, end=999):
    while True:
        random_number = np.random.randint(start, end + 1)  # Generate random number
        if random_number not in df[column_name].values:  # Check if the number exists in the column
            return random_number
def checkCustomer(weekly):
    skey = st.secrets["gcp_service_account"]
    credentials = Credentials.from_service_account_info(
      skey,
      scopes=st.secrets.scopes,
    )
    client2 = gspread.authorize(credentials)
    customer = client2.open('Customer')
    customer_import = customer.worksheet("Sheet1")
    customer_records = customer_import.get_all_records()
    customer = pd.DataFrame.from_dict(customer_records)
    usernames = np.unique(weekly.Username)
    pickup = customer[customer.Pickup == 1].Username.tolist()
    # customer1 = customer[customer.Pickup == 0]
    user_email_dict = customer.set_index('Username')['Email'].to_dict()
    user_name_dict = customer.set_index('Username')['Name'].to_dict()
    usernames = [x for x in usernames if x not in pickup]
    new_york_timezone = pytz.timezone('America/New_York')
    ny_time = datetime.now(new_york_timezone)
    for username in usernames:
      if username not in user_email_dict:
        new_row = {'Username': username, 'Name': '', 'Email': '', 'App': '',
                   'Pickup': 1, 'DateAdded': ny_time.strftime("%m/%d/%Y"),
                   'id': generate_unique_random_number(customer, 'id')}
        customer = customer.append(new_row, ignore_index=True)
        st.write('add email address for', username)
      elif user_email_dict[username] == "":
        print(username, user_email_dict[username], "email")
    customer_import.update([customer.columns.values.tolist()] + customer.fillna(-1).values.tolist())
    return [user_name_dict, user_email_dict, usernames, customer]
def select_sheet():
    skey = st.secrets["gcp_service_account"]
    credentials = Credentials.from_service_account_info(
      skey,
      scopes=st.secrets.scopes,
    )
    client = gspread.authorize(credentials)
    # url=st.secrets.gcp_service_account.spreadsheet
    workbookoption = st.radio('Select a workbook to begin:', (workbook for workbook in st.secrets.gcp_service_account.spreadsheets))
    workbook = client.open(workbookoption)
    
    sheets = workbook.worksheets()
    option = st.radio('Select a sheet:', (sheet.title for sheet in sheets[-5:]))
    folder = option
    folder = folder.replace("/", "")
    os.makedirs('./files/invoices/' + folder, exist_ok=True)
    # Button for action
    if st.button("Confirm & Load Data"):
        with st.status("Loading and Cleaning Data...", expanded=True) as status:
          sheet_import = workbook.worksheet(option)
          weekly = load_data(sheet_import)          
          status.update(label="Checking for customer information...", expanded=True)
          user_name_dict, user_email_dict, usernames, customer = checkCustomer(weekly)
          # update total 
          status.update(label="Update Total...", expanded=True)
          # change: sheet name
          summary = client.open('Summary')
          total_import = summary.worksheet("Total")
          total = pd.DataFrame(total_import.get_all_records())
          if folder not in np.unique(total['Sheet']):
              weekly['Sheet'] = folder
              merged = pd.merge(weekly, customer, on='Username', how='left')
              merged = merged.drop(columns=['Username', 'Email', 'App', 'Pickup', 'Name', 'DateAdded'])
              total = pd.concat([total, merged], ignore_index=True)          
              total_import.update([total.columns.values.tolist()] + total.fillna(-1).values.tolist())
          # pdf
        #   status.update(label="Generating invoice PDF...", expanded=True)
        #   users = np.unique(weekly.Username)
        #   for i in range(len(users)):
        #       Username= users[i]
        #       df = weekly[weekly.Username == Username]
        #       generate_pdf_invoice(df, Username, folder, user_name_dict)
        #   status.update(label="Sending Invoices", expanded=True)
        #   status_text = st.empty() 
        #   progress_bar = st.progress(0)
        #   for i in range(len(usernames)):
        #       Username = usernames[i]
        #       status_text.text("%i%% Complete" % int(100*(i+1)/len(usernames)))
        #       progress_bar.progress((i+1)/len(usernames))
        #       df = weekly[weekly.Username == Username]
        #       send_invoice(df, Username, user_name_dict, user_email_dict)
        #   status_text.empty()
        #   progress_bar.empty()
          status.update(label="Done", state="complete", expanded=True)


st.set_page_config(page_title="Invoice", page_icon="📹")
st.markdown("# Select a sheet to begin")
select_sheet()


