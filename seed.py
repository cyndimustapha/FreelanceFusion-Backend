# seed.py
import os
from datetime import datetime
from flask_bcrypt import Bcrypt
from models import db, User, Job, Bid

bcrypt = Bcrypt()

def create_users():
    users = [
        {
            'name': 'Cyndi Mustapha',
            'email': 'cyndi@gmail.com',
            'password': 'password'
        },
        {
            'name': 'Natalia Juma',
            'email': 'natalia@gmail.com',
            'password': 'password'
        }
        
    ]
    
    for user_data in users:
        hashed_password = bcrypt.generate_password_hash(user_data['password']).decode('utf-8')
        new_user = User(name=user_data['name'], email=user_data['email'], password=hashed_password)
        db.session.add(new_user)
    
    db.session.commit()

def create_jobs():
    jobs = [
        {
            'title': 'Web Development Project',
            'description': 'Develop a website using Python and Flask',
            'budget': 3000,
            'client_id': 1 
        },
        {
            'title': 'Crotchet Project',
            'description': 'Crotchet a sweater from scratch',
            'budget': 1500,
            'client_id': 2  
        }
        
    ]
    
    for job_data in jobs:
        new_job = Job(
            title=job_data['title'],
            description=job_data['description'],
            budget=job_data['budget'],
            client_id=job_data['client_id'],
            posted_date=datetime.utcnow()
        )
        db.session.add(new_job)
    
    db.session.commit()

def create_bids():
    bids = [
        {
            'amount': 1800,
            'job_id': 1, 
            'freelancer_id': 2  
        },
        {
            'amount': 1400,
            'job_id': 2,  # Assuming job with ID 2 is Mobile App Design
            'freelancer_id': 1  # Assuming user with ID 1 is John Doe
        }
        
    ]
    
    for bid_data in bids:
        new_bid = Bid(
            amount=bid_data['amount'],
            job_id=bid_data['job_id'],
            freelancer_id=bid_data['freelancer_id']
        )
        db.session.add(new_bid)
    
    db.session.commit()

if __name__ == '__main__':
    # Initialize Flask app context
    from app import app
    with app.app_context():
        # Create tables 
        db.create_all()
        
        # Populate tables with initial data
        create_users()
        create_jobs()
        create_bids()
        
        print('Database seeding completed.')
