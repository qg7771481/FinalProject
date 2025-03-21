from flask import Flask, request, jsonify, redirect, render_template, url_for
import secrets
from app import app
import random
from flask_mail import Mail, Message
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from models import db, User, Question, Answer, Result
from flask_bcrypt import Bcrypt
import string
import bcrypt
from config import API_KEY, PHONE_SEND


app.config.from_object('config')
mail = Mail(app)
verification_codes = {}
bcrypts = Bcrypt()
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///python_quiz.db'
db.init_app(app)
app.secret_key = API_KEY
login_manager = LoginManager(app)
login_manager.login_view = "login"



def send_verification_email(email):
    code = str(random.randint(100000, 999999))
    verification_codes[email] = code
    msg = Message('Email Verification', sender=app.config['MAIL_USERNAME'], recipients=[email])
    msg.body = f'Your verification code: {code}'
    mail.send(msg)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.get('/')
@login_required
def start():
    return render_template('index.html')


@app.get("/register/")
def register():
    return render_template("register.html")


@app.post("/register/")
def register_post():
    email = request.form.get("email")
    password = request.form.get("password")
    if not email or not password:
        return render_template("register.html", error="Check your email or password")
    user = User.query.filter_by(email=email).first()
    if user and user.is_verified:
        return render_template("register.html", error="User with this email already exists")
    verification_code = str(random.randint(100000, 999999))
    verification_codes[email] = verification_code
    if not user:
        hashed_password = generate_password_hash(password)
        user = User(email=email, password=hashed_password)
        db.session.add(user)
    user.is_verified = False
    db.session.commit()
    send_verification_email(email, verification_code)
    return render_template("verify.html", email=email)


@app.post("/verify/")
def verify_email():
    email = request.form.get("email")
    code = request.form.get("code")
    user = User.query.filter_by(email=email).first()
    if not user or verification_codes.get(email) != code:
        return render_template("verify.html", email=email, error="Invalid code")
    user.is_verified = True
    db.session.commit()
    login_user(user)
    del verification_codes[email]
    return redirect(url_for("start"))



@app.get("/login/")
def login():
    return render_template("login.html")


@app.post("/login/")
def login_post():
    email = request.form.get("email")
    password = request.form.get("password")
    if not email or not password:
        return render_template("login.html", error="Check your email or password")
    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password, password):
        login_user(user)
        return redirect(url_for("start"))
    return render_template("login.html", error="Invalid credentials")



@app.get('/tests/')
@login_required
def tests():
    tests = Question.query.all()
    return render_template('tests.html', tests=tests)


@app.post('/tests/submit/')
@login_required
def submit_test():
    data = request.form
    correct_answers = 0
    total_questions = len(data)
    for question_id, answer in data.items():
        question = Question.query.get(int(question_id))
        if question and question.correct_answer == answer:
            correct_answers += 1
    score = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
    result = Result(user_id=current_user.id, score=score)
    db.session.add(result)
    db.session.commit()
    return render_template('result.html', score=score)


@app.post("/check")
def check_answer():
    data = request.get_json()
    question = Question.query.get(data.get("id"))
    if question:
        is_correct = question.correct_answer == data.get("answer")
        return jsonify({"correct": is_correct})
    return jsonify({"error": "Question not found"}), 404



@app.post("/users")
def add_user():
    data = request.get_json()
    if not data.get("name") or not data.get("email"):
        return jsonify({"error": "Missing name or email"}), 400
    random_password = secrets.token_hex(8)
    user = User(
        name=data["name"],
        email=data["email"],
        password=generate_password_hash(random_password)
    )
    db.session.add(user)
    db.session.commit()
    return render_template("user_added.html", user=user)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)

