from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.utils import secure_filename
import openai

from image2Text import ocr_image, imageProcess
from image2Class import process_business_card
from createData import createEntity
from createData_unconfirmed import createEntity_unconfirmed
from OnedriveUpload import uploadFile
from emailHistory import uploadHistory
from excelUpload import excel
from googleSearch import search
from googleCustom import customSearch
from recipientList import get_recipient_info, get_recipient_individual
from getTagList import get_taglist
from duplicatedName import searchName

import pandas as pd
import requests
from dotenv import load_dotenv

from functools import wraps
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from werkzeug.utils import secure_filename
from pypinyin import lazy_pinyin

from concurrent.futures import ThreadPoolExecutor
import uuid
from datetime import datetime
import subprocess
import os
import json

from msal import ConfidentialClientApplication
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import base64
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'your_secret_key'

app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

UPLOAD_FOLDER = 'img'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

EMAIL_UPLOAD_FOLDER = 'uploads'
app.config['EMAIL_UPLOAD_FOLDER'] = EMAIL_UPLOAD_FOLDER

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///admin.db'
db = SQLAlchemy(app)

load_dotenv()
CLIENT_ID = os.getenv('CLIENT_ID_LOGIN')
CLIENT_SECRET = os.getenv('CLIENT_SECRET_LOGIN')
TENANT_ID = os.getenv('TENANT_ID_LOGIN')
REDIRECT_URI = os.getenv('REDIRECT_URI')
SCOPES = ['https://graph.microsoft.com/Mail.Send', 'https://graph.microsoft.com/User.Read']

###################################################
###################    database   #################
###################################################
ADMIN_USERS = ['cherry.yeh@cancerfree.io']

# 用戶資料
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    
# 登入紀錄資料
class LoginRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    login_time = db.Column(db.DateTime, nullable=False, default=datetime.now)

# 單一名片辨識記錄
class SingleCardRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.now)
    success = db.Column(db.Boolean, nullable=False)
    card_owner = db.Column(db.String(120))
    error_message = db.Column(db.String(255))

# 多張名片辨識記錄
class MultiCardRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.now)
    success_count = db.Column(db.Integer, nullable=False)
    failure_count = db.Column(db.Integer, nullable=False)
    error_message = db.Column(db.String(255))

# 寄信功能記錄
class EmailRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.now)
    success_count = db.Column(db.Integer, nullable=False)
    failure_count = db.Column(db.Integer, nullable=False)
    recipient_group = db.Column(db.String(120))
    individual_recipient = db.Column(db.String(120))

# Excel上傳記錄
class ExcelUploadRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.now)
    success = db.Column(db.Boolean, nullable=False)
    filename = db.Column(db.String(255))
    error_message = db.Column(db.String(255))

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'email' not in session or session['email'].lower() not in ADMIN_USERS:
            # flash('You do not have permission to access this page.', 'error')
            return redirect(url_for('upload'))  
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login_records')
@admin_required
def login_records():
    records = db.session.query(LoginRecord, User).join(User).order_by(LoginRecord.login_time.desc()).all()
    return render_template('login_records.html', records=records, admin_users=ADMIN_USERS)

@app.route('/admin_records')
@admin_required
def admin_records():
    single_card_records = db.session.query(SingleCardRecord, User).join(User).order_by(SingleCardRecord.timestamp.desc()).all()
    multi_card_records = db.session.query(MultiCardRecord, User).join(User).order_by(MultiCardRecord.timestamp.desc()).all()
    email_records = db.session.query(EmailRecord, User).join(User).order_by(EmailRecord.timestamp.desc()).all()
    excel_upload_records = db.session.query(ExcelUploadRecord, User).join(User).order_by(ExcelUploadRecord.timestamp.desc()).all()
    
    return render_template('admin_records.html', 
                           single_card_records=single_card_records,
                           multi_card_records=multi_card_records,
                           email_records=email_records,
                           excel_upload_records=excel_upload_records, admin_users=ADMIN_USERS)

