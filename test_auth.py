import msal
import requests
import webbrowser

# 設置您的 Azure 應用程序憑證
client_id = "6387fe9f-a72d-46c7-9b37-d454976438c0"
tenant_id = "87545bf3-2cb8-410a-a96c-64b5dca46d4c"  # 或者用 'common' 如果是多租戶應用
scopes = ['https://graph.microsoft.com/Files.ReadWrite']

# 創建 MSAL 應用程序
app = msal.PublicClientApplication(
    client_id,
    authority=f"https://login.microsoftonline.com/{tenant_id}"
)

# 嘗試從緩存獲取令牌
accounts = app.get_accounts()
result = None
if accounts:
    result = app.acquire_token_silent(scopes, account=accounts[0])

# 如果緩存中沒有令牌，則進行互動式登錄
if not result:
    flow = app.initiate_device_flow(scopes=scopes)
    print(flow['message'])
    webbrowser.open(flow['verification_uri'])
    result = app.acquire_token_by_device_flow(flow)

if "access_token" in result:
    access_token = result['access_token']
    print("Token acquired!")

    # 準備上傳
    file_path = "static/1706969953334.jpg"
    file_name = "1706969953334.jpg"
    folder_path = "BusinessCards"
    upload_url = f"https://graph.microsoft.com/v1.0/me/drive/root:/{folder_path}/{file_name}:/content"

    # 讀取文件
    with open(file_path, 'rb') as upload:
        file_content = upload.read()

    # 發送上傳請求
    headers = {
        'Authorization': 'Bearer ' + access_token,
        'Content-Type': 'image/jpeg'
    }
    response = requests.put(upload_url, headers=headers, data=file_content)

    if response.status_code == 201 or response.status_code == 200:
        print("File uploaded successfully.")
        # 獲取上傳文件的信息
        file_info = response.json()
        print(file_info)
        print(f"File uploaded to: {file_info.get('parentReference', {}).get('path', 'Unknown location')}")
        print(f"File name: {file_info.get('name', 'Unknown name')}")
        # https://cancerfree-my.sharepoint.com/personal/cherry_yeh_cancerfree_io/Documents/BusinessCards/{file_name}.{file_type}
    else:
        print(f"Error uploading file. Status code: {response.status_code}")
        print(response.text)
else:
    print(result.get("error"))
    print(result.get("error_description"))