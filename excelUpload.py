import pandas as pd
import requests
from dotenv import load_dotenv
import sys
import os

SERVER_URL = 'ap12.ragic.com'
ACCOUNT_NAME = 'cancerfree'
TAB = 'forms5'
SHEET_INDEX = '4'

FIELD_NAME = '1001976' #姓名
FIELD_FIRSTNAME = '1002926' #名字
FIELD_FIRSTNAME_PINYIN = '1003168' #名字拼音或音標
FIELD_LASTNAME = '1002927' #姓
FIELD_LASTNAME_PINYIN = '1003170' #姓氏拼音或音標
FIELD_INDUSTRY = '1003172' #行業
FIELD_LOCATION = '1003174' #所在地
FIELD_COMPANY1 = '1001977' #公司1
FIELD_DEPARTMENT1 = '1001982' #部門1
FIELD_TITLE1 = '1001984' #職位1
FIELD_COMPANY2 = '1003176' #公司2
FIELD_DEPARTMENT2 = '1001983' #部門2
FIELD_TITLE2 = '1001985' #職位2
FIELD_COMPANY_OTHER = '1003178' #公司(其他)
FIELD_DEPARTMENT_OTHER = '1003180' #部門(其他)
FIELD_TITLE3 = '1003182' #職位(其他)
FIELD_MOBILE1 = '1001988' #手機1
FIELD_MOBILE2 = '1001990' #手機2
FIELD_MOBILE_OTHER = '1003183' #手機(其他)
FIELD_TEL1 = '1001992' #電話1
FIELD_TEL2 = '1001994' #電話2
FIELD_TEL_OTHER = '1003184' #電話(其他)
FIELD_FAX1 = '1001996' #傳真1
FIELD_FAX2 = '1001998' #傳真2
FIELD_FAX_OTHER = '1003185' #傳真(其他)
FIELD_EMAIL1 = '1001989' #電子郵件1
FIELD_EMAIL2 = '1001991' #電子郵件2
FIELD_EMAIL_OTHER = '1003186' #電子郵件(其他)
FIELD_ADDRESS1 = '1001993' #地址1
FIELD_ADDRESS2 = '1001995' #地址2
FIELD_ADDRESS_OTHER = '1003187' #地址(其他)
FIELD_WEBSITE = '1001997' #網頁
FIELD_CHAT_ACCOUNT = '1003169' #聊天軟件賬號
FIELD_SOCIAL_ACCOUNT = '1003171' #社交帳戶
FIELD_NICKNAME = '1003173' #暱稱
FIELD_BIRTHDAY = '1003175' #生日
FIELD_ANNIVERSARY = '1003177' #紀念日
FIELD_TYPE = '1002025' #分組
FIELD_DESCRIPTION1 = '1001987' #備註1
FIELD_DESCRIPTION2 = '1003179' #備註2
FIELD_DESCRIPTION3 = '1003181' #備註3

load_dotenv()
API_KEY = os.getenv('RAGIC_API_KEY')

API_ENDPOINT_LISTING_PAGE = f'https://{SERVER_URL}/{ACCOUNT_NAME}/{TAB}/{SHEET_INDEX}'

params = {
    'api': '',
    'v': 3
}