###################################################
####################    login   ###################
###################################################
# Authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'email' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if not email.endswith('@cancerfree.io'):
            flash('Email must be from the @cancerfree.io domain.', 'error')
            return render_template('login.html')

        try:
            server = smtplib.SMTP('smtp.outlook.com', 587)
            server.starttls()
            server.login(email, password)
            server.quit()

            session['email'] = email
            session['password'] = password

            # 查詢或新增用戶
            user = User.query.filter_by(email=email.lower()).first()
            if not user:
                user = User(email=email.lower())
                db.session.add(user)
                db.session.commit()

            # 記錄登入
            login_record = LoginRecord(user_id=user.id)
            db.session.add(login_record)
            db.session.commit()

            return redirect(url_for('home'))
        except smtplib.SMTPAuthenticationError:
            flash('Invalid email or password. Please try again.', 'error')
        except smtplib.SMTPException as e:
            flash(f'An error occurred: {str(e)}', 'error')
        except Exception as e:
            flash(f'Unexpected error: {str(e)}', 'error')

    return render_template('login.html', admin_users=ADMIN_USERS)

@app.route('/microsoft_login')
def microsoft_login():
    msal_app = ConfidentialClientApplication(
        CLIENT_ID, authority=f"https://login.microsoftonline.com/{TENANT_ID}",
        client_credential=CLIENT_SECRET
    )
    auth_url = msal_app.get_authorization_request_url(SCOPES, redirect_uri=REDIRECT_URI, prompt="select_account")
    return redirect(auth_url)

@app.route('/auth_callback')
def auth_callback():
    msal_app = ConfidentialClientApplication(
        CLIENT_ID, authority=f"https://login.microsoftonline.com/{TENANT_ID}",
        client_credential=CLIENT_SECRET
    )
    result = msal_app.acquire_token_by_authorization_code(
        request.args['code'],
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )
    if 'access_token' in result:
        session['access_token'] = result['access_token']
        session['refresh_token'] = result.get('refresh_token')
        user_info = requests.get(
            'https://graph.microsoft.com/v1.0/me',
            headers={'Authorization': f"Bearer {result['access_token']}"}
        ).json()
        email = user_info.get('mail') or user_info.get('userPrincipalName')
        session['email'] = email
        
        # 記錄登入
        user = User.query.filter_by(email=email.lower()).first()
        if not user:
            user = User(email=email.lower())
            db.session.add(user)
            db.session.commit()

        login_record = LoginRecord(user_id=user.id)
        db.session.add(login_record)
        db.session.commit()

        return redirect(url_for('home'))
    return 'Authentication failed', 400
    
###################################################
###########   single upload (comfirmed)  ##########
###################################################
@app.route('/upload')
@login_required
def home():
    return render_template('index.html', email=session['email'], admin_users=ADMIN_USERS)

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
        print("ocr done")

        if ocr_text:
            # Process business card using image2Class.py
            NAME, FIRST, LAST, COMPANY, DEPART1, DEPART2, TITLE1, TITLE2, TITLE3, MOBILE1, MOBILE2, TEL1, TEL2, FAX1, FAX2, EMAIL1, EMAIL2, ADDRESS1, ADDRESS2, WEBSITE = process_business_card(ocr_text)
            print('classification done')

            # 檢查重複名字
            duplicate_records = searchName(NAME)
            print("duplicate check done")
        
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
                'duplicate': duplicate_records if duplicate_records else None,
                'ocr_text': ocr_text
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
        ocr_text = request.form['ocr_text']

        date = datetime.now().strftime('%Y%m%d')
        new_filename = f"{NAME}-{COMPANY}-{date}-010-3{os.path.splitext(session['file_path'])[1]}"
        #print(f"------------{new_filename}------------")
        nfile_path = os.path.join(os.path.dirname(session['file_path']), new_filename)
        os.rename(session['file_path'], nfile_path)

        url = uploadFile(nfile_path)
        os.remove(nfile_path)

        if 'file_path_list' in session:
            urls = []
            for count, value in enumerate(session['file_path_list']):
                new_filename = f"{NAME}-{COMPANY}-{date}-{count+1}-010-3{os.path.splitext(value)[1]}"
                nfile_path = os.path.join(os.path.dirname(value), new_filename)
                os.rename(value, nfile_path)
                urls.append(uploadFile(nfile_path))
                os.remove(nfile_path)

            for i in urls:
                url += ("\n\n" + i)

        session.pop('file_path', None)
        session.pop('file_path_list', None)
        createEntity(ocr_text, NAME, FIRST, LAST, COMPANY, DEPART1, DEPART2, TITLE1, TITLE2, TITLE3, MOBILE1, MOBILE2, TEL1, TEL2, FAX1, FAX2, ETITLE, EMAIL1, EMAIL2, ADDRESS1, ADDRESS2, WEBSITE, DESCRIPTION, url)

        # 記錄成功的單張名片上傳
        user = User.query.filter_by(email=session['email']).first()
        record = SingleCardRecord(user_id=user.id, success=True, card_owner=NAME)
        db.session.add(record)
        db.session.commit()

        return jsonify({'success': True}), 200
    except Exception as e:
        # 記錄失敗的單張名片上傳
        user = User.query.filter_by(email=session['email'].lower()).first()
        record = SingleCardRecord(user_id=user.id, success=False, error_message=str(e))
        db.session.add(record)
        db.session.commit()

        return jsonify({'error': str(e)}), 400
        
