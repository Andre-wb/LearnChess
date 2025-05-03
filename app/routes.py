from flask import Blueprint, render_template, session, request, jsonify
from app.models import db, User
import random

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
    telegram_id = session.get('telegram_id')
    if not telegram_id:
        return "Вы не авторизованы", 403

    user = User.query.filter_by(telegram_id=telegram_id).first()
    if not user:
        return "Пользователь не найден", 404

    return render_template('account.html', user=user)

@main.route('/api/telegram-login', methods=['POST'])
def telegram_login():
    data = request.get_json()
    telegram_id = data.get('telegram_id')
    if not telegram_id:
        return jsonify({"status": "error", "message": "Missing telegram_id"}), 400

    user = User.query.filter_by(telegram_id=telegram_id).first()

    if not user:
        def generate_color():
            return f"#{random.randint(0, 0xFFFFFF):06x}"

        user = User(
            telegram_id=telegram_id,
            name=data.get("first_name", "Unknown"),
            avatar_url=data.get("avatar_url"),
            color=generate_color(),
        )
        db.session.add(user)
        db.session.commit()

    return jsonify({
        "status": "ok",
        "user": {
            "name": user.name,
            "avatar_url": user.avatar_url,
            "color": user.color
        }
    })
