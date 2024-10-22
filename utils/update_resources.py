import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import os
import json
from dotenv import load_dotenv
from utils.helpers import a_ph




amz_sku_mapping_worksheet_name = "amazon_sku_mapping"



def update_resources():
    # print("Updating resources")
    update_from_google_sheet()
    # print("Resources updated ")

def update_from_google_sheet():
   
    try:
        workbook = get_workbook()    
        
        update_amz_sku_mapping(workbook)
     
    except Exception as e: 
        print(f"Error in updating resources from google sheet {e}")
        raise e




def update_amz_sku_mapping(workbook):
    mapping_df = pd.DataFrame(get_worksheet_df_by_name(workbook, amz_sku_mapping_worksheet_name).get_all_records())
    mapping_df.to_csv(os.path.join(a_ph('/data/amazon'), 'amz_sku_mapping.csv'), index=False)
    print("Retrieved amazon - blue system mapping")



def get_workbook(sheet_id = "1ZMzIMn7CzV_tUJSfXguHYLh3fkkgHVh_0u2NBWCzEAQ"):
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = get_sheets_api_credentials()
    client = gspread.authorize(creds)
    workbook = client.open_by_key(sheet_id)
    return workbook


def get_sheets_api_credentials():
    # Load environment variables
    load_dotenv(override=True)
    # print("Getting google sheets api credentials")
    # Create a dictionary with the credentials
    cred_dict = {
        "type": "service_account",
        "project_id": "w4l-inventory-update",
        "private_key_id": os.getenv("GOOGLE_PRIVATE_KEY_ID"),
        "private_key": os.getenv("GOOGLE_PRIVATE_KEY"),   
        "client_email": os.getenv("GOOGLE_CLIENT_EMAIL"),
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": os.getenv("GOOGLE_CLIENT_X509_CERT_URL"),
        "universe_domain": "googleapis.com"
    }

    # Create a temporary file to store the credentials
    temp_cred_file = a_ph('temp_credentials.json')
    # if temp_cred_file exists, delete it first 
    if os.path.exists(temp_cred_file):
        os.remove(temp_cred_file)
        print("Deleted the existing temp_cred_file")

    with open(temp_cred_file, 'w') as f:
        json.dump(cred_dict, f)
        # print("Created the temp_cred_file")


    # Get the credentials from the temporary file
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    
    creds = Credentials.from_service_account_file(temp_cred_file, scopes=scopes)

    # Remove the temporary file
    os.remove(temp_cred_file)

    return creds




def get_worksheet_df_by_name(workbook,worksheet_name):

    worksheet_list = map(lambda x: x.title, workbook.worksheets())
    if worksheet_name not in worksheet_list:
        print(f"Worksheet {worksheet_name} not found in the google sheet")
        raise ValueError(f"Worksheet {worksheet_name} not found in the google sheet")
    # get the worksheet to df 
    return workbook.worksheet(worksheet_name)










# test run 
def test():
    update_resources()

# test()