###################################################
########### multiple upload(uncomfirmed) ##########
###################################################

@app.route('/multiupload')
@login_required
def multiupload():
    return render_template('multiupload.html', email=session['email'], admin_users=ADMIN_USERS)

def process_and_upload_image(file, ocr_engine, ocr_language):
    try:
        filename = f"{uuid.uuid4()}_{secure_filename(file.filename)}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        print(f"{filename} is saved.")

        ocr_text, processed_file_path = ocr_image(file_path, ocr_engine, ocr_language)

        if ocr_text:
            NAME, FIRST, LAST, COMPANY, DEPART1, DEPART2, TITLE1, TITLE2, TITLE3, MOBILE1, MOBILE2, TEL1, TEL2, FAX1, FAX2, EMAIL1, EMAIL2, ADDRESS1, ADDRESS2, WEBSITE = process_business_card(ocr_text)
            
            date = datetime.now().strftime('%Y%m%d')

            if '/' in COMPANY:
                new_company = COMPANY.split('/')[0]
            else:
                new_company = COMPANY

            new_filename = f"{NAME}-{new_company}-{date}-010-3{os.path.splitext(processed_file_path)[1]}"
            print(f"------------{new_filename}------------")
            nfile_path = os.path.join(os.path.dirname(processed_file_path), new_filename)
            os.rename(processed_file_path, nfile_path)

            url = uploadFile(nfile_path)
            os.remove(nfile_path)  # 上傳後刪除文件
            
            # 直接上傳到 Ragic
            createEntity_unconfirmed(ocr_text, NAME, FIRST, LAST, COMPANY, DEPART1, DEPART2, TITLE1, TITLE2, TITLE3, MOBILE1, MOBILE2, TEL1, TEL2, FAX1, FAX2, EMAIL1, EMAIL2, ADDRESS1, ADDRESS2, WEBSITE, url)
            
            return {'success': True, 'filename': filename}
        else:
            if os.path.exists(file_path):
                os.remove(file_path)
            return {'success': False, 'filename': filename, 'error': 'OCR failed'}
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
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
    success_count = 0
    failure_count = 0
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_file = {executor.submit(process_and_upload_image, file, ocr_engine, ocr_language): file for file in files}
        for future in future_to_file:
            result = future.result()
            results.append(result)
            if result['success']:
                success_count += 1
            else:
                failure_count += 1

    # 記錄多張名片上傳結果
    user = User.query.filter_by(email=session['email'].lower()).first()
    record = MultiCardRecord(user_id=user.id, success_count=success_count, failure_count=failure_count)
    db.session.add(record)
    db.session.commit()

    return jsonify({'results': results}), 200

##################################################
############         email           #############
##################################################

@app.route('/get_individual_list', methods=['GET'])
def get_individual_list():
    individual_list = get_recipient_individual()
    return jsonify(individual_list)

@app.route('/get_recipients_by_tag', methods=['POST'])
def get_recipients_by_tag():
    tag = request.json['tag']
    recipients = get_recipient_info(tag)
    return jsonify(recipients)

