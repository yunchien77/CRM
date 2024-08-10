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
        # print(flow['message'])
        webbrowser.open(flow['verification_uri'])
        result = app.acquire_token_by_device_flow(flow)

    if "access_token" in result:
        return result['access_token']
    else:
        print(result.get("error"))
        print(result.get("error_description"))
        return None

# 原本上傳到我自己的資料夾
# def upload_file_to_onedrive(access_token, file_path, file_name, folder_path):
#     upload_url = f"https://graph.microsoft.com/v1.0/me/drive/root:/{folder_path}/{file_name}:/content"
#     #upload_url = f"https://cancerfree-my.sharepoint.com/personal/cherry_yeh_cancerfree_io/Documents/{folder_path}/{file_name}:/content"

#     with open(file_path, 'rb') as upload:
#         file_content = upload.read()

#     headers = {
#         'Authorization': 'Bearer ' + access_token,
#         'Content-Type': 'application/octet-stream'
#     }
#     response = requests.put(upload_url, headers=headers, data=file_content)

#     if response.status_code == 201 or response.status_code == 200:
#         print(f"File '{file_name}' uploaded successfully to folder '{folder_path}'.")
#         file_info = response.json()
#         print(f"File uploaded to: {file_info.get('parentReference', {}).get('path', 'Unknown location')}")
#         print(f"Web URL: {file_info.get('webUrl')}")
#         return file_info.get('webUrl')
#     else:
#         print(f"Error uploading file. Status code: {response.status_code}")
#         print(response.text)
#         return 

def upload_file_to_onedrive(access_token, file_path, file_name, drive_id, folder_id):
    upload_url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/items/{folder_id}:/{file_name}:/content"

    with open(file_path, 'rb') as upload:
        file_content = upload.read()

    headers = {
        'Authorization': 'Bearer ' + access_token,
        'Content-Type': 'application/octet-stream'
    }
    response = requests.put(upload_url, headers=headers, data=file_content)

    if response.status_code == 201 or response.status_code == 200:
        print(f"File '{file_name}' uploaded successfully to the shared folder.")
        file_info = response.json()
        print(f"Web URL: {file_info.get('webUrl')}")
        return file_info.get('webUrl')
    else:
        print(f"Error uploading file. Status code: {response.status_code}")
        print(response.text)
        return None

# 原本上傳到我自己的資料夾
# def uploadFile(file_path):
#     print(file_path)
#     # 設置您的 Azure 應用程序憑證
#     client_id = os.getenv('CILENT_ID')
#     tenant_id = os.getenv('TENANT_ID')
#     scopes = ['https://graph.microsoft.com/Files.ReadWrite.All']

#     # 設置 token 緩存
#     cache = FileSystemTokenCache('./token_cache.json')

#     # 創建 MSAL 應用程序
#     app = msal.PublicClientApplication(
#         client_id,
#         authority=f"https://login.microsoftonline.com/{tenant_id}",
#         token_cache=cache
#     )

#     # 獲取訪問 token
#     access_token = get_access_token(app, scopes)
#     if not access_token:
#         print("Failed to acquire access token.")
#         return
        
#     if not os.path.exists(file_path):
#         print("File does not exist. Please enter a valid file path.")
#         return
#     else:
#         file_name = os.path.basename(file_path)
#         print(file_name)
#         folder_path = "BusinessCard"
            
#         url = upload_file_to_onedrive(access_token, file_path, file_name, folder_path)
#         return url


def get_shared_folder_info():
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
    headers = {
        'Authorization': 'Bearer ' + access_token,
        'Content-Type': 'application/json'
    }
    
    # 獲取共享項目
    shared_items_url = "https://graph.microsoft.com/v1.0/me/drive/sharedWithMe"
    shared_items_response = requests.get(shared_items_url, headers=headers)
    
    if shared_items_response.status_code != 200:
        print(f"Error getting shared items. Status code: {shared_items_response.status_code}")
        print(shared_items_response.text)
        return None, None

    shared_items = shared_items_response.json().get('value', [])
    
    # 自動尋找 BusinessCards 資料夾
    business_cards_folder = next((item for item in shared_items if item['name'] == 'BusinessCards' and item.get('folder')), None)
    
    if not business_cards_folder:
        print("BusinessCards folder not found in shared items.")
        return None, None

    drive_id = business_cards_folder['remoteItem']['parentReference']['driveId']
    folder_id = business_cards_folder['remoteItem']['id']
    
    print(f"Found BusinessCards folder.")
    print(f"Drive ID: {drive_id}")
    print(f"Folder ID: {folder_id}")

    return drive_id, folder_id

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
        
        # 獲取共享文件夾信息
        drive_id, folder_id = get_shared_folder_info()
        if not drive_id or not folder_id:
            print("Failed to get shared folder information.")
            return
            
        url = upload_file_to_onedrive(access_token, file_path, file_name, drive_id, folder_id)
        return url




