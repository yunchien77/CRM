import requests
from dotenv import load_dotenv
import os

def getAllPeople():
    load_dotenv()
    API_KEY = 'b0hPOFAzbkRaNzFJV1F4RzNkRTA1Sko3QS9BMVlrbzdUZWtzVi9FcGtzejVFTzlDMGxHMnMwVzVQaFpEcGdzT29JOENFVy9qNzZnPQ=='


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
    #print(response.text)

    data = response.json()
    '''
    if data:
        people_list = []
        for key, value in data.items():
            if value['相關連結'] == '':
                people_list.append({
                    'id': value['ID'],
                    'name': value['Name'],
                    'company': value['Company']
                })
                count = 0
    for i in people_list:
        print(i)
        count+=1
    print(count)

    '''

    if data:
        people_list = []
        for key, value in data.items():
            if value['相關連結'] == '':
                search_str = value['Name'] + ' ' + value['Company']
                people_list.append({
                    "id": value['ID'],
                    "search": search_str
                })
    '''
    for i in people_list:
        print(i['id'], i['search'])
    '''
    return people_list
