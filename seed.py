import os
from datetime import datetime, timezone
from flask_bcrypt import Bcrypt
from models import db, User, JobPosting, Bid

bcrypt = Bcrypt()

def create_users():
    users = [
        {
            'name': 'Cyndi Mustapha',
            'email': 'cyndi@gmail.com',
            'password': 'password',
            'role': 'client'
        },
        {
            'name': 'Midge Maisel',
            'email': 'midge@gmail.com',
            'password': 'password',
            'role': 'client'
        },
        {
            'name': 'Alice Cullen',
            'email': 'alice@example.com',
            'password': 'password',
            'role': 'freelancer'
        },
        {
            'name': 'Lenny Bruce',
            'email': 'lenny@example.com',
            'password': 'password',
            'role': 'freelancer'
        }
    ]
    
    for user_data in users:
        hashed_password = bcrypt.generate_password_hash(user_data['password']).decode('utf-8')
        new_user = User(name=user_data['name'], email=user_data['email'], password=hashed_password, role=user_data['role'])
        db.session.add(new_user)
    
    db.session.commit()

def create_jobs():
    jobs = [
        {
            'title': 'Web Development Project',
            'description': 'Develop a website using Python and Flask',
            'budget': 2000,
            'client_id': 1 
        },
        {
            'title': 'Mobile App Design',
            'description': 'Design an iOS and Android app UI/UX',
            'budget': 1500,
            'client_id': 2  
        }
        
    ]
    
    for job_data in jobs:
        new_job = JobPosting(
            title=job_data['title'],
            description=job_data['description'],
            budget=job_data['budget'],
            client_id=job_data['client_id'],
            posted_date=datetime.now(timezone.utc)
        )
        db.session.add(new_job)
    
    db.session.commit()

def create_bids():
    bids = [
        {
            'amount': 1800,
            'job_id': 1,  # Web Development Project
            'freelancer_id': 3  # Alice Cullen (freelancer)
        },
        {
            'amount': 1400,
            'job_id': 2,  # Mobile App Design
            'freelancer_id': 4  # Lenny Bruce (freelancer)
        }
        
    ]
    
    for bid_data in bids:
        new_bid = Bid(
            amount=bid_data['amount'],
            job_id=bid_data['job_id'],
            freelancer_id=bid_data['freelancer_id'],
            bid_date=datetime.now(timezone.utc) 
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