##### 找我自己的檔案 #####
# def get_shared_folder_info():
#     client_id = os.getenv('CILENT_ID')
#     tenant_id = os.getenv('TENANT_ID')
#     scopes = ['https://graph.microsoft.com/Files.ReadWrite.All']

#     # 設置 token 緩存
#     cache = FileSystemTokenCache('./token_cache.json')

#     # 創建 MSAL 應用程序
#     app = msal.PublicClientApplication(
#         client_id,
#         authority=f"https://login.microsoftonline.com/{tenant_id}",
#         token_cache=cache
#     )

#     # 獲取訪問 token
#     access_token = get_access_token(app, scopes)
#     headers = {
#         'Authorization': 'Bearer ' + access_token,
#         'Content-Type': 'application/json'
#     }
    
#     # 獲取所有驅動器
#     drives_url = "https://graph.microsoft.com/v1.0/me/drives"
#     drives_response = requests.get(drives_url, headers=headers)
    
#     if drives_response.status_code != 200:
#         print(f"Error getting drives. Status code: {drives_response.status_code}")
#         print(drives_response.text)
#         return None, None

#     drives = drives_response.json().get('value', [])
    
#     for drive in drives:
#         print(f"Drive Name: {drive['name']}, ID: {drive['id']}")
    
#     drive_id = input("Please enter the ID of the drive containing the BusinessCards folder: ")
#     print(f"Selected drive ID: {drive_id}")

#     # 列出驅動器根目錄下的所有項目
#     root_items_url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/root/children"
#     root_items_response = requests.get(root_items_url, headers=headers)
    
#     if root_items_response.status_code != 200:
#         print(f"Error getting root items. Status code: {root_items_response.status_code}")
#         print(root_items_response.text)
#         return None, None

#     root_items = root_items_response.json().get('value', [])
    
#     print("Items in the root directory:")
#     for item in root_items:
#         print(f"Name: {item['name']}, ID: {item['id']}, Type: {'Folder' if item.get('folder') else 'File'}")
    
#     folder_name = input("Please enter the exact name of the BusinessCards folder: ")
    
#     # 在根目錄項目中查找指定的文件夾
#     business_cards_folder = next((item for item in root_items if item['name'].lower() == folder_name.lower() and item.get('folder')), None)
    
#     if not business_cards_folder:
#         print(f"Folder '{folder_name}' not found in the root directory.")
#         return None, None

#     folder_id = business_cards_folder['id']
#     print(f"Found folder. Folder ID: {folder_id}")

#     return drive_id, folder_id




##### 找共用給我的檔案 #####
# def get_shared_folder_info():
#     client_id = os.getenv('CILENT_ID')
#     tenant_id = os.getenv('TENANT_ID')
#     scopes = ['https://graph.microsoft.com/Files.ReadWrite.All']

#     # 設置 token 緩存
#     cache = FileSystemTokenCache('./token_cache.json')

#     # 創建 MSAL 應用程序
#     app = msal.PublicClientApplication(
#         client_id,
#         authority=f"https://login.microsoftonline.com/{tenant_id}",
#         token_cache=cache
#     )

#     # 獲取訪問 token
#     access_token = get_access_token(app, scopes)
#     headers = {
#         'Authorization': 'Bearer ' + access_token,
#         'Content-Type': 'application/json'
#     }
    
#     # 獲取共享項目
#     shared_items_url = "https://graph.microsoft.com/v1.0/me/drive/sharedWithMe"
#     shared_items_response = requests.get(shared_items_url, headers=headers)
    
#     if shared_items_response.status_code != 200:
#         print(f"Error getting shared items. Status code: {shared_items_response.status_code}")
#         print(shared_items_response.text)
#         return None, None

#     shared_items = shared_items_response.json().get('value', [])
    
#     print("Shared items:")
#     for index, item in enumerate(shared_items):
#         print(f"{index + 1}. Name: {item['name']}, ID: {item['id']}, Type: {'Folder' if item.get('folder') else 'File'}")
    
#     selected_index = int(input("Please enter the number of the BusinessCards folder: ")) - 1
    
#     if selected_index < 0 or selected_index >= len(shared_items):
#         print("Invalid selection.")
#         return None, None

#     selected_item = shared_items[selected_index]
    
#     if not selected_item.get('folder'):
#         print("The selected item is not a folder.")
#         return None, None

#     drive_id = selected_item['remoteItem']['parentReference']['driveId']
#     folder_id = selected_item['remoteItem']['id']
    
#     print(f"Selected folder: {selected_item['name']}")
#     print(f"Drive ID: {drive_id}")
#     print(f"Folder ID: {folder_id}")

#     return drive_id, folder_id