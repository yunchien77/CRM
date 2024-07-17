import os
import msal
import json
import requests
import webbrowser
from dotenv import load_dotenv

load_dotenv()

class FileSystemTokenCache(msal.SerializableTokenCache):
    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path
        self.load_cache()

    def load_cache(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r') as file:
                cache_data = file.read()
                if cache_data:
                    self.deserialize(cache_data)

    def save_cache(self):
        with open(self.file_path, 'w') as file:
            file.write(self.serialize())

    def add(self, event):
        super().add(event)
        self.save_cache()

    def remove(self, event, key):
        super().remove(event, key)
        self.save_cache()

def get_access_token(app, scopes):
    accounts = app.get_accounts()
    result = None
    if accounts:
        result = app.acquire_token_silent(scopes, account=accounts[0])

    if not result:
        flow = app.initiate_device_flow(scopes=scopes)
        print(flow['message'])
        webbrowser.open(flow['verification_uri'])
        result = app.acquire_token_by_device_flow(flow)

    if "access_token" in result:
        return result['access_token']
    else:
        print(result.get("error"))
        print(result.get("error_description"))
        return None

def upload_file_to_onedrive(access_token, file_path, file_name, folder_path):
    upload_url = f"https://graph.microsoft.com/v1.0/me/drive/root:/{folder_path}/{file_name}:/content"

    with open(file_path, 'rb') as upload:
        file_content = upload.read()

    headers = {
        'Authorization': 'Bearer ' + access_token,
        'Content-Type': 'application/octet-stream'
    }
    response = requests.put(upload_url, headers=headers, data=file_content)

    if response.status_code == 201 or response.status_code == 200:
        print(f"File '{file_name}' uploaded successfully to folder '{folder_path}'.")
        file_info = response.json()
        print(f"File uploaded to: {file_info.get('parentReference', {}).get('path', 'Unknown location')}")
        print(f"Web URL: {file_info.get('webUrl')}")
        return file_info.get('webUrl')
    else:
        print(f"Error uploading file. Status code: {response.status_code}")
        print(response.text)
        return 

def uploadFile(file_path):
    print(file_path)
    # 設置您的 Azure 應用程序憑證
    client_id = os.getenv('CILENT_ID')
    tenant_id = os.getenv('TENANT_ID')
    scopes = ['https://graph.microsoft.com/Files.ReadWrite.All']

    # 設置 token 緩存
    cache = FileSystemTokenCache('./token_cache.json')

    # 創建 MSAL 應用程序
    app = msal.PublicClientApplication(
        client_id,
        authority=f"https://login.microsoftonline.com/{tenant_id}",
        token_cache=cache
    )

    # 獲取訪問 token
    access_token = get_access_token(app, scopes)
    if not access_token:
        print("Failed to acquire access token.")
        return
        
    if not os.path.exists(file_path):
        print("File does not exist. Please enter a valid file path.")
        return
    else:
        file_name = os.path.basename(file_path)
        print(file_name)
        folder_path = "BusinessCards"
            
        url = upload_file_to_onedrive(access_token, file_path, file_name, folder_path)
        return url

