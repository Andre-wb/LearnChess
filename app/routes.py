from flask import Blueprint, render_template, session, request, jsonify
from app.models import db, User
import random
from flask_cors import CORS

main = Blueprint('main', __name__)

@main.route('/')
def base():
    return render_template('base.html')

@main.route('/main')
def main_page():
    return render_template('main.html')

@main.route('/stats')
def stats_page():
    return render_template('stats.html')


@main.route('/account')
def account_page():
    return render_template('account.html', user=session.get('user'))

@main.route('/set_user', methods=['POST'])
def set_user():
    user_data = request.get_json()
    session['user'] = {
        'id': user_data['id'],
        'first_name': user_data.get('first_name'),
        'username': user_data.get('username'),
        'avatar_url': user_data.get('photo_url')  # ← сохраняем ссылку
    }
    return '', 204

