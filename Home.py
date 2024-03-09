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

import streamlit as st
from streamlit.logger import get_logger
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta
import pytz

# generate invoce
import numpy as np

LOGGER = get_logger(__name__)

def create_dataframe():
    skey = st.secrets["gcp_service_account"]
    credentials = Credentials.from_service_account_info(
      skey,
      scopes=st.secrets.scopes,
    )
    client = gspread.authorize(credentials)
    url="https://docs.google.com/spreadsheets/d/11ofUhzFKWPBCJxI-Xj-coL34ie0VE-XkHKA_SQcDOSI/edit#gid=1941987294"
    sh = client.open_by_url(url)
    df = pd.DataFrame(sh.worksheet("Total").get_all_records())
    return df

def run():
    st.set_page_config(
        page_title="Home",
        page_icon="👋",
    )
    
    st.write("# :balloon: Welcome to Crystal Clear! 👋")  


    st.markdown(
        """        
    """
    )


if __name__ == "__main__":
    run()
    df = create_dataframe()
    df
