from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    telegram_id = db.Column(db.BigInteger, unique=True, nullable=True)
    username = db.Column(db.String(64), nullable=False)
    avatar_url = db.Column(db.String(256))
    color = db.Column(db.String(8))