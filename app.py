from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.utils import secure_filename
from image2Text import ocr_image, imageProcess
from image2Class import process_business_card
from createData import createEntity
from createData_unconfirmed import createEntity_unconfirmed
from OnedriveUpload import uploadFile
from emailHistory import uploadHistory
from excelUpload import excel
import openai

import pandas as pd
import requests
from dotenv import load_dotenv

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from werkzeug.utils import secure_filename
from recipientList import get_recipient_info
from getTagList import get_taglist
from duplicatedName import searchName
from pypinyin import lazy_pinyin

from concurrent.futures import ThreadPoolExecutor
import uuid
from datetime import datetime
import subprocess
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024

UPLOAD_FOLDER = 'img'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

EMAIL_UPLOAD_FOLDER = 'uploads'
app.config['EMAIL_UPLOAD_FOLDER'] = EMAIL_UPLOAD_FOLDER

def remove_files(folder_path):
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)
            
# Route to display upload form
@app.route('/')
def home():
    print('homeeeeeeeeee')
    return render_template('index.html')

###################################################
###########           search             ##########
###################################################
@app.route('/run-linkedin-search', methods=['POST'])
def run_linkedin_search():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    try:
        # Run the LinkedIn script with the provided credentials
        result = subprocess.run(['python', 'linkedin.py', username, password], 
                                capture_output=True, text=True, check=True)
        return jsonify({"message": "LinkedIn search completed successfully."})
    except subprocess.CalledProcessError as e:
        return jsonify({"message": f"An error occurred."})

@app.route('/run-google-search', methods=['POST'])
def run_google_search():
    try:
        # Run the Google search script
        result = subprocess.run(['python', 'googleSearch.py'], 
                                capture_output=True, text=True, check=True)
        return jsonify({"message": "Google search completed successfully."})
    except subprocess.CalledProcessError as e:
        return jsonify({"message": f"An error occurred."})

###################################################
###########   single upload (comfirmed)  ##########
###################################################

# Route for handling image upload and invoking image2Class.py
@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['file']
    afiles = request.files.getlist('afiles')

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    try:
        # Ensure the upload folder exists
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])

        filename = f"{uuid.uuid4()}_{secure_filename(file.filename)}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        print("File saved:", file_path)

        file_path_list = []
        for afile in afiles:
            if afile.filename != '':
                afilename = f"{uuid.uuid4()}_{secure_filename(afile.filename)}"
                af_path = os.path.join(app.config['UPLOAD_FOLDER'], afilename)
                afile.save(af_path)
                print("File saved:", af_path)
                af_path = imageProcess(af_path)
                file_path_list.append(af_path)

        description = request.form.get('description', '')
        print("Description:", description)

        # Determine OCR engine based on selected language
        ocr_language = request.form.get('ocrLanguage', 'cht')
        ocr_engine = 2 if ocr_language in ['chs', 'cht', 'eng'] else 1

        
        # Call OCR function from image2Text.py
        ocr_text, file_path = ocr_image(file_path, ocr_engine, ocr_language)

        if ocr_text:
            # Process business card using image2Class.py
            NAME, FIRST, LAST, COMPANY, DEPART1, DEPART2, TITLE1, TITLE2, TITLE3, MOBILE1, MOBILE2, TEL1, TEL2, FAX1, FAX2, EMAIL1, EMAIL2, ADDRESS1, ADDRESS2, WEBSITE = process_business_card(ocr_text)

            # 檢查重複名字
            duplicate_records = searchName(NAME)
        
            data = {
                'filename': filename,
                'description': description,
                'name': NAME,
                'first': FIRST,
                'last': LAST,
                'company': COMPANY,
                'department1': DEPART1,
                'department2': DEPART2,
                'title1': TITLE1,
                'title2': TITLE2,
                'title3': TITLE3,
                'mobile1': MOBILE1,
                'mobile2': MOBILE2,
                'tel1': TEL1,
                'tel2': TEL2,
                'fax1': FAX1,
                'fax2': FAX2,
                'email1': EMAIL1,
                'email2': EMAIL2,
                'address1': ADDRESS1,
                'address2': ADDRESS2,
                'website': WEBSITE,
                'duplicate': duplicate_records if duplicate_records else None
            }

            session['file_path'] = file_path
            if file_path_list:
                session['file_path_list'] = file_path_list

            return jsonify({'success': True, 'data': data}), 200

        else:
            return jsonify({'error': 'OCR failed to recognize text from the image'}), 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    