def send_email_microsoft(email, to_email, subject, content, attachment_paths=None, reply_to=None):
    print("send_email_microsoft")
    # access_token = session.get('access_token')
    # mailsend.send_email(access_token, to_email, subject, content)
    # print("done")
    # return True, "Email sent successfully"
    print(f"Attempting to send email to {to_email}")
    access_token = session.get('access_token')
    if not access_token:
        return False, "No access token available"

    # Prepare email message
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
            ]
        },
        "saveToSentItems": "true"
    }

    # Add reply-to if provided
    if reply_to:
        message["message"]["replyTo"] = [
            {
                "emailAddress": {
                    "address": reply_to
                }
            }
        ]

    if email != session["email"]:
        message["message"]["from"] = {
                "emailAddress": {
                    "address": email
                }
            }

    # Add attachments if any
    if attachment_paths:
        attachments = []
        for path in attachment_paths:
            with open(path, 'rb') as file:
                content = file.read()
                attachments.append({
                    "@odata.type": "#microsoft.graph.fileAttachment",
                    "name": os.path.basename(path),
                    "contentBytes": base64.b64encode(content).decode('utf-8')
                })
        message["message"]["attachments"] = attachments

    endpoint = f'https://graph.microsoft.com/v1.0/users/{session["email"]}/sendMail'

    # Send email using Microsoft Graph API
    response = requests.post(
        endpoint,
        headers={
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        },
        json=message
    )

    if response.status_code == 202:
        print(f"Email to {to_email} accepted for processing")
        return True, "Email sent successfully"
    else:
        print(f"Failed to send email to {to_email}: {response.text}")
        return False, f"Failed to send email: {response.text}"

def send_email_smtp(email, password, to_email, subject, content, attachment_paths=None, reply_to=None):
    try:
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = email
        message["To"] = to_email
        if reply_to:
            message["Reply-To"] = reply_to
            print(reply_to)

        html_part = MIMEText(content, "html")
        message.attach(html_part)

        if attachment_paths:
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

        with smtplib.SMTP('smtp.outlook.com', 587) as server:
            server.starttls()
            server.login(session['email'], password)
            server.sendmail(email, to_email, message.as_string())

        return True, "Email sent successfully"
    except Exception as e:
        return False, str(e)

def send_email_to_customer(customer, subject, content, attachment_paths, from_email, reply_to):
    try:
        receiver_email = customer['email']
        receiver_name = customer['emailtitle']
        receiver_company = customer['company']
        receiver_title1 = customer['title1']
        receiver_title2 = customer['title2']
        receiver_department1 = customer['department1']
        receiver_department2 = customer['department2']
        print(f'Sending email to {receiver_name} : {receiver_email} from {from_email}')

        html_content = content.replace('\n', '<br>').replace('{name}', receiver_name).replace('{company}', receiver_company).replace('{title1}', receiver_title1).replace('{title2}', receiver_title2).replace('{department1}', receiver_department1).replace('{department2}', receiver_department2)

        email = from_email or session['email']
        print("from_email: ", email)
        if 'access_token' in session:
            # Use Microsoft Graph API
            print("Use Microsoft Graph API...")
            success, message = send_email_microsoft(email, receiver_email, subject, html_content, attachment_paths, reply_to)
        else:
            # Use SMTP
            print("Use SMTP...")
            password = session['password']
            success, message = send_email_smtp(email, password, receiver_email, subject, html_content, attachment_paths, reply_to)

        if success:
            print(f'Email sent to {receiver_email} successfully')
            date = datetime.now().strftime('%Y/%m/%d')
            plain_content = html_content.replace('<br>', '\n')
            uploadHistory(customer, subject, plain_content, date, from_email)
            #uploadHistory(customer, subject, html_content, date, from_email)
            return True
        else:
            print(f'Failed to send email to {receiver_email}. Error: {message}')
            return False
    except Exception as e:
        print(f'Failed to send email to {receiver_email}. Error: {str(e)}')
        return False

def send_emails_to_customers(customers, subject, content, attachment_paths, from_email, reply_to):
    success_count = 0
    failure_count = 0

    for customer in customers:
        if send_email_to_customer(customer, subject, content, attachment_paths, from_email, reply_to):
            success_count += 1
        else:
            failure_count += 1

    for attachment_path in attachment_paths:
        try:
            os.remove(attachment_path)
            print(f"Deleted attachment file: {attachment_path}")
        except Exception as e:
            print(f"Failed to delete attachment file {attachment_path}: {str(e)}")

    print(f"Email sending complete. Successes: {success_count}, Failures: {failure_count}")
    return success_count > 0, success_count, failure_count  # Return True if at least one email was sent successfully

