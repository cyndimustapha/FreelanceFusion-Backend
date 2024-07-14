from flask import request, jsonify
from .models import db, JobPosting

def init_routes(app):
    @app.route('/job', methods=['POST'])
    def create_job():
        data = request.json
        new_job = JobPosting(
            title=data['title'],
            description=data['description'],
            location=data['location'],
            budget=data['budget'],
            companyName=data['companyName'],
            email=data['email']
        )
        db.session.add(new_job)
        db.session.commit()
        return jsonify({"message": "Job posted successfully!"})


    JobPosting.to_dict = lambda self: {
        "id": self.id,
        "title": self.title,
        "description": self.description,
        "location": self.location,
        "budget": self.budget,
        "companyName": self.companyName,
        "email": self.email
    }
