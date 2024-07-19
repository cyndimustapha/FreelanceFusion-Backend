from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import validates
import re
import pytz
from datetime import datetime

metadata = MetaData()
db = SQLAlchemy(metadata=metadata)

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(129), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())
    role = db.Column(db.Text)

    job_bidder = db.relationship('Bid', backref='freelancer')
    sent_messages = db.relationship('Message', foreign_keys='Message.sender_id', backref='sender', lazy=True)
    received_messages = db.relationship('Message', foreign_keys='Message.recipient_id', backref='recipient', lazy=True)

    @validates('email')
    def validate_email(self, key, email):
        regex = r'^\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if not re.match(regex, email):
            raise ValueError("Invalid email address")
        return email

    def __repr__(self):
        return f"<User {self.id}: {self.username}>"

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "created_at": self.created_at,
            "role": self.role
        }

class JobPosting(db.Model, SerializerMixin):
    __tablename__ = 'job_postings'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(100), nullable=False)
    budget = db.Column(db.Float, nullable=False)
    companyName = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)

    gig = db.relationship('Bid', backref='job')

    def __repr__(self):
        return f"JobPosting('{self.title}')"

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

class Bid(db.Model, SerializerMixin):
    __tablename__ = 'bids'

    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    freelancer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('job_postings.id'), nullable=False)
    selected = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"Bid('{self.amount}', '{self.freelancer_id}')"

    def to_dict(self):
        return {
            "id": self.id,
            "amount": self.amount,
            "freelancer": self.freelancer.to_dict(),
            "job": self.job.to_dict(),
            "selected": self.selected
        }

class Message(db.Model, SerializerMixin):
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    time = db.Column(db.DateTime, default=db.func.now())

    def __repr__(self):
        return f"<Message {self.id}: from {self.sender_id} to {self.recipient_id}>"

    def to_dict(self):
        # Nairobi timezone (GMT + 3)
        nairobi_tz = pytz.timezone('Africa/Nairobi')
        
        # Convert time to Nairobi timezone
        local_time = self.time.replace(tzinfo=pytz.utc).astimezone(nairobi_tz)
        return {
            "id": self.id,
            "sender": self.sender.to_dict(),
            "recipient": self.recipient.to_dict(),
            "message": self.message,
            "time": local_time.strftime('%a, %d %b %Y %H:%M:%S GMT%z') 
        }
