import string

import googleapiclient.errors
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build


alphabet = list(string.ascii_uppercase)

def check_id_and_error_catch(func):
    def decorator(self, *args):
        if Spreadsheet.spreadsheets_id is None:
            answer = 'Please add the spreadsheet_id!'
            return answer

        try:
            answer = func(self, *args)
        except googleapiclient.errors.HttpError as e:
            answer = str(e) + "\n\nCheck if the spreadsheet_id is correct, " \
                              "make sure you enter the correct arguments"

        return answer

    return decorator


class Spreadsheet:
    spreadsheets_id = None
    CREDENTIALS_FILE = 'creds.json'

    def __init__(self):
        self.credentials = Credentials.from_service_account_file(self.CREDENTIALS_FILE)
        self.service = build('sheets', 'v4', credentials=self.credentials)

    def create_spreadsheet(self, name: str) -> str:
        spreadsheet = self.service.spreadsheets().create(body={
            'properties': {'title': name},
            'sheets': [{'properties': {'sheetId': 0}}]
        }).execute()

        spreadsheet_id = spreadsheet['spreadsheetId']
        self.give_me_access(spreadsheet_id)
        link = make_me_link(spreadsheet_id)
        self.set_spreadsheet_id(spreadsheet_id)
        return link

    def give_me_access(self, spread_sheet_id: int):
        drive_service = build('drive', 'v3', credentials=self.credentials)
        drive_service.permissions().create(
            fileId=spread_sheet_id,
            body={'type': 'anyone', 'role': 'writer'},  # доступ на чтение кому угодно
            fields='id'
        ).execute()

    @check_id_and_error_catch
    def read_the_spreadsheet(self, value_range: str):
        response = self.service.spreadsheets().values().\
            get(spreadsheetId=self.spreadsheets_id, range=value_range).execute()

        values = response['values']
        answer = ''

        for index, rows in enumerate(values):
            for number, item in enumerate(rows):
                answer += f'[{alphabet[index]}{number + 1}: {item}] \n'
            answer += '\n'

        return answer

    @check_id_and_error_catch
    def get_list_of_sheets(self) -> str:
        sheet_metadata = self.service.spreadsheets().get(spreadsheetId=self.spreadsheets_id).execute()

        sheet_list = ''
        for sheet in sheet_metadata['sheets']:
            sheet_list += sheet['properties']['title']

        return sheet_list

    def set_spreadsheet_id(self, spreadsheet_id: str):
        Spreadsheet.spreadsheets_id = spreadsheet_id

    @check_id_and_error_catch
    def give_me_id(self):
        return f"\n\nYour id: <code> {Spreadsheet.spreadsheets_id} </code>"


def make_me_link(spreadsheet_id: int) -> str:
    link = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}"
    return link

# values = service.spreadsheets().values().get(
#     spreadsheetId=spreadsheets_id,
#     range="A1:E10",
#     majorDimension="ROWS"
# ).execute()

# value = service.spreadsheets().values().batchUpdate(
#     spreadsheetId=spreadsheets_id,
#     body={
#         "valueInputOption": "USER_ENTERED",
#         "data": [
#             {"range": "B3:C4",
#              "majorDimension": "ROWS",
#              "values": [["omnom", 'жесть'], ['афигеть', "прогерЭ"]]
#              }
#         ]
#     }
# ).execute()
