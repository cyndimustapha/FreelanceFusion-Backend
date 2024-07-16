from flask import Flask, make_response, request, jsonify
from flask_migrate import Migrate
from flask_restful import Api, Resource, reqparse
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
from sqlalchemy import MetaData
from models import User, Bid, JobPosting, db
from config import Config

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configure the app
app.config.from_object(Config)

# Initialize extensions
metadata = MetaData()
db.init_app(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
api = Api(app)

# User Resource for handling user operations
class Users(Resource):
    @jwt_required()
    def get(self):
        current_user = get_jwt_identity()
        if current_user:
            users = User.query.all()
            users_list = [user.to_dict() for user in users]
            body = {
                "count": len(users_list),
                "users": users_list
            }
            return make_response(body, 200)
        else:
            return make_response({"message": "Unauthorized"}, 401)

    def post(self):
        try:
            email = request.json.get('email')
            existing_user = User.query.filter_by(email=email).first()

            if existing_user:
                return make_response({"message": "Email already taken"}, 422)

            new_user = User(
                username=request.json.get("username"),
                email=email,
                role=request.json.get("role"),
                password=bcrypt.generate_password_hash(request.json.get("password")).decode('utf-8')
            )

            db.session.add(new_user)
            db.session.commit()

            access_token = create_access_token(identity=new_user.id)

            response = {
                "user": new_user.to_dict(),
                "access_token": access_token
            }

            return make_response(response, 201)

        except Exception as e:
            return make_response({"message": str(e)}, 500)

@app.route('/login', methods=['POST', 'OPTIONS'])
def signin():
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        }
        return ('', 204, headers)

    try:
        email = request.json.get('email')
        password = request.json.get('password')

        user = User.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(user.password, password):
            access_token = create_access_token(identity=user.id)
            return make_response({
                "user": user.to_dict(),
                "access_token": access_token
            }, 200)
        else:
            return make_response({"message": "Invalid credentials"}, 401)

    except Exception as e:
        return make_response({"message": str(e)}, 500)
    
@app.route('/api/jobs', methods=['POST'])
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

@app.route('/api/jobs', methods=['GET'])
def get_jobs():
    jobs = JobPosting.query.all()
    return jsonify([job.to_dict() for job in jobs])

@app.route('/api/jobs/<int:job_id>', methods=['GET'])
def get_job(job_id):
    job = JobPosting.query.get(job_id)
    if job is None:
        return jsonify({"error": "Job not found"}), 404
    return jsonify(job.to_dict())

class BidResource(Resource):
    
    @jwt_required()
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('amount', type=float, required=True, help='Amount must be provided')
        parser.add_argument('job_id', type=int, required=True, help='Job ID must be provided')
        args = parser.parse_args()

        current_user_id = get_jwt_identity()
        if not current_user_id:
            return {'message': 'User not authenticated'}, 401

        job = JobPosting.query.get(args['job_id'])
        if not job:
            return {'message': 'Job not found'}, 404

        bid = Bid(
            amount=args['amount'],
            job_id=args['job_id'],
            freelancer_id=current_user_id
        )

        db.session.add(bid)
        db.session.commit()

        return {'message': 'Bid placed successfully', 'bid_id': bid.id}, 201

    @jwt_required()
    def get(self, job_id):
        current_user_id = get_jwt_identity()
        if not current_user_id:
            return {'message': 'User not authenticated'}, 401

        job = JobPosting.query.get(job_id)
        if not job:
            return {'message': 'Job not found'}, 404

        bids = Bid.query.filter_by(job_id=job_id).all()
        serialized_bids = [{'id': bid.id, 'amount': bid.amount, 'freelancer_id': bid.freelancer_id} for bid in bids]

        return {'bids': serialized_bids}, 200

    @jwt_required()
    def put(self, job_id):
        parser = reqparse.RequestParser()
        parser.add_argument('bid_id', type=int, required=True, help='Bid ID must be provided')
        args = parser.parse_args()

        current_user_id = get_jwt_identity()
        if not current_user_id:
            return {'message': 'User not authenticated'}, 401

        job = JobPosting.query.get(job_id)
        if not job:
            return {'message': 'Job not found'}, 404

        if job.client_id != current_user_id:
            return {'message': 'Only the client who posted the job can select a bid'}, 403

        bid = Bid.query.get(args['bid_id'])
        if not bid or bid.job_id != job_id:
            return {'message': 'Bid not found for this job'}, 404

        # Mark all bids for this job as not selected
        Bid.query.filter_by(job_id=job_id).update({'selected': False})

        # Mark the chosen bid as selected
        bid.selected = True
        db.session.commit()

        return {'message': 'Bid selected successfully'}, 200

# Add resources to API
api.add_resource(Users, '/users')
api.add_resource(BidResource, '/bids', '/bids/<int:job_id>')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
