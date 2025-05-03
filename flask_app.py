from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv
import os
from app.routes import main

load_dotenv()
#flask конфигурация
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app = Flask(__name__)
app.register_blueprint(main)


if __name__ == '__main__':
    app.run(debug=True)