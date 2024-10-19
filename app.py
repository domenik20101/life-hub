from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os

# Создаем Flask-приложение
app = Flask(__name__)

# Настройка подключения к базе данных
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lifehub.db'  # Используем SQLite для тестов
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Инициализация базы данных
db = SQLAlchemy(app)

# Модель для пользователя
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Модель для трекинга параметров здоровья
class HealthTracking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    sleep_hours = db.Column(db.Float, nullable=True)
    stress_level = db.Column(db.Integer, nullable=True)
    physical_activity = db.Column(db.Float, nullable=True)

# Модель для курсов и прогресса
class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)

class UserCourseProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    progress = db.Column(db.Float, nullable=False)

# Модель для целей по экологии
class EcoGoal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    is_completed = db.Column(db.Boolean, default=False)

# Модель для социальной сети
class Community(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)

class CommunityPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    community_id = db.Column(db.Integer, db.ForeignKey('community.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())

# Создание всех таблиц в базе данных
with app.app_context():
    db.create_all()

# Маршруты для различных функций
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
        return jsonify({"message": "User with this username or email already exists."}), 400
    new_user = User(username=username, email=email, password=password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User registered successfully."}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify({"message": "Invalid username or password."}), 401
    return jsonify({"message": "Login successful."}), 200

@app.route('/health/track', methods=['POST'])
def track_health():
    data = request.get_json()
    user_id = data.get('user_id')
    date = data.get('date')
    sleep_hours = data.get('sleep_hours')
    stress_level = data.get('stress_level')
    physical_activity = data.get('physical_activity')
    new_entry = HealthTracking(user_id=user_id, date=date, sleep_hours=sleep_hours,
                               stress_level=stress_level, physical_activity=physical_activity)
    db.session.add(new_entry)
    db.session.commit()
    return jsonify({"message": "Health tracking data added successfully."}), 201

@app.route('/courses', methods=['POST'])
def add_course():
    data = request.get_json()
    title = data.get('title')
    description = data.get('description')
    new_course = Course(title=title, description=description)
    db.session.add(new_course)
    db.session.commit()
    return jsonify({"message": "Course added successfully."}), 201

@app.route('/eco/goals', methods=['POST'])
def add_eco_goal():
    data = request.get_json()
    user_id = data.get('user_id')
    description = data.get('description')
    new_goal = EcoGoal(user_id=user_id, description=description)
    db.session.add(new_goal)
    db.session.commit()
    return jsonify({"message": "Eco goal added successfully."}), 201

@app.route('/community/post', methods=['POST'])
def add_community_post():
    data = request.get_json()
    community_id = data.get('community_id')
    user_id = data.get('user_id')
    content = data.get('content')
    new_post = CommunityPost(community_id=community_id, user_id=user_id, content=content)
    db.session.add(new_post)
    db.session.commit()
    return jsonify({"message": "Community post added successfully."}), 201

if __name__ == '__main__':
    app.run(debug=True)
