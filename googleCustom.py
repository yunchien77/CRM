import requests
from getData import getAllPeopleSeperate, updateData
from dotenv import load_dotenv
import os

load_dotenv()

def get_first_linkedin_result(query):
    print(query)
    try:
        API_KEY = os.getenv('CSE_API_KEY')
        CX = os.getenv('CSE_CX') 
        QUERY = query

        url = f"https://www.googleapis.com/customsearch/v1?q={QUERY}&key={API_KEY}&cx={CX}"

        response = requests.get(url)
        data = response.json()

        if 'items' in data and len(data['items']) > 0:
            # 獲取第一筆資料
            item = data['items'][0]
            print("Title:", item['title'])
            print("URL:", item['link'])
            title = item['title']
            link = item['link']
            # print("Display URL:", item['displayLink'])
            # print("Snippet:", item['snippet'])
            return f'{title} - {link}'
        else:
            print("???????????")
            return None
    except requests.exceptions.RequestException as e:
        print(f'API request error: {e}')
        return None

def customSearch():
    try:
        people_list = getAllPeopleSeperate()
        for person in people_list:
            name = person['name']
            company = person['company']
            query = f'site:linkedin.com/in/ "{name}" "{company}"'
            result = get_first_linkedin_result(query)
            if result is None:
                print('No result found')
                updateData(person['id'], "not found")
            else:
                print(f'Found: {result}')
                updateData(person['id'], result)  # 更新資料到 Ragic
    except Exception as e:
        print(f'An error occurred: {e}')

if __name__ == "__main__":
    search()
