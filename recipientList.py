import requests
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv('RAGIC_API_KEY')

SERVER_URL = 'ap12.ragic.com'
ACCOUNT_NAME = 'cancerfree'
TAB = 'forms5'
SHEET_INDEX = '4'
API_ENDPOINT_LISTING_PAGE = f'https://{SERVER_URL}/{ACCOUNT_NAME}/{TAB}/{SHEET_INDEX}'

def get_recipient_info(target_tag):
    params = {
        'api': '',
        'v': 3,
        'subtables': 0,
        'where': '1002025,eq,'+target_tag
    }

    response = requests.get(API_ENDPOINT_LISTING_PAGE, params=params, headers={'Authorization': 'Basic '+API_KEY})
    print(response.text)
    
    data = response.json()
    customers = []

    for key, value in data.items():
        id = value.get('ID', '')
        name = value.get('Name', '')
        last = value.get('Last Name', '')
        title = value.get('Title 1', '')
        email = value.get('Email 1', '')
        tags = ', '.join(value.get('Type', []))
        etitle = value.get('Email Title', '')

        if etitle == '':
            if name != '' and title != '':
                etitle = last + title
            else: 
                etitle = name

        if target_tag in tags:
            customers.append({'id': id, 'name': name, 'email': email, 'tags': tags, 'title': title, 'emailtitle': etitle})

    for customer in customers:
        print(f"ID: {customer['id']}\n抬頭: {customer['emailtitle']}\n姓名: {customer['name']}\n電子郵件: {customer['email']}\n標籤: {customer['tags']}")

    return customers


def get_recipient_individual():
    params = {
        'api': '',
        'v': 3,
        'subtables': 0,
    }

    response = requests.get(API_ENDPOINT_LISTING_PAGE, params=params, headers={'Authorization': 'Basic '+API_KEY})
    #print(response.text)
    
    data = response.json()
    customers_list = []

    for key, value in data.items():
        id = value.get('ID', '')
        name = value.get('Name', '')
        last = value.get('Last Name', '')
        title = value.get('Title 1', '')
        email = value.get('Email 1', '')
        etitle = value.get('Email Title', '')

        if etitle == '':
            if name != '' and title != '':
                etitle = last + title
            else: 
                etitle = name

        customers_list.append({'id': id, 'name': name, 'email': email, 'title': title, 'emailtitle': etitle})

    # for customer in customers_list:
    #     print(f"ID: {customer['id']}\n抬頭: {customer['emailtitle']}\n姓名: {customer['name']}\n電子郵件: {customer['email']}\n")

    return customers_list
    #print(data)

# Example usage
#customers = get_recipient_info('朋友')
#print(customers)


#get_recipient_individual()