import requests
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = 'b0hPOFAzbkRaNzFJV1F4RzNkRTA1Sko3QS9BMVlrbzdUZWtzVi9FcGtzejVFTzlDMGxHMnMwVzVQaFpEcGdzT29JOENFVy9qNzZnPQ=='

SERVER_URL = 'ap12.ragic.com'
ACCOUNT_NAME = 'cancerfree'
TAB = 'forms5'
SHEET_INDEX = '4'

FIELD_ID = '1002023'
FIELD_LINK = '1002999'

params = {
    'api': '',
    'v': 3,
    'subtables': 0
}

API_ENDPOINT_LISTING_PAGE = f'https://{SERVER_URL}/{ACCOUNT_NAME}/{TAB}/{SHEET_INDEX}'

response = requests.get(API_ENDPOINT_LISTING_PAGE, params=params, headers={'Authorization': 'Basic '+API_KEY})

def getAllPeople():
    response = requests.get(API_ENDPOINT_LISTING_PAGE, params=params, headers={'Authorization': 'Basic '+API_KEY})
    #print(response.text)

    data = response.json()

    if data:
        people_list = []
        for key, value in data.items():
            if value['相關連結'] == '':
                search_str = value['Name'] + ' ' + value['Company']
                people_list.append({
                    "id": key,
                    "search": search_str
                })
    return people_list

def updateData(RECORD_ID, result):
    print(RECORD_ID, result)
    API_ENDPOINT_FORM_PAGE = f'https://{SERVER_URL}/{ACCOUNT_NAME}/{TAB}/{SHEET_INDEX}/{RECORD_ID}'
    
    data = {
        FIELD_LINK: result
    }
    requests.post(API_ENDPOINT_FORM_PAGE, params=params, json=data, headers={'Authorization': 'Basic '+API_KEY})


getAllPeople()