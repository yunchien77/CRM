from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.utils import secure_filename
from image2Text import ocr_image, imageProcess
from image2Class import process_business_card
from createData import createEntity
from createData_unconfirmed import createEntity_unconfirmed
from OnedriveUpload import uploadFile
from emailHistory import uploadHistory
import openai

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
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

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
    return render_template('index.html')

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

        ####################
        if 'file_path_list' in session:
            urls = []
            for count, value in enumerate(session['file_path_list']):
                new_filename = f"{NAME}-{COMPANY}-{date}-{count+1}-010-3{os.path.splitext(value)[1]}"
                nfile_path = os.path.join(os.path.dirname(value), new_filename)
                os.rename(value, nfile_path)
                urls.append(uploadFile(nfile_path))

            for i in urls:
                url += ("\n\n" + i)
        #########################
        session.pop('file_path', None)
        session.pop('file_path_list', None)
        createEntity(NAME, FIRST, LAST, COMPANY, DEPART1, DEPART2, TITLE1, TITLE2, TITLE3, MOBILE1, MOBILE2, TEL1, TEL2, FAX1, FAX2, ETITLE, EMAIL1, EMAIL2, ADDRESS1, ADDRESS2, WEBSITE, DESCRIPTION, url)
        remove_files('img/')

        return jsonify({'success': True}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400
        
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
            new_filename = f"{NAME}-{COMPANY}-{date}-010-3{os.path.splitext(file_path)[1]}"
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
                success = send_emails_to_customers(customers, email_subject, email_content, attachment_paths)
                if success:
                    date = datetime.now().strftime('%Y/%m/%d')
                    uploadHistory(customers, email_subject, email_content, date, session['email'])
                    return redirect(url_for('send_email', status='sent'))
                else:
                    return redirect(url_for('send_email', status='error'))

    return render_template('send_email.html', taglist=taglist, email=session['email'])

def send_emails_to_customers(customers, subject, content, attachment_paths):
    email = session['email']
    password = session['password']

    try:
        server = smtplib.SMTP('smtp.outlook.com', 587)
        server.starttls()
        server.login(email, password)

        for customer in customers:
            receiver_email = customer['email']
            receiver_name = customer['emailtitle']
            print(f'Sending email to {receiver_name} : {receiver_email}')

            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = email
            message["To"] = receiver_email

            ### 在郵件內文中添加{name}標籤會取代成郵件對應的名字
            html_content = content.replace('\n', '<br>').replace('{name}', receiver_name)
            message.attach(MIMEText(html_content, "html"))

            # 如果有上傳附件
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

if __name__ == '__main__':
    app.run(debug=True)
