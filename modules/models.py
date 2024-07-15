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

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "location": self.location,
            "budget": self.budget,
            "companyName": self.companyName,
            "email": self.email
        }
