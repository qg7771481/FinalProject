from flask import Flask, request, jsonify, redirect, render_template

import random
from flask_login import LoginManager, login_user, login_required, logout_user
from models import db, User, Question, Answer, Result
from flask_bcrypt import Bcrypt
import requests
import string
import bcrypt
from config import API_KEY, PHONE_SEND


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        number = request.form['number']

    code = ''.join(random.choice(string.ascii_letters) for _ in range(5))

    sms_data = {
        "number": phone_send,
        "destination": number,
        "text": code}


    headers = {'Authorization': f'Bearer {API_KEY}'}

    response = requests.post(url="https://api.exolve.ru/messaging/v1/SendSMS",
                             json=sms_data, headers=headers)

    if response.status_code == 200:
        generated_codes[number] = code
        return render_template('verify.html', number=number)
    else:
        return f"Ошибка при отправке SMS: {response.status_code}"

    return render_template('signup.html')
