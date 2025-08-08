from flask import Flask, render_template, redirect, request, session, flash, url_for
import firebase_admin
from firebase_admin import credentials, auth
from functools import wraps

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


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session or not session['user'].get('is_admin'):
            flash('Admin access required', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/admin')
@admin_required
def admin_dashboard():
    # Fetch users from Firebase
    users = []
    for user in auth.list_users().iterate_all():
        users.append({
            'uid': user.uid,
            'email': user.email,
            'created': user.user_metadata.creation_timestamp
        })
    
    return render_template('admin.html', users=users)

@app.route('/admin/make_admin/<uid>')
@admin_required
def make_admin(uid):
    # Set custom claim for admin
    auth.set_custom_user_claims(uid, {'admin': True})
    flash('User promoted to admin', 'success')
    return redirect(url_for('admin_dashboard'))