def createEntity(NAME, FIRSTNAME, FIRSTNAME_PINYIN, LASTNAME, LASTNAME_PINYIN, INDUSTRY, LOCATION, COMPANY1, DEPARTMENT1, TITLE1, COMPANY2, DEPARTMENT2, TITLE2, COMPANY_OTHER, DEPARTMENT_OTHER, TITLE3, MOBILE1, MOBILE2, MOBILE_OTHER, TEL1, TEL2, TEL_OTHER, FAX1, FAX2, FAX_OTHER, EMAIL1, EMAIL2, EMAIL_OTHER, ADDRESS1, ADDRESS2, ADDRESS_OTHER, WEBSITE, CHAT_ACCOUNT, SOCIAL_ACCOUNT, NICKNAME, BIRTHDAY, ANNIVERSARY, TYPE, DESCRIPTION1, DESCRIPTION2, DESCRIPTION3):
    print("upload to Ragic...")
    data = {
        FIELD_NAME : NAME, #姓名
        FIELD_FIRSTNAME : FIRSTNAME, #名字
        FIELD_FIRSTNAME_PINYIN : FIRSTNAME_PINYIN, #名字拼音或音標
        FIELD_LASTNAME : LASTNAME, #姓
        FIELD_LASTNAME_PINYIN : LASTNAME_PINYIN, #姓氏拼音或音標
        FIELD_INDUSTRY : INDUSTRY, #行業
        FIELD_LOCATION : LOCATION, #所在地
        FIELD_COMPANY1 : COMPANY1, #公司1
        FIELD_DEPARTMENT1 : DEPARTMENT1, #部門1
        FIELD_TITLE1 : TITLE1, #職位1
        FIELD_COMPANY2 : COMPANY2, #公司2
        FIELD_DEPARTMENT2 : DEPARTMENT2, #部門2
        FIELD_TITLE2 : TITLE2, #職位2
        FIELD_COMPANY_OTHER : COMPANY_OTHER, #公司(其他)
        FIELD_DEPARTMENT_OTHER : DEPARTMENT_OTHER, #部門(其他)
        FIELD_TITLE3 : TITLE3, #職位(其他)
        FIELD_MOBILE1 : MOBILE1, #手機1
        FIELD_MOBILE2 : MOBILE2, #手機2
        FIELD_MOBILE_OTHER : MOBILE_OTHER, #手機(其他)
        FIELD_TEL1 : TEL1, #電話1
        FIELD_TEL2 : TEL2, #電話2
        FIELD_TEL_OTHER : TEL_OTHER, #電話(其他)
        FIELD_FAX1 : FAX1, #傳真1
        FIELD_FAX2 : FAX2, #傳真2
        FIELD_FAX_OTHER : FAX_OTHER, #傳真(其他)
        FIELD_EMAIL1 : EMAIL1, #電子郵件1
        FIELD_EMAIL2 : EMAIL2, #電子郵件2
        FIELD_EMAIL_OTHER : EMAIL_OTHER, #電子郵件(其他)
        FIELD_ADDRESS1 : ADDRESS1, #地址1
        FIELD_ADDRESS2 : ADDRESS2, #地址2
        FIELD_ADDRESS_OTHER : ADDRESS_OTHER, #地址(其他)
        FIELD_WEBSITE : WEBSITE, #網頁
        FIELD_CHAT_ACCOUNT : CHAT_ACCOUNT, #聊天軟件賬號
        FIELD_SOCIAL_ACCOUNT : SOCIAL_ACCOUNT, #社交帳戶
        FIELD_NICKNAME : NICKNAME, #暱稱
        FIELD_BIRTHDAY : BIRTHDAY, #生日
        FIELD_ANNIVERSARY : ANNIVERSARY, #紀念日
        FIELD_TYPE : TYPE, #分組
        FIELD_DESCRIPTION1 : DESCRIPTION1, #備註1
        FIELD_DESCRIPTION2 : DESCRIPTION2, #備註2
        FIELD_DESCRIPTION3 : DESCRIPTION3, #備註3
    }

    response = requests.post(API_ENDPOINT_LISTING_PAGE, params=params, json=data, headers={'Authorization': 'Basic '+API_KEY})
    print(response.text)

