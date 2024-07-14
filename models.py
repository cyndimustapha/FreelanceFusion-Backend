from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class JobPosting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(100), nullable=False)
    budget = db.Column(db.Float, nullable=False)
    companyName = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)

def init_app(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()
