import smtplib
import threading
from flask import flash
import sqlite3
from email.message import EmailMessage


from werkzeug.security import generate_password_hash, check_password_hash


from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()  # 🚀 Run it on startup

app.secret_key = 'charles-secret-key-change-this'  # use a long random string in production


@app.route('/')
def home():
    return render_template('portfolio.html')


@app.route('/profile')
def profile():
    return render_template('profile.html')

def send_email(name, email, message):
    msg = EmailMessage()
    msg['Subject'] = f'New Message from {name}'
    msg['From'] = 'ajbobz.jagto@gmail.com'        # <- REPLACE THIS
    msg['To'] = 'ajbobz.jagto@gmail.com'          # <- REPLACE THIS (same or different)

    msg.set_content(f'''
    You received a new message from your contact form:

    Name: {name}
    Email: {email}
    Message:
    {message}
    ''')

    # Gmail SMTP login
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login('ajbobz.jagto@gmail.com', 'rujcdtxalgksrxzn')  # <--- REPLACE BOTH
        smtp.send_message(msg)


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']

        # Save to DB
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO messages (name, email, message)
            VALUES (?, ?, ?)
        ''', (name, email, message))
        conn.commit()
        conn.close()

        # Send email to yourself in background
        threading.Thread(target=send_email, args=(name, email, message)).start()

        flash('✅ Your message has been sent!', 'success')
        return redirect(url_for('contact'))

    return render_template('contact.html')  # Needed for GET requests

@app.route('/admin/messages')
def view_messages():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, email, message, created_at FROM messages ORDER BY created_at DESC')
    rows = cursor.fetchall()
    conn.close()
    return render_template('messages.html', messages=rows)


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        password = request.form['password']
        # Hardcoded hashed admin password (generated from Step 2)
        hashed_password = (
            'scrypt:32768:8:1$6syGnpXelr7sP6ji$69406d7c5b328423b266deb20ebf08b087768bc0d31f69f38ed638eecffc7cf07b49e5eeaa970fb0b40772fe406b715db4e6c1b3d91f51da547036c92cfcf7fa'
        )  # 🔁 Replace with your actual hash

        if check_password_hash(hashed_password, password):
            session['admin'] = True
            flash('✅ Logged in successfully.', 'success')
            return redirect(url_for('view_messages'))
        else:
            flash('❌ Incorrect password.', 'error')
            return redirect(url_for('admin_login'))
    return render_template('admin_login.html')




@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    return redirect(url_for('admin_login'))

@app.route('/admin/delete/<int:message_id>', methods=['POST'])
def delete_message(message_id):
    if not session.get('admin'):
        return redirect(url_for('admin_login'))

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('DELETE FROM messages WHERE id = ?', (message_id,))
    conn.commit()
    conn.close()

    flash('🗑 Message deleted.', 'success')
    return redirect(url_for('view_messages'))



@app.route('/admin/edit/<int:message_id>', methods=['GET', 'POST'])
def edit_message(message_id):
    if not session.get('admin'):
        return redirect(url_for('admin_login'))

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']

        cursor.execute('''
            UPDATE messages
            SET name = ?, email = ?, message = ?
            WHERE id = ?
        ''', (name, email, message, message_id))

        conn.commit()
        conn.close()

        flash('✏ Message updated successfully.', 'success')
        return redirect(url_for('view_messages'))

    # GET request: fetch current data
    cursor.execute('SELECT * FROM messages WHERE id = ?', (message_id,))
    message = cursor.fetchone()
    conn.close()

    if message:
        return render_template('edit.html', message=message)
    else:
        return "Message not found", 404




if __name__ == '__main__':
    app.run(debug=True)
    
