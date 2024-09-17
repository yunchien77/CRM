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
from googleSearch import search
from googleCustom import customSearch

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
from recipientList import get_recipient_info, get_recipient_individual
from getTagList import get_taglist
from duplicatedName import searchName
from pypinyin import lazy_pinyin

from concurrent.futures import ThreadPoolExecutor
import uuid
from datetime import datetime
import subprocess
import os
import json

app = Flask(__name__)
app.secret_key = 'your_secret_key'

app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

UPLOAD_FOLDER = 'img'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

EMAIL_UPLOAD_FOLDER = 'uploads'
app.config['EMAIL_UPLOAD_FOLDER'] = EMAIL_UPLOAD_FOLDER

# Authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'email' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
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
            return redirect(url_for('home'))
        except smtplib.SMTPAuthenticationError:
            flash('Invalid email or password. Please try again.', 'error')

    return render_template('login.html')

###################################################
###########   single upload (comfirmed)  ##########
###################################################
@app.route('/')
@login_required
def home():
    return render_template('index.html', email=session['email'])

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

        return jsonify({'success': True}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400
        
###################################################
########### multiple upload(uncomfirmed) ##########
###################################################

@app.route('/multiupload')
@login_required
def multiupload():
    return render_template('multiupload.html', email=session['email'])

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
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_file = {executor.submit(process_and_upload_image, file, ocr_engine, ocr_language): file for file in files}
        for future in future_to_file:
            result = future.result()
            results.append(result)

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

def send_email_to_customer(email, password, customer, subject, content, attachment_paths, from_email, reply_to):
    try:
        receiver_email = customer['email']
        receiver_name = customer['emailtitle']
        receiver_company = customer['company']
        receiver_title1 = customer['title1']
        receiver_title2 = customer['title2']
        receiver_title3 = customer['title3']
        receiver_department1 = customer['department1']
        receiver_department2 = customer['department2']
        print(f'Sending email to {receiver_name} : {receiver_email}')

        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = from_email
        message["To"] = receiver_email

        if reply_to:
            message.add_header('Reply-To', reply_to)

        html_content = content.replace('\n', '<br>').replace('{name}', receiver_name).replace('{company}', receiver_company).replace('{title1}', receiver_title1).replace('{title2}', receiver_title2).replace('{title3}', receiver_title3).replace('{department1}', receiver_department1).replace('{department2}', receiver_department2)
        message.attach(MIMEText(html_content, "html"))

        for attachment_path in attachment_paths:
            try:
                with open(attachment_path, "rb") as attachment_file:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(attachment_file.read())
                    encoders.encode_base64(part)
                    part.add_header(
                        "Content-Disposition",
                        f"attachment; filename= {os.path.basename(attachment_path)}",
                    )
                    message.attach(part)
            except Exception as e:
                print(f"Error attaching file {attachment_path}: {str(e)}")

        with smtplib.SMTP('smtp.outlook.com', 587, timeout=300) as server:
            server.starttls()
            server.login(email, password)
            server.sendmail(from_email, receiver_email, message.as_string())

        print(f'Email sent to {receiver_email} successfully')
        date = datetime.now().strftime('%Y/%m/%d')
        history_content = content.replace('{name}', receiver_name).replace('{company}', receiver_company).replace('{title1}', receiver_title1).replace('{title2}', receiver_title2).replace('{title3}', receiver_title3).replace('{department1}', receiver_department1).replace('{department2}', receiver_department2)
        uploadHistory(customer, subject, history_content, date, from_email)
        return True
    except smtplib.SMTPAuthenticationError:
        print(f"SMTP Authentication failed for {email}")
        return False
    except smtplib.SMTPException as e:
        print(f"SMTP error occurred while sending to {receiver_email}: {str(e)}")
        return False
    except Exception as e:
        print(f'Failed to send email to {receiver_email}. Error: {str(e)}')
        return False

def send_emails_to_customers(customers, subject, content, attachment_paths, from_email, reply_to):
    email = from_email or session['email']
    password = session['password']

    success_count = 0
    failure_count = 0

    for customer in customers:
        if send_email_to_customer(email, password, customer, subject, content, attachment_paths, email, reply_to):
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
    return success_count > 0  # Return True if at least one email was sent successfully

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
        selected_recipients = request.form.get('selected_recipients')  # <-- 修改點：接收選中的收件人

        if recipient_type == 'group':
            # 使用前端刪減後的收件人列表
            customers = json.loads(selected_recipients)  # <-- 修改點：將傳遞過來的收件人列表轉為 Python 物件
            print(customers)
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
            success = send_emails_to_customers(customers, email_subject, email_content, attachment_paths, from_email, reply_to)
            if success:
                return redirect(url_for('send_email', status='sent'))
            else:
                return redirect(url_for('send_email', status='error'))
            return redirect(url_for('send_email'))

    return render_template('send_email.html', taglist=taglist, email=session['email'], individual_list=individual_list)

@app.route('/logout')
@login_required
def logout():
    session.pop('email', None)
    session.pop('password', None)
    return redirect(url_for('login'))

################################################
##############   excel upload   ################
################################################
@app.route('/excelupload')
@login_required
def excelupload():
    return render_template('excelupload.html', email=session['email'])

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
            os.remove(file_path)
            return jsonify({'message': 'File processed successfully'})
        else:
            os.remove(file_path)
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
    app.run(debug=True)