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
You will be provided with business card information. 
The information will be delimited with {{delimiter}} characters.
Your task is to classify each piece of information into appropriate categories and output the result in a specific JSON format. Pay special attention to correctly identifying and classifying Person Name, Company Name, Department, and Job Title.

Guidelines:
1. Each category in the JSON should be unique.
2. If a category has multiple values, separate them with a slash (/).
3. If information doesn't fit into the predefined categories, you may ignore it.
5. If the provided information contains multiple "different" instances of email addresses, phone numbers, or addresses, ensure they are separated and classified accordingly in the output JSON. For example, if the string is "example@gmail.com 886979666666", they will be classified into emails and mobile phone numbers.

Specific instructions for key categories:
1. Person Name: Split the name into first name and last name.
   - For English names, the first name comes first, followed by the last name.
   - For Chinese names, the last name (family name) comes first, followed by the first name (given name).

2. Company Name: The name of the organization or business.

3. Department

4. Job Title: The person's role or position within the company.

5. Contact Information: Carefully distinguish between Mobile Phone, Telephone (office), and Fax numbers.

6. Address

7. Website

Output the classified information in the following JSON format:
{
    "businessCard": [
        {
            "category": "Person Name",
            "value": "Name_value"
        },
        {
            "category": "First Name",
            "value": "FirstName_value"
        },
        {
            "category": "Last Name",
            "value": "LastName_value"
        },
        {
            "category": "Company Name",
            "value": "Company_value"
        },
        {
            "category": "Department",
            "value": "Department_value"
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
"""
 

def process_business_card(ocr_text):
    prompt = [
        {'role': 'system', 'content': system_message},
        {'role': 'user', 'content': f"{delimiter}{ocr_text}{delimiter}"},
    ]
    response = get_completion_from_messages(prompt)
    print(response)
    
    return split_data(response)

def split_data(response):
    NAME = None
    FIRST_NAME= None
    LAST_NAME=None
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
        elif category == 'First Name':
            FIRST_NAME = value
        elif category == 'Last Name':
            LAST_NAME = value
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
    print("FIRST NAME:", FIRST_NAME)
    print("LAST NAME:", LAST_NAME)
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
    
    return NAME, FIRST_NAME, LAST_NAME, COMPANY, DEPART1, DEPART2, TITLE1, TITLE2, TITLE3, MOBILE1, MOBILE2, TEL1, TEL2, FAX1, FAX2, EMAIL1, EMAIL2, ADDRESS1, ADDRESS2, WEBSITE