def excel(file_path):
    print(f"Processing file: {file_path}")

    try:
        # 讀取 Excel 文件
        df = pd.read_excel(file_path, skiprows=1, engine='openpyxl')
        
        # 更好的空值處理
        df = df.fillna('')
        
        for index, row in df.iterrows():
            # 將所有值轉換為字符串,並處理特殊數值
            row = row.apply(lambda x: '' if pd.isna(x) else 
                            str(x) if not isinstance(x, float) else 
                            str(int(x)) if x.is_integer() else str(x))
            
            variables = row.tolist()  # Convert the row to a list
                
            # Store values into specific variables (adjust according to your needs)
            CREATION_DATE, NAME, FIRSTNAME, FIRSTNAME_PINYIN, LASTNAME, LASTNAME_PINYIN, \
            INDUSTRY, LOCATION, COMPANY1, DEPARTMENT1, TITLE1, COMPANY2, DEPARTMENT2, TITLE2, \
            COMPANY_OTHER, DEPARTMENT_OTHER, TITLE3, MOBILE1, MOBILE2, MOBILE_OTHER, TEL1, \
            TEL2, TEL_OTHER, FAX1, FAX2, FAX_OTHER, EMAIL1, EMAIL2, EMAIL_OTHER, ADDRESS1, \
            ADDRESS2, ADDRESS_OTHER, WEBSITE, CHAT_ACCOUNT, SOCIAL_ACCOUNT, NICKNAME, BIRTHDAY, \
            ANNIVERSARY, TYPE, DESCRIPTION1, DESCRIPTION2, DESCRIPTION3 = variables[:43]  # Adjust the number of variables if needed

            # Print extracted data for debugging or processing
            print(f"CREATION_DATE: {CREATION_DATE}")
            print(f"NAME: {NAME}")
            print(f"FIRSTNAME: {FIRSTNAME}")
            print(f"FIRSTNAME_PINYIN: {FIRSTNAME_PINYIN}")
            print(f"LASTNAME: {LASTNAME}")
            print(f"LASTNAME_PINYIN: {LASTNAME_PINYIN}")
            print(f"INDUSTRY: {INDUSTRY}")
            print(f"LOCATION: {LOCATION}")
            print(f"COMPANY1: {COMPANY1}")
            print(f"DEPARTMENT1: {DEPARTMENT1}")
            print(f"TITLE1: {TITLE1}")
            print(f"COMPANY2: {COMPANY2}")
            print(f"DEPARTMENT2: {DEPARTMENT2}")
            print(f"TITLE2: {TITLE2}")
            print(f"COMPANY_OTHER: {COMPANY_OTHER}")
            print(f"DEPARTMENT_OTHER: {DEPARTMENT_OTHER}")
            print(f"TITLE3: {TITLE3}")
            print(f"MOBILE1: {MOBILE1}")
            print(f"MOBILE2: {MOBILE2}")
            print(f"MOBILE_OTHER: {MOBILE_OTHER}")
            print(f"TEL1: {TEL1}")
            print(f"TEL2: {TEL2}")
            print(f"TEL_OTHER: {TEL_OTHER}")
            print(f"FAX1: {FAX1}")
            print(f"FAX2: {FAX2}")
            print(f"FAX_OTHER: {FAX_OTHER}")
            print(f"EMAIL1: {EMAIL1}")
            print(f"EMAIL2: {EMAIL2}")
            print(f"EMAIL_OTHER: {EMAIL_OTHER}")
            print(f"ADDRESS1: {ADDRESS1}")
            print(f"ADDRESS2: {ADDRESS2}")
            print(f"ADDRESS_OTHER: {ADDRESS_OTHER}")
            print(f"WEBSITE: {WEBSITE}")
            print(f"CHAT_ACCOUNT: {CHAT_ACCOUNT}")
            print(f"SOCIAL_ACCOUNT: {SOCIAL_ACCOUNT}")
            print(f"NICKNAME: {NICKNAME}")
            print(f"BIRTHDAY: {BIRTHDAY}")
            print(f"ANNIVERSARY: {ANNIVERSARY}")
            print(f"TYPE: {TYPE}")
            print(f"DESCRIPTION1: {DESCRIPTION1}")
            print(f"DESCRIPTION2: {DESCRIPTION2}")
            print(f"DESCRIPTION3: {DESCRIPTION3}")
            print()

            createEntity(NAME, FIRSTNAME, FIRSTNAME_PINYIN, LASTNAME, LASTNAME_PINYIN, INDUSTRY, LOCATION, COMPANY1, DEPARTMENT1, TITLE1, COMPANY2, DEPARTMENT2, TITLE2, COMPANY_OTHER, DEPARTMENT_OTHER, TITLE3, MOBILE1, MOBILE2, MOBILE_OTHER, TEL1, TEL2, TEL_OTHER, FAX1, FAX2, FAX_OTHER, EMAIL1, EMAIL2, EMAIL_OTHER, ADDRESS1, ADDRESS2, ADDRESS_OTHER, WEBSITE, CHAT_ACCOUNT, SOCIAL_ACCOUNT, NICKNAME, BIRTHDAY, ANNIVERSARY, TYPE, DESCRIPTION1, DESCRIPTION2, DESCRIPTION3)
        
        return 1

    except Exception as e:
        print(f"An error occurred: {e}")
        return 0

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


