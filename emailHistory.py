import requests
from dotenv import load_dotenv
import os

SERVER_URL = 'ap12.ragic.com'
ACCOUNT_NAME = 'cancerfree'
TAB = 'forms5'
SHEET_INDEX = '12'

FIELD_id = '1002663'
FIELD_date = '1002656'
FIELD_method = '1002657'
FIELD_person = '1002659'
FIELD_content = '1002660'
FIELD_name = '1002923'
FIELD_title = '1002924'

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

def uploadHistory(customer, email_subject, email_content, date, username):
    id = customer['id']
    username = username.split('@')[0]
    name = customer['name']
    title = customer['title1']

    data = {
        FIELD_id: id,
        FIELD_date: date,        
        FIELD_method: '郵件',     
        FIELD_person: username,       
        FIELD_content: email_subject+'\n'+email_content,   
        FIELD_name: name,
        FIELD_title: title    
    }

    response = requests.post(API_ENDPOINT_LISTING_PAGE, params=params, json=data, headers={'Authorization': 'Basic '+API_KEY})
    print(response.text)