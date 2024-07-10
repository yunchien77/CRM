import requests
from dotenv import load_dotenv
import os

def get_taglist():
    load_dotenv()
    API_KEY = os.getenv('RAGIC_API_KEY')

    SERVER_URL = 'ap12.ragic.com'
    ACCOUNT_NAME = 'cancerfree'
    TAB = 'forms5'
    SHEET_INDEX = '4'

    params = {
        'api': '',
        'v': 3,
        'subtables': 0
    }

    API_ENDPOINT_LISTING_PAGE = f'https://{SERVER_URL}/{ACCOUNT_NAME}/{TAB}/{SHEET_INDEX}'

    response = requests.get(API_ENDPOINT_LISTING_PAGE, params=params, headers={'Authorization': 'Basic '+API_KEY})
    
    data = response.json()
    taglist = []

    for key, value in data.items():
        tags = value.get('標籤', [])
        for tag in tags:
            if tag not in taglist:
                taglist.append(tag)

    print(taglist)

    return taglist
