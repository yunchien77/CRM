import requests
from dotenv import load_dotenv
import os

SERVER_URL = 'ap12.ragic.com'
ACCOUNT_NAME = 'cancerfree'
TAB = 'forms5'
SHEET_INDEX = '4'

FIELD_ID_1 = '1001976'
FIELD_ID_2 = '1001977'
FIELD_ID_3 = '1001982'
FIELD_ID_4 = '1001983'
FIELD_ID_5 = '1001984'
FIELD_ID_6 = '1001985'
FIELD_ID_7 = '1001986'
FIELD_ID_8 = '1001988'
FIELD_ID_9 = '1001990'
FIELD_ID_10 = '1001992'
FIELD_ID_11 = '1001994'
FIELD_ID_12 = '1001996'
FIELD_ID_13 = '1001998'
FIELD_ID_14 = '1001989'
FIELD_ID_15 = '1001991'
FIELD_ID_16 = '1001993'
FIELD_ID_17 = '1001995'
FIELD_ID_18 = '1001997'
FIELD_ID_19 = '1001987'

load_dotenv()
API_KEY = os.getenv('RAGIC_API_KEY')

API_ENDPOINT_LISTING_PAGE = f'https://{SERVER_URL}/{ACCOUNT_NAME}/{TAB}/{SHEET_INDEX}'

#
# creating a new entry
#
params = {
    'api': '',
    'v': 3
}

def createEntity(NAME, COMPANY, DEPART1, DEPART2, TITLE1, TITLE2, TITLE3, MOBILE1, MOBILE2, TEL1, TEL2, FAX1, FAX2, EMAIL1, EMAIL2, ADDRESS1, ADDRESS2, WEBSITE, DESCRIPTION):
    data = {
        FIELD_ID_1: NAME,        
        FIELD_ID_2: COMPANY,     
        FIELD_ID_3: DEPART1,       
        FIELD_ID_4: DEPART2,       
        FIELD_ID_5: TITLE1,       
        FIELD_ID_6: TITLE2,     
        FIELD_ID_7: TITLE3,
        FIELD_ID_8: MOBILE1,
        FIELD_ID_9: MOBILE2,
        FIELD_ID_10: TEL1,
        FIELD_ID_11: TEL2,
        FIELD_ID_12: FAX1,
        FIELD_ID_13: FAX2,
        FIELD_ID_14: EMAIL1,
        FIELD_ID_15: EMAIL2,
        FIELD_ID_16: ADDRESS1,
        FIELD_ID_17: ADDRESS2,
        FIELD_ID_18: WEBSITE,
        FIELD_ID_19: DESCRIPTION,
    }

    response = requests.post(API_ENDPOINT_LISTING_PAGE, params=params, json=data, headers={'Authorization': 'Basic '+API_KEY})
    print(response.text)