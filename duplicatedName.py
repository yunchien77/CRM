import requests
from dotenv import load_dotenv
import os

def searchName(name):
    load_dotenv()
    API_KEY = os.getenv('RAGIC_API_KEY')

    SERVER_URL = 'ap12.ragic.com'
    ACCOUNT_NAME = 'cancerfree'
    TAB = 'forms5'
    SHEET_INDEX = '4'

    params = {
        'api': '',
        'v': 3,
        'subtables': 0,
        'where': '1001976,eq,'+name
    }

    API_ENDPOINT_LISTING_PAGE = f'https://{SERVER_URL}/{ACCOUNT_NAME}/{TAB}/{SHEET_INDEX}'

    response = requests.get(API_ENDPOINT_LISTING_PAGE, params=params, headers={'Authorization': 'Basic '+API_KEY})
    print(response.text)

    data = response.json()
    
    if data:
        duplicate_records = []
        for record_id, record in data.items():
            duplicate_records.append({
                '姓名': record['姓名'],
                '公司': record['公司'],
                '職稱1': record['職稱1']
            })

        for record in duplicate_records:
            print(f"姓名: {record['姓名']}, 公司: {record['公司']}, 職稱: {record['職稱1']}")
        return duplicate_records

    else:
        print('empty data')
        return 0


searchName('陳柏翰')
