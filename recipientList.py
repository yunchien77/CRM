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
    print(data)
    customers = []

    for key, value in data.items():
        id = value.get('ID', '')
        name = value.get('Name', '')
        last = value.get('Last Name', '')
        company = value.get('Company', '')
        title1 = value.get('Title 1', '')
        title2 = value.get('Title 2', '')
        title3 = value.get('Title 3', '')
        department1 = value.get('Department 1', '')
        department2 = value.get('Department 2', '')
        email = value.get('Email 1', '')
        tags = ', '.join(value.get('Type', []))
        etitle = value.get('Email Title', '')

        if etitle == '':
            if name != '' and title1 != '':
                etitle = last + ' ' + title1
            else: 
                etitle = name

        if email != "" and target_tag in tags:
            customers.append({'id': id, 'name': name, 'email': email, 'tags': tags, 'company': company, 'title1': title1, 'title2': title2, 'title3': title3, 'department1': department1, 'department2': department2, 'emailtitle': etitle})

    for customer in customers:
        print(f"ID: {customer['id']}\n抬頭: {customer['emailtitle']}\n姓名: {customer['name']}\n電子郵件: {customer['email']}\n標籤: {customer['tags']}")
        print(f"公司: {customer['company']}\n職稱1: {customer['title1']}\n職稱2: {customer['title2']}\n職稱3: {customer['title3']}\n部門1: {customer['department1']}\n部門2: {customer['department2']}")
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
        company = value.get('Company', '')
        title1 = value.get('Title 1', '')
        title2 = value.get('Title 2', '')
        title3 = value.get('Title 3', '')
        department1 = value.get('Department 1', '')
        department2 = value.get('Department 2', '')
        email = value.get('Email 1', '')
        tags = ', '.join(value.get('Type', []))
        etitle = value.get('Email Title', '')

        if etitle == '':
            if name != '' and title1 != '':
                etitle = last + ' ' + title1
            else: 
                etitle = name

        if email != "":
            customers_list.append({'id': id, 'name': name, 'email': email, 'tags': tags, 'company': company, 'title1': title1, 'title2': title2, 'title3': title3, 'department1': department1, 'department2': department2, 'emailtitle': etitle})

    # for customer in customers_list:
    #     print(f"ID: {customer['id']}\n抬頭: {customer['emailtitle']}\n姓名: {customer['name']}\n電子郵件: {customer['email']}\n")

    return customers_list
    #print(data)

# Example usage
# customers = get_recipient_info('測試')
#print(customers)


#get_recipient_individual()