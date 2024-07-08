import openai
import json
from dotenv import load_dotenv
import os
#from image2Text import ocr_image

load_dotenv()

# OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')


def get_completion_from_messages(prompt, model="gpt-3.5-turbo", temperature=0, max_tokens=500):
    response = openai.ChatCompletion.create(
        model=model,
        messages=prompt,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return response.choices[0].message["content"]

delimiter = "####"
system_message = """
You will be provided with business card information. \
The information will be delimited with \
{{delimiter}} characters.
Classify each piece of information into categories \
such as Address, Phone Number, Name, etc. 
Each category in the json is "unique". If each category has multiple values, separate them with a slash (/). Don’t have duplicate categories.

JSON Format Example:
{
    "businessCard": [
        {
            "category": "Person Name",
            "value": "Name_value"
        },
        {
            "category": "Company Name",
            "value": "Company_value"
        },
        {
            "category": "Job Title",
            "value": "Title_value"
        },
        {
            "category": "Mobile Phone Number",
            "value": "Mobile_Phone_value"
        },
        {
            "category": "Telephone Number",
            "value": "Telephone_Number_value"
        },
        {
            "category": "Fax Number",
            "value": "Fax_Number_value"
        },
        {
            "category": "Email",
            "value": "Email_value"
        },
        {
            "category": "Address",
            "value": "Address_value"
        },
        {
            "category": "Website",
            "value": "Website_value"
        }
    ]
}

Categories:
- Person Name: The name of the person on the business card.
- Company Name: The name of the company associated with the person.
- Department: Department information (if available).
- Job Title: The job title or position of the person.
- Mobile Phone Number: The mobile phone number of the person.
- Telephone Number: The telephone number of the person.
- Fax Number: The fax number of the person.
- Email: The email address of the person.
- Address: The physical address of the person or company.
- Website: The website URL of the person or company.

If the provided information contains multiple "different" instances of email addresses, phone numbers, or addresses, ensure they are separated and classified accordingly in the output JSON.
For example, if the string is "example@gmail.com 886979666666", they will be classified into emails and mobile phone numbers.
If there is a string "beijing taipei", it will be classified into the address, and the values ​​will be separated by slashes(/), for example, beijing/taipei.
If there is information that does not fit into the above categories, you can ignore it in the output.
If multiple values ​​only differ in language but have the same value, the Tradionnal Chinese or English value will prevail.
"""

def remove_files(folder_path):
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            os.remove(file_path) 

def process_business_card(ocr_text):
    prompt = [
        {'role': 'system', 'content': system_message},
        {'role': 'user', 'content': f"{delimiter}{ocr_text}{delimiter}"},
    ]
    response = get_completion_from_messages(prompt)
    print(response)
    remove_files('img/')
    return split_data(response)

def split_data(response):
    NAME = None
    COMPANY = None
    DEPART1 = None
    DEPART2 = None
    TITLE1 = None
    TITLE2 = None
    TITLE3 = None
    MOBILE1 = None
    MOBILE2 = None
    TEL1 = None
    TEL2 = None
    FAX1 = None
    FAX2 = None
    EMAIL1 = None
    EMAIL2 = None
    ADDRESS1 = None
    ADDRESS2 = None
    WEBSITE = None

    response = json.loads(response)
    for entry in response['businessCard']:
        category = entry['category']
        value = entry['value']

        if category == 'Person Name':
            NAME = value
        elif category == 'Company Name':
            COMPANY = value
        elif category == 'Department':
            departments = value.split('/')
            if len(departments) >= 2:
                DEPART1 = departments[0]
                DEPART2 = departments[1]
            else:
                DEPART1 = value
        elif category == 'Job Title':
            titles = value.split('/')
            if len(titles) >= 1:
                TITLE1 = titles[0]
            if len(titles) >= 2:
                TITLE2 = titles[1]
            if len(titles) >= 3:
                TITLE3 = titles[2]
        elif category == 'Email':
            emails = value.split('/')
            if len(emails) >= 1:
                EMAIL1 = emails[0]
            if len(emails) >= 2:
                EMAIL2 = emails[1]
        elif category == 'Mobile Phone Number':
            phones = value.split('/')
            if len(phones) >= 1:
                MOBILE1 = phones[0]
            if len(phones) >= 2:
                MOBILE2 = phones[1]
        elif category == 'Telephone Number':
            tels = value.split('/')
            if len(tels) >= 1:
                TEL1 = tels[0]
            if len(tels) >= 2:
                TEL2 = tels[1]
        elif category == 'Fax Number':
            faxes = value.split('/')
            if len(faxes) >= 1:
                FAX1 = faxes[0]
            if len(faxes) >= 2:
                FAX2 = faxes[1]
        elif category == 'Address':
            addresses = value.split('/')
            if len(addresses) >= 1:
                ADDRESS1 = addresses[0]
            if len(addresses) >= 2:
                ADDRESS2 = addresses[1]
        elif category == 'Website':
            WEBSITE = value
    
    print("NAME:", NAME)
    print("COMPANY:", COMPANY)
    print("DEPARTMENT1:", DEPART1)
    print("DEPARTMENT2:", DEPART2)
    print("TITLE1:", TITLE1)
    print("TITLE2:", TITLE2)
    print("TITLE3:", TITLE3)
    print("MOBILE1:", MOBILE1)
    print("MOBILE2:", MOBILE2)
    print("TEL1:", TEL1)
    print("TEL2:", TEL2)
    print("FAX1:", FAX1)
    print("FAX2:", FAX2)
    print("EMAIL1:", EMAIL1)
    print("EMAIL2:", EMAIL2)
    print("ADDRESS1:", ADDRESS1)
    print("ADDRESS2:", ADDRESS2)
    print("WEBSITE:", WEBSITE)
    
    return NAME, COMPANY, DEPART1, DEPART2, TITLE1, TITLE2, TITLE3, MOBILE1, MOBILE2, TEL1, TEL2, FAX1, FAX2, EMAIL1, EMAIL2, ADDRESS1, ADDRESS2, WEBSITE
