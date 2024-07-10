import requests
from dotenv import load_dotenv
import os

def get_data_by_tag(target_tag):
    # Example URL and API Key for Ragic, replace with actual values

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
    print(response.text)
    
    data = response.json()
    customers = []

    for key, value in data.items():
        name = value.get('Name', '')
        email = value.get('Email 1', '')
        tags = ', '.join(value.get('Type', []))

        if target_tag in tags:
            customers.append({'name': name, 'email': email, 'tags': tags})

    for customer in customers:
        print(f"姓名: {customer['name']}\n電子郵件: {customer['email']}\n標籤: {customer['tags']}")
        print("------------------------------")

    return customers

# Example usage
#customers = get_data_by_tag('朋友')
#print(customers)