# Route for confirming the data and calling createEntity function
@app.route('/confirm', methods=['POST'])
def confirm():
    try:
        NAME = request.form['name']
        FIRST = request.form['first']
        LAST = request.form['last']
        COMPANY = request.form['company']
        DEPART1 = request.form['department1']
        DEPART2 = request.form['department2']
        TITLE1 = request.form['title1']
        TITLE2 = request.form['title2']
        TITLE3 = request.form['title3']
        ETITLE = request.form['emailtitle']
        EMAIL1 = request.form['email1']
        EMAIL2 = request.form['email2']
        MOBILE1 = request.form['mobile1']
        MOBILE2 = request.form['mobile2']
        TEL1 = request.form['tel1']
        TEL2 = request.form['tel2']
        FAX1 = request.form['fax1']
        FAX2 = request.form['fax2']
        EMAIL1 = request.form['email1']
        EMAIL2 = request.form['email2']
        ADDRESS1 = request.form['address1']
        ADDRESS2 = request.form['address2']
        WEBSITE = request.form['website']
        DESCRIPTION = request.form['description']

        date = datetime.now().strftime('%Y%m%d')
        new_filename = f"{NAME}-{COMPANY}-{date}-010-3{os.path.splitext(session['file_path'])[1]}"
        #print(f"------------{new_filename}------------")
        nfile_path = os.path.join(os.path.dirname(session['file_path']), new_filename)
        os.rename(session['file_path'], nfile_path)

        url = uploadFile(nfile_path)

        if 'file_path_list' in session:
            urls = []
            for count, value in enumerate(session['file_path_list']):
                new_filename = f"{NAME}-{COMPANY}-{date}-{count+1}-010-3{os.path.splitext(value)[1]}"
                nfile_path = os.path.join(os.path.dirname(value), new_filename)
                os.rename(value, nfile_path)
                urls.append(uploadFile(nfile_path))

            for i in urls:
                url += ("\n\n" + i)

        session.pop('file_path', None)
        session.pop('file_path_list', None)
        createEntity(NAME, FIRST, LAST, COMPANY, DEPART1, DEPART2, TITLE1, TITLE2, TITLE3, MOBILE1, MOBILE2, TEL1, TEL2, FAX1, FAX2, ETITLE, EMAIL1, EMAIL2, ADDRESS1, ADDRESS2, WEBSITE, DESCRIPTION, url)
        remove_files('img/')

        return jsonify({'success': True}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400
        
###################################################
########### multiple upload(uncomfirmed) ##########
###################################################

@app.route('/multiupload')
def multiupload():
    return render_template('multiupload.html')

def process_and_upload_image(file, ocr_engine, ocr_language):
    try:
        #filename = secure_filename(file.filename)
        filename = f"{uuid.uuid4()}_{secure_filename(file.filename)}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        print(f"{filename} is saved.")

        ocr_text, file_path = ocr_image(file_path, ocr_engine, ocr_language)

        if ocr_text:
            NAME, FIRST, LAST, COMPANY, DEPART1, DEPART2, TITLE1, TITLE2, TITLE3, MOBILE1, MOBILE2, TEL1, TEL2, FAX1, FAX2, EMAIL1, EMAIL2, ADDRESS1, ADDRESS2, WEBSITE = process_business_card(ocr_text)
            
            date = datetime.now().strftime('%Y%m%d')

            if '/' in COMPANY:
                # 提取斜杠之前的部分作為新的變數
                new_company = COMPANY.split('/')[0]
            else:
                # 如果不存在斜杠，new_company保持為原始COMPANY
                new_company = COMPANY

            new_filename = f"{NAME}-{new_company}-{date}-010-3{os.path.splitext(file_path)[1]}"
            print(f"------------{new_filename}------------")
            nfile_path = os.path.join(os.path.dirname(file_path), new_filename)
            os.rename(file_path, nfile_path)

            url = uploadFile(nfile_path)
            # 直接上傳到 Ragic
            createEntity_unconfirmed(NAME, FIRST, LAST, COMPANY, DEPART1, DEPART2, TITLE1, TITLE2, TITLE3, MOBILE1, MOBILE2, TEL1, TEL2, FAX1, FAX2, EMAIL1, EMAIL2, ADDRESS1, ADDRESS2, WEBSITE, url)
            
            return {'success': True, 'filename': filename}
        else:
            return {'success': False, 'filename': filename, 'error': 'OCR failed'}
    except Exception as e:
        return {'success': False, 'filename': filename, 'error': str(e)}

@app.route('/multiupload', methods=['POST'])
def upload_multi_file():
    if 'files[]' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    files = request.files.getlist('files[]')
    if not files or files[0].filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    ocr_language = request.form.get('ocrLanguage', 'cht')
    ocr_engine = 2 if ocr_language in ['chs', 'cht', 'eng'] else 1

    results = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_file = {executor.submit(process_and_upload_image, file, ocr_engine, ocr_language): file for file in files}
        for future in future_to_file:
            result = future.result()
            results.append(result)

    remove_files('img/')

    return jsonify({'results': results}), 200

##################################################
############         email           #############
##################################################

@app.route('/login', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        try:
            server = smtplib.SMTP('smtp.outlook.com', 587)
            server.starttls()
            server.login(email, password)
            server.quit()

            session['email'] = email
            session['password'] = password
            return redirect(url_for('send_email'))
        except smtplib.SMTPAuthenticationError:
            flash('Invalid email or password. Please try again.', 'error')

    return render_template('login.html')

@app.route('/send_email', methods=['GET', 'POST'])
def send_email():
    if 'email' not in session:
        return redirect(url_for('index'))

    if not os.path.exists(EMAIL_UPLOAD_FOLDER):
        os.makedirs(EMAIL_UPLOAD_FOLDER)

    taglist = get_taglist()

    if request.method == 'POST':
        recipient_group = request.form.get('recipient_group')
        email_subject = request.form.get('email_subject')
        email_content = request.form.get('email_content')
        attachments = request.files.getlist('attachments')
        from_email = request.form.get('from_email')
        reply_to = request.form.get('reply_to')

        if recipient_group and email_subject and email_content:
            attachment_paths = []
            for attachment in attachments:
                if attachment:
                    filename = secure_filename(''.join(lazy_pinyin(attachment.filename)))
                    attachment_path = os.path.join(app.config['EMAIL_UPLOAD_FOLDER'], filename)
                    attachment.save(attachment_path)
                    attachment_paths.append(attachment_path)

            customers = get_recipient_info(recipient_group)
            if customers:
                success = send_emails_to_customers(customers, email_subject, email_content, attachment_paths, from_email, reply_to)
                if success:
                    date = datetime.now().strftime('%Y/%m/%d')
                    uploadHistory(customers, email_subject, email_content, date, session['email'])
                    return redirect(url_for('send_email', status='sent'))
                else:
                    return redirect(url_for('send_email', status='error'))

    return render_template('send_email.html', taglist=taglist, email=session['email'])

def send_emails_to_customers(customers, subject, content, attachment_paths, from_email=None, reply_to=None):
    email = from_email or session['email']
    password = session['password']

    try:
        server = smtplib.SMTP('smtp.outlook.com', 587)
        server.starttls()
        server.login(session['email'], password)  # 總是使用登錄的電子郵件進行身份驗證

        for customer in customers:
            receiver_email = customer['email']
            receiver_name = customer['emailtitle']
            print(f'Sending email to {receiver_name} : {receiver_email}')

            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = email
            message["To"] = receiver_email

            if reply_to:
                message.add_header('Reply-To', reply_to)

            html_content = content.replace('\n', '<br>').replace('{name}', receiver_name)
            message.attach(MIMEText(html_content, "html"))

            for attachment_path in attachment_paths:
                with open(attachment_path, "rb") as attachment_file:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(attachment_file.read())
                    encoders.encode_base64(part)
                    part.add_header(
                        "Content-Disposition",
                        f"attachment; filename= {os.path.basename(attachment_path)}",
                    )
                    message.attach(part)

            try:
                server.sendmail(email, receiver_email, message.as_string())
                print(f'Email sent to {receiver_email} successfully')
                
            except Exception as e:
                print(f'Failed to send email to {receiver_email}. Error: {str(e)}')
                continue

        server.quit()
        remove_files('uploads/')
        return True

    except Exception as e:
        print(f'Send mail failed. Error message: {str(e)}')
        return False

@app.route('/logout')
def logout():
    session.pop('email', None)
    session.pop('password', None)
    return redirect(url_for('index'))

################################################
##############   excel upload   ################
################################################)
@app.route('/excelupload')
def excelupload():
    return render_template('excelupload.html')

# def createEntity(NAME, FIRSTNAME, FIRSTNAME_PINYIN, LASTNAME, LASTNAME_PINYIN, INDUSTRY, LOCATION, COMPANY1, DEPARTMENT1, TITLE1, COMPANY2, DEPARTMENT2, TITLE2, COMPANY_OTHER, DEPARTMENT_OTHER, TITLE3, MOBILE1, MOBILE2, MOBILE_OTHER, TEL1, TEL2, TEL_OTHER, FAX1, FAX2, FAX_OTHER, EMAIL1, EMAIL2, EMAIL_OTHER, ADDRESS1, ADDRESS2, ADDRESS_OTHER, WEBSITE, CHAT_ACCOUNT, SOCIAL_ACCOUNT, NICKNAME, BIRTHDAY, ANNIVERSARY, TYPE, DESCRIPTION1, DESCRIPTION2, DESCRIPTION3):
#     SERVER_URL = 'ap12.ragic.com'
#     ACCOUNT_NAME = 'cancerfree'
#     TAB = 'forms5'
#     SHEET_INDEX = '4'

#     FIELD_NAME = '1001976' #姓名
#     FIELD_FIRSTNAME = '1002926' #名字
#     FIELD_FIRSTNAME_PINYIN = '1003168' #名字拼音或音標
#     FIELD_LASTNAME = '1002927' #姓
#     FIELD_LASTNAME_PINYIN = '1003170' #姓氏拼音或音標
#     FIELD_INDUSTRY = '1003172' #行業
#     FIELD_LOCATION = '1003174' #所在地
#     FIELD_COMPANY1 = '1001977' #公司1
#     FIELD_DEPARTMENT1 = '1001982' #部門1
#     FIELD_TITLE1 = '1001984' #職位1
#     FIELD_COMPANY2 = '1003176' #公司2
#     FIELD_DEPARTMENT2 = '1001983' #部門2
#     FIELD_TITLE2 = '1001985' #職位2
#     FIELD_COMPANY_OTHER = '1003178' #公司(其他)
#     FIELD_DEPARTMENT_OTHER = '1003180' #部門(其他)
#     FIELD_TITLE3 = '1003182' #職位(其他)
#     FIELD_MOBILE1 = '1001988' #手機1
#     FIELD_MOBILE2 = '1001990' #手機2
#     FIELD_MOBILE_OTHER = '1003183' #手機(其他)
#     FIELD_TEL1 = '1001992' #電話1
#     FIELD_TEL2 = '1001994' #電話2
#     FIELD_TEL_OTHER = '1003184' #電話(其他)
#     FIELD_FAX1 = '1001996' #傳真1
#     FIELD_FAX2 = '1001998' #傳真2
#     FIELD_FAX_OTHER = '1003185' #傳真(其他)
#     FIELD_EMAIL1 = '1001989' #電子郵件1
#     FIELD_EMAIL2 = '1001991' #電子郵件2
#     FIELD_EMAIL_OTHER = '1003186' #電子郵件(其他)
#     FIELD_ADDRESS1 = '1001993' #地址1
#     FIELD_ADDRESS2 = '1001995' #地址2
#     FIELD_ADDRESS_OTHER = '1003187' #地址(其他)
#     FIELD_WEBSITE = '1001997' #網頁
#     FIELD_CHAT_ACCOUNT = '1003169' #聊天軟件賬號
#     FIELD_SOCIAL_ACCOUNT = '1003171' #社交帳戶
#     FIELD_NICKNAME = '1003173' #暱稱
#     FIELD_BIRTHDAY = '1003175' #生日
#     FIELD_ANNIVERSARY = '1003177' #紀念日
#     FIELD_TYPE = '1002025' #分組
#     FIELD_DESCRIPTION1 = '1001987' #備註1
#     FIELD_DESCRIPTION2 = '1003179' #備註2
#     FIELD_DESCRIPTION3 = '1003181' #備註3

#     print('2222222222222222')

#     load_dotenv()
#     API_KEY = os.getenv('RAGIC_API_KEY')

#     API_ENDPOINT_LISTING_PAGE = f'https://{SERVER_URL}/{ACCOUNT_NAME}/{TAB}/{SHEET_INDEX}'

#     params = {
#         'api': '',
#         'v': 3
#     }

#     data = {
#         FIELD_NAME : NAME, #姓名
#         FIELD_FIRSTNAME : FIRSTNAME, #名字
#         FIELD_FIRSTNAME_PINYIN : FIRSTNAME_PINYIN, #名字拼音或音標
#         FIELD_LASTNAME : LASTNAME, #姓
#         FIELD_LASTNAME_PINYIN : LASTNAME_PINYIN, #姓氏拼音或音標
#         FIELD_INDUSTRY : INDUSTRY, #行業
#         FIELD_LOCATION : LOCATION, #所在地
#         FIELD_COMPANY1 : COMPANY1, #公司1
#         FIELD_DEPARTMENT1 : DEPARTMENT1, #部門1
#         FIELD_TITLE1 : TITLE1, #職位1
#         FIELD_COMPANY2 : COMPANY2, #公司2
#         FIELD_DEPARTMENT2 : DEPARTMENT2, #部門2
#         FIELD_TITLE2 : TITLE2, #職位2
#         FIELD_COMPANY_OTHER : COMPANY_OTHER, #公司(其他)
#         FIELD_DEPARTMENT_OTHER : DEPARTMENT_OTHER, #部門(其他)
#         FIELD_TITLE3 : TITLE3, #職位(其他)
#         FIELD_MOBILE1 : MOBILE1, #手機1
#         FIELD_MOBILE2 : MOBILE2, #手機2
#         FIELD_MOBILE_OTHER : MOBILE_OTHER, #手機(其他)
#         FIELD_TEL1 : TEL1, #電話1
#         FIELD_TEL2 : TEL2, #電話2
#         FIELD_TEL_OTHER : TEL_OTHER, #電話(其他)
#         FIELD_FAX1 : FAX1, #傳真1
#         FIELD_FAX2 : FAX2, #傳真2
#         FIELD_FAX_OTHER : FAX_OTHER, #傳真(其他)
#         FIELD_EMAIL1 : EMAIL1, #電子郵件1
#         FIELD_EMAIL2 : EMAIL2, #電子郵件2
#         FIELD_EMAIL_OTHER : EMAIL_OTHER, #電子郵件(其他)
#         FIELD_ADDRESS1 : ADDRESS1, #地址1
#         FIELD_ADDRESS2 : ADDRESS2, #地址2
#         FIELD_ADDRESS_OTHER : ADDRESS_OTHER, #地址(其他)
#         FIELD_WEBSITE : WEBSITE, #網頁
#         FIELD_CHAT_ACCOUNT : CHAT_ACCOUNT, #聊天軟件賬號
#         FIELD_SOCIAL_ACCOUNT : SOCIAL_ACCOUNT, #社交帳戶
#         FIELD_NICKNAME : NICKNAME, #暱稱
#         FIELD_BIRTHDAY : BIRTHDAY, #生日
#         FIELD_ANNIVERSARY : ANNIVERSARY, #紀念日
#         FIELD_TYPE : TYPE, #分組
#         FIELD_DESCRIPTION1 : DESCRIPTION1, #備註1
#         FIELD_DESCRIPTION2 : DESCRIPTION2, #備註2
#         FIELD_DESCRIPTION3 : DESCRIPTION3, #備註3
#     }

#     response = requests.post(API_ENDPOINT_LISTING_PAGE, params=params, json=data, headers={'Authorization': 'Basic '+API_KEY})
#     print(response.text)

# def excel(file_path):
#     print(f"Processing file: {file_path}")

    
#     # 讀取 Excel 文件
#     df = pd.read_excel(file_path, skiprows=1, engine='openpyxl')
#     df = df.fillna('')
#     print('1111111111111111')
        
#     for index, row in df.iterrows():
#         #row = row.apply(lambda x: str(x) if isinstance(x, float) and (pd.isna(x) or x == float('inf') or x == float('-inf')) else x)
#         variables = row.tolist()  # Convert the row to a list
                
#         # Store values into specific variables (adjust according to your needs)
#         CREATION_DATE, NAME, FIRSTNAME, FIRSTNAME_PINYIN, LASTNAME, LASTNAME_PINYIN, \
#         INDUSTRY, LOCATION, COMPANY1, DEPARTMENT1, TITLE1, COMPANY2, DEPARTMENT2, TITLE2, \
#         COMPANY_OTHER, DEPARTMENT_OTHER, TITLE3, MOBILE1, MOBILE2, MOBILE_OTHER, TEL1, \
#         TEL2, TEL_OTHER, FAX1, FAX2, FAX_OTHER, EMAIL1, EMAIL2, EMAIL_OTHER, ADDRESS1, \
#         ADDRESS2, ADDRESS_OTHER, WEBSITE, CHAT_ACCOUNT, SOCIAL_ACCOUNT, NICKNAME, BIRTHDAY, \
#         ANNIVERSARY, TYPE, DESCRIPTION1, DESCRIPTION2, DESCRIPTION3 = variables[:43]  # Adjust the number of variables if needed

#         print(f"CREATION_DATE: {CREATION_DATE}")
#         print(f"NAME: {NAME}")
#         print(f"FIRSTNAME: {FIRSTNAME}")
#         print(f"FIRSTNAME_PINYIN: {FIRSTNAME_PINYIN}")
#         print(f"LASTNAME: {LASTNAME}")
#         print(f"LASTNAME_PINYIN: {LASTNAME_PINYIN}")
#         print(f"INDUSTRY: {INDUSTRY}")
#         print(f"LOCATION: {LOCATION}")
#         print(f"COMPANY1: {COMPANY1}")
#         print(f"DEPARTMENT1: {DEPARTMENT1}")
#         print(f"TITLE1: {TITLE1}")
#         print(f"COMPANY2: {COMPANY2}")
#         print(f"DEPARTMENT2: {DEPARTMENT2}")
#         print(f"TITLE2: {TITLE2}")
#         print(f"COMPANY_OTHER: {COMPANY_OTHER}")
#         print(f"DEPARTMENT_OTHER: {DEPARTMENT_OTHER}")
#         print(f"TITLE3: {TITLE3}")
#         print(f"MOBILE1: {MOBILE1}")
#         print(f"MOBILE2: {MOBILE2}")
#         print(f"MOBILE_OTHER: {MOBILE_OTHER}")
#         print(f"TEL1: {TEL1}")
#         print(f"TEL2: {TEL2}")
#         print(f"TEL_OTHER: {TEL_OTHER}")
#         print(f"FAX1: {FAX1}")
#         print(f"FAX2: {FAX2}")
#         print(f"FAX_OTHER: {FAX_OTHER}")
#         print(f"EMAIL1: {EMAIL1}")
#         print(f"EMAIL2: {EMAIL2}")
#         print(f"EMAIL_OTHER: {EMAIL_OTHER}")
#         print(f"ADDRESS1: {ADDRESS1}")
#         print(f"ADDRESS2: {ADDRESS2}")
#         print(f"ADDRESS_OTHER: {ADDRESS_OTHER}")
#         print(f"WEBSITE: {WEBSITE}")
#         print(f"CHAT_ACCOUNT: {CHAT_ACCOUNT}")
#         print(f"SOCIAL_ACCOUNT: {SOCIAL_ACCOUNT}")
#         print(f"NICKNAME: {NICKNAME}")
#         print(f"BIRTHDAY: {BIRTHDAY}")
#         print(f"ANNIVERSARY: {ANNIVERSARY}")
#         print(f"TYPE: {TYPE}")
#         print(f"DESCRIPTION1: {DESCRIPTION1}")
#         print(f"DESCRIPTION2: {DESCRIPTION2}")
#         print(f"DESCRIPTION3: {DESCRIPTION3}")
#         print()

#         createEntity(NAME, FIRSTNAME, FIRSTNAME_PINYIN, LASTNAME, LASTNAME_PINYIN, INDUSTRY, LOCATION, COMPANY1, DEPARTMENT1, TITLE1, COMPANY2, DEPARTMENT2, TITLE2, COMPANY_OTHER, DEPARTMENT_OTHER, TITLE3, MOBILE1, MOBILE2, MOBILE_OTHER, TEL1, TEL2, TEL_OTHER, FAX1, FAX2, FAX_OTHER, EMAIL1, EMAIL2, EMAIL_OTHER, ADDRESS1, ADDRESS2, ADDRESS_OTHER, WEBSITE, CHAT_ACCOUNT, SOCIAL_ACCOUNT, NICKNAME, BIRTHDAY, ANNIVERSARY, TYPE, DESCRIPTION1, DESCRIPTION2, DESCRIPTION3)

@app.route('/upload-excel', methods=['POST'])
def upload_excel():
    if 'excel_file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['excel_file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        result = excel(file_path)
        if result:
            return jsonify({'message': 'File processed successfully'})
        else:
            return jsonify({'error': str(e)}), 500

# @app.route('/upload-excel', methods=['POST'])
# def upload_excel():
#     print('22222222222222222222')
#     app.logger.info("Received request to /upload-excel")

#     if 'excel_file' not in request.files:
#         return jsonify({"error": "No file part"}), 400
#     file = request.files['excel_file']
#     if file.filename == '':
#         return jsonify({"error": "No selected file"}), 400
#     if file and allowed_file(file.filename):
#         filename = secure_filename(file.filename)
#         file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#         file.save(file_path)
        
#         try:
#             result = excel(file_path)
#             # result = subprocess.run(['python', 'excelUpload.py', file_path], 
#             #                         capture_output=True, text=True, check=True)
            
#             # if result.returncode == 0:
#             #     app.logger.info("Finished processing Excel file")
#             #     return jsonify({"message": "Excel file processed successfully", "success": True}), 200
#             # else:
#             #     return jsonify({"error": "Error processing Excel file: " + result.stdout, "success": False}), 500

#             if result == 0:
#                 return jsonify({"message": "Excel file processed successfully", "success": True}), 200
#             else:
#                  return jsonify({"error": "Error processing Excel file", "success": False}), 500

#         except subprocess.CalledProcessError as e:
#             return jsonify({"error": f"Error processing Excel file: {e.output}", "success": False}), 500
#         #finally:
#             #os.remove(file_path)
#     else:
#         return jsonify({"error": "File type not allowed", "success": False}), 400
    

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'xlsx', 'xls'}


if __name__ == '__main__':
    app.run(debug=True)