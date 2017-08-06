import gspread

import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

from tools import get_config


def authenticate_drive():

    email = get_config()['email']

    json_key = json.load(open('creds.json'))  # json credentials you downloaded earlier
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']

    credentials = ServiceAccountCredentials.from_json_keyfile_name('creds.json', scope)

    file = gspread.authorize(credentials)  # authenticate with Google

    return file

# read sheet
# sheet = file.open("test_spreadsheet").sheet1  # open sheet
# all_cells = sheet.range('A1:A4')
# for cell in all_cells:
#     print(cell.value)

# row = sheet.row_values(1) # first row
# col = sheet.col_values(2) # models

# create spreadsheet. will only do so once
# sh = file.create('Spotify test')
#
# sh.share(email, perm_type='user', role='writer')
#
# # create worksheet
# worksheet = sh.add_worksheet(title="Sheet2", rows="100", cols="20")

