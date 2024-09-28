# from msal import PublicClientApplication

# app = PublicClientApplication(
#     "your_client_id",
#     authority="https://login.microsoftonline.com/common")

# # initialize result variable to hole the token response
# result = None 

# # We now check the cache to see
# # whether we already have some accounts that the end user already used to sign in before.
# accounts = app.get_accounts()
# if accounts:
#     # If so, you could then somehow display these accounts and let end user choose
#     print("Pick the account you want to use to proceed:")
#     for a in accounts:
#         print(a["username"])
#     # Assuming the end user chose this one
#     chosen = accounts[0]
#     # Now let's try to find a token in cache for this account
#     result = app.acquire_token_silent(["User.Read"], account=chosen)

# if not result:
#     # So no suitable token exists in cache. Let's get a new one from Azure AD.
#     result = app.acquire_token_interactive(scopes=["User.Read"])
# if "access_token" in result:
#     print(result["access_token"])  # Yay!
# else:
#     print(result.get("error"))
#     print(result.get("error_description"))
#     print(result.get("correlation_id"))  # You may need this when reporting a bug


import webbrowser
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
import sys

CLIENT_ID = "7fcb9abb-55cb-466d-8aa2-2125a46ff767"
TENANT_ID = "87545bf3-2cb8-410a-a96c-64b5dca46d4c" 
REDIRECT_URI = "http://localhost:8000"

# 構建授權URL （注意這裡使用了特定的租戶 ID）
base_url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/authorize"
params = {
    "client_id": CLIENT_ID,
    "response_type": "code",
    "redirect_uri": REDIRECT_URI,
    "response_mode": "query",
    "scope": "https://graph.microsoft.com/.default",  # 使用默認範圍
    "state": "12345"
}

auth_url = f"{base_url}?{urllib.parse.urlencode(params)}"

class OAuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        query_components = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        if 'code' in query_components:
            auth_code = query_components['code'][0]
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(f"Authorization Code: {auth_code}".encode())
            print(f"\nAuthorization Code: {auth_code}")
            print("You can now use this code to request an access token.")
        elif 'error' in query_components:
            error = query_components['error'][0]
            error_description = query_components.get('error_description', ['No description'])[0]
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            error_message = f"Error: {error}\nDescription: {error_description}"
            self.wfile.write(error_message.encode())
            print(f"\nError occurred: {error_message}")
        else:
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"No authorization code or error received.")
        
        # 關閉服務器
        def shutdown_server(server):
            server.shutdown()
        import threading
        threading.Thread(target=shutdown_server, args=(httpd,)).start()

print(f"Authorization URL: {auth_url}")
print("Opening browser for authentication...")

# 打開瀏覽器
webbrowser.open(auth_url)

# 啟動本地服務器來處理重定向
httpd = HTTPServer(('localhost', 8000), OAuthHandler)
print("Local server is running on http://localhost:8000")
print("Waiting for redirect...")
httpd.handle_request()  # 處理一個請求後關閉
print("Server has been shut down.")