import requests
from dotenv import load_dotenv
import os

SERVER_URL = 'ap12.ragic.com'
ACCOUNT_NAME = 'cancerfree'
TAB = 'forms5'
SHEET_INDEX = '9'

FIELD_ID_1 = '1002671'
FIELD_ID_2 = '1002674'
FIELD_ID_3 = '1002680'
FIELD_ID_4 = '1002683'
FIELD_ID_5 = '1002686'
FIELD_ID_6 = '1002689'
FIELD_ID_7 = '1002692'
FIELD_ID_8 = '1002673'
FIELD_ID_9 = '1002676'
FIELD_ID_10 = '1002679'
FIELD_ID_11 = '1002682'
FIELD_ID_12 = '1002685'
FIELD_ID_13 = '1002688'
FIELD_ID_14 = '1002691'
FIELD_ID_15 = '1002694'
FIELD_ID_16 = '1002697'
FIELD_ID_17 = '1002698'
FIELD_ID_18 = '1002696'
FIELD_ID_20 = '1002910'
FIELD_ID_21 = '1002928'
FIELD_ID_22 = '1002929'
FIELD_ID_OCR = '1004229'

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

def createEntity_unconfirmed(OCR, NAME, FIRST, LAST, COMPANY, DEPART1, DEPART2, TITLE1, TITLE2, TITLE3, MOBILE1, MOBILE2, TEL1, TEL2, FAX1, FAX2, EMAIL1, EMAIL2, ADDRESS1, ADDRESS2, WEBSITE, url):
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
        FIELD_ID_20: url,
        FIELD_ID_21: FIRST,
        FIELD_ID_22: LAST,
        FIELD_ID_OCR: OCR
    }

    response = requests.post(API_ENDPOINT_LISTING_PAGE, params=params, json=data, headers={'Authorization': 'Basic '+API_KEY})
    print(response.text)