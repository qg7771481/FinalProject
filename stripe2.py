from statistics import correlation

from flask import Flask, request, jsonify, redirect, render_template, url_for
import secrets
import random
from flask_mail import Mail, Message
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from sqlalchemy.util.langhelpers import repr_tuple_names
from werkzeug.security import generate_password_hash, check_password_hash

from models import db, User, Question, Answer, Result
from flask_bcrypt import Bcrypt
import string
import bcrypt
from config import MAIL_USERNAME, MAIL_PASSWORD, MAIL_SERVER, MAIL_PORT, MAIL_USE_TLS, MAIL_DEFAULT_SENDER



app = Flask(__name__)
app.config['SECRET_KEY'] = 'qg777'
app.config.from_pyfile('config.py')
mail = Mail(app)
verification_codes = {}
bcrypts = Bcrypt(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///python_quiz.db'
db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"
app.debug = True


@app.get("/test_mail/")
def test_mail():
    try:
        msg = Message("Test email", recipients=["ddavidok845@gmail.com"])
        msg.body = "Its test listok"
        mail.send(msg)
        return "list otpravlen!"
    except Exception as e:
        return f"Error: {e}"


def send_verification_email(email):
    verification_code = str(random.randint(100000, 999999))
    verification_codes[email] = verification_code
    msg = Message("Verification Code",
                  sender="noreply@example.com",
                  recipients=[email])
    msg.body = f"Your verification code is: {verification_code}"
    try:
        mail.send(msg)
        print(f"Verification email sent to {email}")
    except Exception as e:
        print(f"Error sending email: {e}")


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.get('/logout/')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.get('/home/')
@login_required
def start():
    return render_template('index.html')


@app.get("/register/")
def register():
    return render_template("register.html")


@app.post("/register/")
def register_post():
    print("register_post was called")
    name = request.form.get("name")
    email = request.form.get("email")
    password = request.form.get("password")
    if not name or not email or not password:
        return render_template("register.html", error="Check your name, email, or password")
    user = User.query.filter_by(email=email).first()
    if user:
        print("User already exists, stopping registration.")
        return render_template("register.html", error="User with this email already exists")
    verification_code = str(random.randint(100000, 999999))
    verification_codes[email] = verification_code
    hashed_password = generate_password_hash(password)
    user = User(name=name, email=email, password=hashed_password)
    db.session.add(user)
    db.session.commit()
    send_verification_email(email)
    return redirect(url_for("verify_email", email=email))



@app.route("/verify/", methods=["GET", "POST"])
def verify_email():
    if request.method == "POST":
        email = request.form.get('email')
        code = request.form.get("code")
        user = User.query.filter_by(email=email).first()
        if not user or verification_codes.get(email) != code:
            return render_template("verify.html", email=email, error="Invalid code")
        user.is_verified = True
        db.session.commit()
        del verification_codes[email]
        return redirect(url_for("profile"))
    email = request.args.get('email')
    return render_template("verify.html", email=email)


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
    return render_template('test.html', tests=tests)


@app.post('/tests/submit/')
@login_required
def submit_test():
    data = request.form
    correct_answers = 0
    total_questions = len(data)
    for question_id, answer in data.items():
        question = Question.query.get(int(question_id))
        if question:
            is_correct = question.correct_answer == answer
            if is_correct:
                correct_answers += 1
            result = Result(
                user_id=current_user.id,
                question_id=question.id,
                selected_answer=answer,
                is_correct=is_correct,
                score=0
            )
            db.session.add(result)
    score = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
    for r in current_user.results:
        r.score = score
    db.session.commit()
    return render_template('result.html', score=score)



@app.get("/profile/")
@login_required
def profile():
    user_results = Result.query.filter_by(user_id=current_user.id).all()
    if user_results:
        average_score = sum(result.score for result in user_results) / len(user_results)
    else:
        average_score = 0
    return render_template("profile.html", average_score=average_score)



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


@app.get("/admin_page/")
def admin_page():
    questions = Question.query.all()
    return render_template("admin_page.html", questions=questions)


@app.post("/admin_page/")
def add_questions():
    text = request.form.get("question")
    correct_answer = request.form.get("correct_answer")
    if text and correct_answer:
        db.session.add(Question(text=text, correct_answer=correct_answer))
        db.session.commit()
    return redirect(url_for('admin_page'))



if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)


