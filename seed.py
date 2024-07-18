import os
import random
from datetime import datetime, timezone, timedelta
from flask_bcrypt import Bcrypt
from models import db, User, JobPosting, Bid, Message

bcrypt = Bcrypt()

def create_users():
    users = [
        {
            'username': 'Cyndi Mustapha',
            'email': 'cyndi@gmail.com',
            'password': 'password',
            'role': 'client'
        },
        {
            'username': 'Midge Maisel',
            'email': 'midge@gmail.com',
            'password': 'password',
            'role': 'client'
        },
        {
            'username': 'Alice Cullen',
            'email': 'alice@example.com',
            'password': 'password',
            'role': 'freelancer'
        },
        {
            'username': 'Lenny Bruce',
            'email': 'lenny@example.com',
            'password': 'password',
            'role': 'freelancer'
        }
    ]

    # Ensure the database is empty
    User.query.delete()
    
    for user_data in users:
        hashed_password = bcrypt.generate_password_hash(user_data['password']).decode('utf-8')
        new_user = User(username=user_data['username'], email=user_data['email'], password=hashed_password, role=user_data['role'])
        db.session.add(new_user)
    
    db.session.commit()

def create_jobs():
    # List of example locations
    locations = [
        "New York, NY",
        "Los Angeles, CA",
        "Chicago, IL",
        "Houston, TX",
        "Phoenix, AZ",
        "San Francisco, CA",
        "Austin, TX",
        "Seattle, WA",
        "Boston, MA",
        "Denver, CO"
    ]
    jobs = [
        {
            'title': 'Web Development Project',
            'description': 'Develop a website using Python and Flask',
            'location': random.choice(locations),
            'budget': 2000,
            'companyName': 'Company A',
            'email': 'jobs@companya.com'
        },
        {
            'title': 'Mobile App Design',
            'description': 'Design an iOS and Android app UI/UX',
            'location': random.choice(locations),
            'budget': 1500,
            'companyName': 'Company B',
            'email': 'companyb@gmail.com'
        },
        {
            'title': 'Data Analysis Project',
            'description': 'Analyze data using machine learning techniques',
            'location': random.choice(locations),
            'budget': 2500,
            'companyName': 'Company C',
            'email': 'jobs@companyc.com'
        },
        {
            'title': 'Graphic Design Work',
            'description': 'Create graphics for a marketing campaign',
            'location': random.choice(locations),
            'budget': 1000,
            'companyName': 'Company D',
            'email': 'design@companyd.com'
        }
        
    ]
    # Ensure the database is empty
    JobPosting.query.delete()
    for job_data in jobs:
        new_job = JobPosting(
            title=job_data['title'],
            description=job_data['description'],
            budget=job_data['budget'],
            companyName=job_data['companyName'],
            email=job_data['email'],
            location=job_data['location']
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
    # Ensure the database is empty
    Bid.query.delete()
    for bid_data in bids:
        new_bid = Bid(
            amount=bid_data['amount'],
            job_id=bid_data['job_id'],
            freelancer_id=bid_data['freelancer_id']
        )
        db.session.add(new_bid)

    db.session.commit()

# Seed the database with messages
def seed_messages():
    # List of example messages
    example_messages = [
        "Hello! How are you?",
        "I'm interested in your job posting.",
        "Can we discuss the project details?",
        "Please let me know if you have any questions.",
        "Thank you for your response.",
        "Looking forward to working with you.",
        "Do you need any further information?",
        "Let's schedule a meeting.",
        "I have attached the project proposal.",
        "Please review the attached document.",
        "Can you provide an update on the project?",
        "What is the expected timeline?",
        "Do you have any specific requirements?",
        "Thank you for your feedback.",
        "Let's discuss the next steps.",
        "I will get back to you soon.",
        "Can you clarify the project scope?",
        "Please find the updated document attached.",
        "Do you have any preferences?",
        "Thank you for your cooperation.",
        "Let's finalize the project details.",
        "I appreciate your assistance.",
        "Can you confirm the meeting time?",
        "Please let me know your availability.",
        "Looking forward to hearing from you.",
        "Can you provide more details?",
        "Thank you for your patience.",
        "Let's move forward with the project.",
        "I have made the requested changes.",
        "Please let me know if everything is okay.",
        "Can we arrange a call to discuss further?",
        "I am available at your convenience.",
        "Thank you for your time.",
        "I will send you the updated proposal.",
        "Let's proceed with the agreed plan.",
        "I will keep you updated on the progress.",
        "Can you review the attached file?",
        "Please let me know if you need anything else.",
        "Thank you for the opportunity.",
        "Looking forward to your response.",
        "Can we schedule a follow-up meeting?",
        "I have noted your comments.",
        "Please confirm receipt of this message.",
        "Do you need any additional information?",
        "Thank you for your consideration.",
        "Let's touch base next week.",
        "I appreciate your prompt response.",
        "Can you send me the necessary documents?",
        "Please let me know if you have any concerns.",
        "Thank you for your understanding."
    ]

    with app.app_context():
        # Ensure the database is empty
        Message.query.delete()

        # List of user ids
        user_ids = [1, 2, 3, 4]

        for _ in range(50):
            sender_id = random.choice(user_ids)
            recipient_id = random.choice([uid for uid in user_ids if uid != sender_id])
            message_text = random.choice(example_messages)
            time_sent = datetime.utcnow() - timedelta(days=random.randint(0, 30))

            new_message = Message(
                sender_id=sender_id,
                recipient_id=recipient_id,
                message=message_text,
                time=time_sent
            )

            db.session.add(new_message)

        db.session.commit()
        print("Database seeded with 50 messages.")

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
        seed_messages()
        
        print('Database seeding completed.')

