import os
import json
from functools import wraps
from flask import (
    Flask, render_template, request, jsonify, redirect, url_for, session
)
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import auth as firebase_auth, credentials
import openai
from flask_cors import CORS

load_dotenv()

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///fitapp.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# initialize firebase admin
if os.path.exists(os.getenv('GOOGLE_APPLICATION_CREDENTIALS', '')):
    cred = credentials.Certificate(os.getenv('GOOGLE_APPLICATION_CREDENTIALS'))
    firebase_admin.initialize_app(cred)
else:
    # try application default creds
    try:
        firebase_admin.initialize_app()
    except Exception:
        print('Firebase admin not initialized — service account missing')

openai.api_key = os.getenv('OPENAI_API_KEY')

# ----- Models -----
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firebase_uid = db.Column(db.String(255), unique=True, nullable=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    name = db.Column(db.String(255), nullable=True)
    is_admin = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'is_admin': self.is_admin,
            'firebase_uid': self.firebase_uid
        }

# ----- Helpers -----
def verify_firebase_token(id_token):
    """Verify Firebase token. Returns decoded token or raises."""
    try:
        decoded = firebase_auth.verify_id_token(id_token)
        return decoded
    except Exception as e:
        raise

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # check session first
        if session.get('user'):
            return f(*args, **kwargs)
        # allow bearer token from frontend
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ', 1)[1]
            try:
                decoded = verify_firebase_token(token)
                uid = decoded.get('uid')
                user = User.query.filter_by(firebase_uid=uid).first()
                if not user:
                    # create user row if doesn't exist
                    user = User(firebase_uid=uid, email=decoded.get('email'))
                    db.session.add(user)
                    db.session.commit()
                # attach to request context via session
                session['user'] = user.to_dict()
                return f(*args, **kwargs)
            except Exception:
                return jsonify({'error': 'Invalid token'}), 401
        return jsonify({'error': 'Authentication required'}), 401
    return decorated

# ----- Routes (frontend pages) -----
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/signup')
def signup_page():
    return render_template('signup.html')

@app.route('/chatbot')
@login_required
def chatbot_page():
    return render_template('chatbot.html')

@app.route('/workout')
@login_required
def workout_page():
    return render_template('workout.html')

@app.route('/meal')
@login_required
def meal_page():
    return render_template('meal.html')

@app.route('/dashboard')
@login_required
def dashboard_page():
    return render_template('dashboard.html')

@app.route('/admin')
@login_required
def admin_page():
    user = session.get('user')
    if not user or not user.get('is_admin'):
        return "Forbidden", 403
    return render_template('admin.html')

# ----- API Endpoints -----
@app.route('/api/auth/session', methods=['POST'])
def create_session():
    """Frontend can post firebase idToken to create server-side session."""
    data = request.get_json() or {}
    id_token = data.get('idToken')
    if not id_token:
        return jsonify({'error': 'idToken required'}), 400
    try:
        decoded = verify_firebase_token(id_token)
        uid = decoded.get('uid')
        email = decoded.get('email')
        user = User.query.filter_by(firebase_uid=uid).first()
        if not user:
            user = User(firebase_uid=uid, email=email, name=decoded.get('name'))
            db.session.add(user)
            db.session.commit()
        session['user'] = user.to_dict()
        return jsonify({'user': user.to_dict()})
    except Exception as e:
        return jsonify({'error': 'Invalid token'}), 401

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    session.pop('user', None)
    return jsonify({'ok': True})

@app.route('/api/chat', methods=['POST'])
@login_required
def api_chat():
    payload = request.get_json() or {}
    prompt = payload.get('prompt', '')
    if not prompt:
        return jsonify({'error': 'prompt required'}), 400
    try:
        # simple OpenAI chat completion
        resp = openai.ChatCompletion.create(
            model='gpt-4o-mini',
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500
        )
        text = resp.choices[0].message.content
        return jsonify({'reply': text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/workout', methods=['POST'])
@login_required
def api_workout():
    data = request.get_json() or {}
    # expected: goal, days_per_week, level, preferences
    goal = data.get('goal', 'general fitness')
    days = int(data.get('days_per_week', 3))
    level = data.get('level', 'beginner')

    prompt = f"Generate a {days}-day per week {level} workout plan for {goal}. Provide exercises, sets, reps, and short warmup/cooldown."
    try:
        resp = openai.ChatCompletion.create(
            model='gpt-4o-mini',
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800
        )
        plan = resp.choices[0].message.content
        return jsonify({'plan': plan})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/meal', methods=['POST'])
@login_required
def api_meal():
    data = request.get_json() or {}
    calories = data.get('calories', 2000)
    diet = data.get('diet', 'balanced')

    prompt = f"Create a 7-day {diet} meal plan for ~{calories} kcal/day with recipes and grocery list."
    try:
        resp = openai.ChatCompletion.create(
            model='gpt-4o-mini',
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1200
        )
        plan = resp.choices[0].message.content
        return jsonify({'plan': plan})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
@login_required
def api_stats():
    # stubbed sample stats
    stats = {
        'weekly_workouts': [0,1,2,3,4,2,1],
        'calories': [2200,2100,2000,2300,1900,1800,2000]
    }
    return jsonify({'stats': stats})

# utility route to create DB tables
@app.cli.command('init-db')
def init_db():
    db.create_all()
    print('DB initialized')

if __name__ == '__main__':
    # create DB if missing
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)), debug=(os.getenv('FLASK_ENV')!='production'))
