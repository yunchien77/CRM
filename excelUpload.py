import pandas as pd
import requests
from dotenv import load_dotenv
import sys
import os

SERVER_URL = 'ap12.ragic.com'
ACCOUNT_NAME = 'cancerfree'
TAB = 'forms5'
SHEET_INDEX = '4'

FIELD_NAME = '1001976' 
FIELD_LASTNAME = '1002927' 
FIELD_LASTNAME_PINYIN  = '1003170' 
FIELD_FIRSTNAME = '1002926' 
FIELD_FIRSTNAME_PINYIN = '1003168' 
FIELD_GENDER = '1002664' 
FIELD_WHEN  = '1002665' 
FIELD_WHERE = '1002666' 
FIELD_COMPANY1  = '1001977' 
FIELD_COMPANY2 = '1003176' 
FIELD_HOSPITAL  = '1004230' 
FIELD_TITLE1  = '1001984' 
FIELD_TITLE2 = '1001985' 
FIELD_DEPARTMENT1  = '1001982' 
FIELD_DEPARTMENT2 = '1001983' 
FIELD_PRIORITY = '1002668' 
FIELD_TYPE = '1002025' 
FIELD_CUSTOMER_TYPE = '1003750' 
FIELD_MOBILE1 = '1001988' 
FIELD_MOBILE2 = '1001990' 
FIELD_TEL1 = '1001992' 
FIELD_TEL2 = '1001994' 
FIELD_FAX1 = '1001996' 
FIELD_FAX2  = '1001998' 
FIELD_EMAIL_TITLE = '1002930' 
FIELD_EMAIL1 = '1001989' 
FIELD_EMAIL2 = '1001991' 
FIELD_COUNTRY_CITY = '1003174' 
FIELD_ADDRESS1 = '1001993' 
FIELD_ADDRESS2 = '1001995' 
FIELD_LINKEDIN = '1002669' 
FIELD_FOCUS_AREA = '1003172' 
FIELD_WEBSITE = '1001997' 
FIELD_DESCRIPTION = '1001987' 

load_dotenv()
API_KEY = os.getenv('RAGIC_API_KEY')

API_ENDPOINT_LISTING_PAGE = f'https://{SERVER_URL}/{ACCOUNT_NAME}/{TAB}/{SHEET_INDEX}'

params = {
    'api': '',
    'v': 3
}

def createEntity(NAME, LASTNAME, LASTNAME_PINYIN, FIRSTNAME, FIRSTNAME_PINYIN, GENDER, WHEN, WHERE, COMPANY1, COMPANY2, HOSPITAL, TITLE1, TITLE2, DEPARTMENT1, DEPARTMENT2, PRIORITY, TYPE, CUSTOMER_TYPE, MOBILE1, MOBILE2, TEL1, TEL2, FAX1, FAX2, EMAIL_TITLE, EMAIL1, EMAIL2, COUNTRY_CITY, ADDRESS1, ADDRESS2, LINKEDIN, FOCUS_AREA, WEBSITE, DESCRIPTION):
    print("upload to Ragic...")
    data = {
        FIELD_NAME : NAME, 
        FIELD_LASTNAME : LASTNAME, 
        FIELD_LASTNAME_PINYIN : LASTNAME_PINYIN, 
        FIELD_FIRSTNAME : FIRSTNAME, 
        FIELD_FIRSTNAME_PINYIN : FIRSTNAME_PINYIN, 
        FIELD_GENDER : GENDER, 
        FIELD_WHEN : WHEN, 
        FIELD_WHERE : WHERE, 
        FIELD_COMPANY1 : COMPANY1, 
        FIELD_COMPANY2 : COMPANY2, 
        FIELD_HOSPITAL : HOSPITAL, 
        FIELD_TITLE1 : TITLE1, 
        FIELD_TITLE2 : TITLE2, 
        FIELD_DEPARTMENT1 : DEPARTMENT1, 
        FIELD_DEPARTMENT2 : DEPARTMENT2, 
        FIELD_PRIORITY : PRIORITY, 
        FIELD_TYPE : TYPE, 
        FIELD_CUSTOMER_TYPE : CUSTOMER_TYPE, 
        FIELD_MOBILE1 : MOBILE1, 
        FIELD_MOBILE2 : MOBILE2, 
        FIELD_TEL1 : TEL1, 
        FIELD_TEL2 : TEL2, 
        FIELD_FAX1 : FAX1, 
        FIELD_FAX2 : FAX2, 
        FIELD_EMAIL_TITLE : EMAIL_TITLE, 
        FIELD_EMAIL1 : EMAIL1, 
        FIELD_EMAIL2 : EMAIL2, 
        FIELD_COUNTRY_CITY : COUNTRY_CITY, 
        FIELD_ADDRESS1 : ADDRESS1, 
        FIELD_ADDRESS2 : ADDRESS2, 
        FIELD_LINKEDIN : LINKEDIN, 
        FIELD_FOCUS_AREA : FOCUS_AREA, 
        FIELD_WEBSITE : WEBSITE, 
        FIELD_DESCRIPTION : DESCRIPTION
    }

    response = requests.post(API_ENDPOINT_LISTING_PAGE, params=params, json=data, headers={'Authorization': 'Basic '+API_KEY})
    print(response.text)