@app.route('/send_email', methods=['GET', 'POST'])
@login_required
def send_email():
    if 'email' not in session:
        return redirect(url_for('index'))

    if not os.path.exists(EMAIL_UPLOAD_FOLDER):
        os.makedirs(EMAIL_UPLOAD_FOLDER)

    taglist = get_taglist()
    individual_list = get_recipient_individual()

    if request.method == 'POST':
        recipient_type = request.form.get('recipient_type')
        email_subject = request.form.get('email_subject')
        email_content = request.form.get('email_content')
        attachments = request.files.getlist('attachments')
        from_email = request.form.get('from_email')
        reply_to = request.form.get('reply_to')
        selected_recipients = request.form.get('selected_recipients')  

        if recipient_type == 'group':
            # 使用前端刪減後的收件人列表
            try:
                # 嘗試解析 JSON，如果失敗則使用原始的客戶列表
                customers = json.loads(selected_recipients) if selected_recipients else []
                print("customers: ", customers)
                if not customers:
                    # 如果解析後的列表為空，則從原始來源獲取所有客戶
                    customers = get_recipient_info(request.form.get('recipient_group'))
            except json.JSONDecodeError:
                # 如果 JSON 解析失敗，從原始來源獲取所有客戶
                customers = get_recipient_info(request.form.get('recipient_group'))
        elif recipient_type == 'individual':
            selected_id = request.form.get('selected_individual')
            customers = [next(item for item in individual_list if item["id"] == selected_id)]
        else:
            return redirect(url_for('send_email'))

        if customers and email_subject and email_content:
            attachment_paths = []
            for attachment in attachments:
                if attachment:
                    filename = secure_filename(''.join(lazy_pinyin(attachment.filename)))
                    attachment_path = os.path.join(app.config['EMAIL_UPLOAD_FOLDER'], filename)
                    attachment.save(attachment_path)
                    attachment_paths.append(attachment_path)

            # 發送郵件給經過過濾的客戶
            success, success_count, failure_count = send_emails_to_customers(customers, email_subject, email_content, attachment_paths, from_email, reply_to)
            
            # 添加記錄
            record = EmailRecord(
                user_id=User.query.filter_by(email=session['email'].lower()).first().id,
                success_count=success_count,
                failure_count=failure_count,
                recipient_group=request.form.get('recipient_group') if recipient_type == 'group' else None,
                individual_recipient=customers[0]['email'] if recipient_type == 'individual' else None
            )
            db.session.add(record)
            db.session.commit()
            
            if success:
                return redirect(url_for('send_email', status='sent'))
            else:
                return redirect(url_for('send_email', status='error'))
            return redirect(url_for('send_email'))

    return render_template('send_email.html', taglist=taglist, email=session['email'], individual_list=individual_list, admin_users=ADMIN_USERS)

@app.route('/logout')
@login_required
def logout():
    # session.pop('email', None)
    # session.pop('password', None)
    session.clear()
    return redirect(url_for('login'))

################################################
##############   excel upload   ################
################################################
@app.route('/excelupload')
@login_required
def excelupload():
    return render_template('excelupload.html', email=session['email'], admin_users=ADMIN_USERS)

@app.route('/upload-excel', methods=['POST'])
def upload_excel():
    print("uploading.......")
    if 'excel_file' not in request.files:
        print("No file part in the request")
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['excel_file']
    if file.filename == '':
        print("No selected file")
        return jsonify({'error': 'No selected file'}), 400

    if file:
        print("get file")
        try: 
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            print(f"Attempting to save file to: {file_path}")
            file.save(file_path)
            print(f"File saved successfully: {file_path}")

            result = excel(file_path)
            # 添加記錄
            record = ExcelUploadRecord(
                user_id=User.query.filter_by(email=session['email'].lower()).first().id,
                success=result,
                filename=filename
            )
            db.session.add(record)
            db.session.commit()
            if result:
                os.remove(file_path)
                return jsonify({'message': 'File processed successfully'})
            else:
                os.remove(file_path)
                return jsonify({'error': 'File processing failed'}), 500
        except Exception as e:
            os.remove(file_path)
            print(f"Error during file upload and processing: {str(e)}")
            return jsonify({'error': str(e)}), 500

###################################################
###########           search             ##########
###################################################
@app.route('/run-linkedin-search', methods=['POST'])
@login_required
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
@login_required
def run_google_search():
    try:
        search()
        return jsonify({"message": "Google search completed successfully."})
    except subprocess.CalledProcessError as e:
        return jsonify({"message": f"An error occurred."})

@app.route('/run-custom-search', methods=['POST'])
@login_required
def run_custom_search():
    try:
        customSearch()
        return jsonify({"message": "Google custom search completed successfully."})
    except subprocess.CalledProcessError as e:
        return jsonify({"message": f"An error occurred."})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    #app.run(debug=True)
    app.run(debug=True, host='localhost', port=5000)