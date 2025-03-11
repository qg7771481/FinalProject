from flask import Flask, request, jsonify

from flask_login import LoginManager, login_user, login_required
from auth import hashed_password
from models import db, User, Question, Answer, Result
from flask_bcrypt import Bcrypt
import bcrypt


bcrypt = Bcrypt
login_manager = LoginManager()
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///python_quiz.db'
db.init_app(app)


def load_user(user_id):
    return User.query.get(int(user_id))


@app.get("/register/")
def register(User):
    email = request.args.get("email")
    password = request.args.get("password")
    if not email or not password:
        return jsonify({'error': 'Email и пароль обовязковий!'}), 400
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({'error': 'Користувач з таким емейл вже є'}), 400
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(email=email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    login_user(new_user)
    return jsonify({'message': 'Регистрація успішна!'})

@app.get("/login/")
def login():
    email = request.args.get("email")
    password = request.args.get("password")



@app.post("/check")
def check_answer():
    data = request.get_json()
    question = Question.query.get(data.get("id"))
    if question:
        is_correct = question.correct_answer == data.get("answer")
        return jsonify({"correct": is_correct})
    return jsonify({"error": "Питання не немає"}), 404


@app.post("/users")
def add_user():
    data = request.get_json()
    user = User(name=data["name"], email=data["email"])
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "Користвуча додано", "id": user.id})


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
