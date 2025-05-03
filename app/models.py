from flask_app import db

class User(db.Model):
    telegram_id = db.Column(db.Integer, primary_key=True)
    id = db.Column(db.String, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)\

def create_db():
    from flask_app import app, db
    with app.app_context():
        db.create_all()

def drop_db():
    from flask_app import app, db
    with app.app_context():
        db.drop_all()