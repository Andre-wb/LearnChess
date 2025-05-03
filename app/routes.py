from flask import Blueprint, render_template

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
    return render_template('account.html')