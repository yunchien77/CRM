import msal
import requests

# 设置您的 Azure 应用程序凭证
client_id = "6387fe9f-a72d-46c7-9b37-d454976438c0"
client_secret = "QX48Q~bpsCyfCk4VjSfW2_Mm_w.QqYHVPnwYfckv"
tenant_id = "87545bf3-2cb8-410a-a96c-64b5dca46d4c"
scopes = ['https://graph.microsoft.com/.default']

# 创建 MSAL 应用程序
app = msal.ConfidentialClientApplication(
    client_id,
    authority=f"https://login.microsoftonline.com/{tenant_id}",
    client_credential=client_secret
)

# 获取访问令牌
result = app.acquire_token_for_client(scopes=scopes)

if "access_token" in result:
    access_token = result['access_token']
    print("Token acquired!")
else:
    print(result.get("error"))
    print(result.get("error_description"))
    exit()

# 准备上传
file_path = "static/1706969953334.jpg"
file_name = "1706969953334.jpg"

# 指定用户或共享驱动器
# 选项 1：上传到特定用户的 OneDrive
user_id = "cherry.yeh@cancerfree.io"
upload_url = f"https://graph.microsoft.com/v1.0/users/{user_id}/drive/root:/{file_name}:/content"

# 选项 2：上传到共享驱动器
# drive_id = "drive-id"
# upload_url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/root:/{file_name}:/content"

# 读取文件
with open(file_path, 'rb') as upload:
    file_content = upload.read()

# 发送上传请求
headers = {
    'Authorization': 'Bearer ' + access_token,
    'Content-Type': 'image/jpeg'
}
response = requests.put(upload_url, headers=headers, data=file_content)

if response.status_code == 201 or response.status_code == 200:
    print("File uploaded successfully.")
else:
    print(f"Error uploading file. Status code: {response.status_code}")
    print(response.text)