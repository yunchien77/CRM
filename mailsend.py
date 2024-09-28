import os
import requests
import base64
import json
import smtplib
from msal import ConfidentialClientApplication
from getpass import getpass

# Microsoft 認證設定
CLIENT_ID = "7fcb9abb-55cb-466d-8aa2-2125a46ff767"
CLIENT_SECRET = "G4L8Q~dzlRo2G4wdTadGrr3c9nfv3M76snxV0a2F"
TENANT_ID = "87545bf3-2cb8-410a-a96c-64b5dca46d4c"
SCOPES = ['https://graph.microsoft.com/.default']

def authenticate(email, password):
    # 使用 MSAL 進行認證
    msal_app = ConfidentialClientApplication(
        CLIENT_ID,
        authority=f"https://login.microsoftonline.com/{TENANT_ID}",
        client_credential=CLIENT_SECRET
    )
    
    # 獲取 token
    result = msal_app.acquire_token_by_username_password(
        username=email,
        password=password,
        scopes=SCOPES
    )

    if 'access_token' in result:
        print("Token 獲取成功")
        return result['access_token']
    else:
        print("獲取 token 失敗:", result.get('error'), result.get('error_description'))
        return None

def send_email(access_token, to_email, subject, content):
    # 準備郵件內容
    message = {
        "message": {
            "subject": subject,
            "body": {
                "contentType": "HTML",
                "content": content
            },
            "toRecipients": [
                {
                    "emailAddress": {
                        "address": to_email
                    }
                }
            ],
            "from": {
                "emailAddress": {
                    "address": "support@cancerfree.io"  # 自定義發件人地址
                }
            },
            "replyTo": [
                {
                    "emailAddress": {
                        "address": "yunchien.yeh@gmail.com"  # 自定義回覆地址
                    }
                }
            ]
        },
        "saveToSentItems": "true"
    }

    # 發送郵件
    endpoint = f'https://graph.microsoft.com/v1.0/users/cherry.yeh@cancerfree.io/sendMail'
    response = requests.post(
        endpoint,
        headers={
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        },
        json=message
    )

    if response.status_code == 202:
        print("郵件發送成功")
    else:
        print("發送郵件失敗:", response.text)

if __name__ == "__main__":
    email = input("請輸入你的電子郵件: ")
    password = getpass("請輸入你的密碼: ")
    
    access_token = authenticate(email, password)
    
    if access_token:
        to_email = input("請輸入收件者電子郵件: ")
        subject = input("請輸入郵件主題: ")
        content = input("請輸入郵件內容: ")
        
        send_email(access_token, to_email, subject, content)
