from flask import Flask, render_template, redirect, request, session, flash, url_for
import firebase_admin
from firebase_admin import credentials, auth

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Initialize Firebase
cred = credentials.Certificate("path/to/serviceAccountKey.json")
firebase_admin.initialize_app(cred)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        id_token = request.form.get('id_token')
        try:
            decoded_token = auth.verify_id_token(id_token)
            session['user'] = decoded_token['uid']
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        except Exception as e:
            flash(f'Login failed: {str(e)}', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))