def excel(file_path):
    print(f"Processing file: {file_path}")

    try:
        # 讀取 Excel 文件
        # df = pd.read_excel(file_path, skiprows=1, engine='openpyxl')
        df = pd.read_excel(file_path, engine='openpyxl')
        
        # 更好的空值處理
        df = df.fillna('')
        
        for index, row in df.iterrows():
            # 將所有值轉換為字符串,並處理特殊數值
            row = row.apply(lambda x: '' if pd.isna(x) else 
                            str(x) if not isinstance(x, float) else 
                            str(int(x)) if x.is_integer() else str(x))
            
            variables = row.tolist()  # Convert the row to a list
                
            # Store values into specific variables (adjust according to your needs)
            NAME, LASTNAME, LASTNAME_PINYIN, FIRSTNAME, FIRSTNAME_PINYIN, \
            GENDER, WHEN, WHERE, COMPANY1, COMPANY2, HOSPITAL, \
            TITLE1, TITLE2, DEPARTMENT1, DEPARTMENT2, \
            PRIORITY, TYPE, CUSTOMER_TYPE, \
            MOBILE1, MOBILE2, TEL1, TEL2, FAX1, FAX2, \
            EMAIL_TITLE, EMAIL1, EMAIL2, \
            COUNTRY_CITY, ADDRESS1, ADDRESS2, \
            LINKEDIN, FOCUS_AREA, WEBSITE, DESCRIPTION = variables[:35]  # Adjust the number of variables if needed

            createEntity(NAME, LASTNAME, LASTNAME_PINYIN, FIRSTNAME, FIRSTNAME_PINYIN, GENDER, WHEN, WHERE, COMPANY1, COMPANY2, HOSPITAL, TITLE1, TITLE2, DEPARTMENT1, DEPARTMENT2, PRIORITY, TYPE, CUSTOMER_TYPE, MOBILE1, MOBILE2, TEL1, TEL2, FAX1, FAX2, EMAIL_TITLE, EMAIL1, EMAIL2, COUNTRY_CITY, ADDRESS1, ADDRESS2, LINKEDIN, FOCUS_AREA, WEBSITE, DESCRIPTION)
        return 1

    except Exception as e:
        print(f"An error occurred in excel function: {e}")
        raise

# if __name__ == "__main__":
#     if len(sys.argv) != 2:
#         print("Usage: python excelUpload.py <path_to_excel_file>")
#         sys.exit(1)
    
#     file_path = sys.argv[1]
#     result = excel(file_path)
#     if result:
#         print("Upload completed successfully.")
#     else:
#         print("Upload failed.")


# excel("img/test.xlsx")