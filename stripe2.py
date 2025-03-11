from flask import Flask, request, jsonify
from models import db, User, Question, Answer, Result

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///python_quiz.db'
db.init_app(app)


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
