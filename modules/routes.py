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
        return jsonify({"message": "Job posted successfully!", "job": new_job.to_dict()})
