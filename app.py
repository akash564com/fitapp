from flask import Flask, render_template, redirect, request, session, flash, url_for
import firebase_admin
from firebase_admin import credentials, auth
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this for production!

# Dummy user database (replace with real database in production)
users = {
    'user@example.com': {
        'password': 'userpass',
        'name': 'John User',
        'role': 'user'
    },
    'admin@example.com': {
        'password': 'adminpass',
        'name': 'Admin',
        'role': 'admin'
    }
}

# Decorator for login-required routes
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            flash('Please log in first!', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Decorator for admin-only routes
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session or session.get('role') != 'admin':
            flash('Admin access required!', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = users.get(email)
        if user and user['password'] == password:
            session['user'] = email
            session['name'] = user['name']
            session['role'] = user['role']
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials!', 'danger')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Add actual user registration logic here
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', name=session.get('name'))

@app.route('/chatbot')
@login_required
def chatbot():
    return render_template('chatbot.html')

@app.route('/workout')
@login_required
def workout():
    return render_template('workout.html')

@app.route('/meal')
@login_required
def meal():
    return render_template('meal.html')

@app.route('/admin')
@admin_required
def admin():
    return render_template('admin.html')

# Example form processing routes
@app.route('/generate_workout', methods=['POST'])
@login_required
def generate_workout():
    # Add workout generation logic here
    goal = request.form.get('goal')
    level = request.form.get('level')
    # Process inputs and generate workout
    flash('Workout plan generated!', 'success')
    return redirect(url_for('workout'))

@app.route('/generate_meal', methods=['POST'])
@login_required
def generate_meal():
    # Add meal plan generation logic here
    diet = request.form.get('diet')
    calories = request.form.get('calories')
    # Process inputs and generate meal plan
    flash('Meal plan generated!', 'success')
    return redirect(url_for('meal'))

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
