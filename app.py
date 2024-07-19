from flask import Flask, make_response, request, jsonify
from flask_migrate import Migrate
from flask_restful import Api, Resource, reqparse
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
from sqlalchemy import MetaData
from models import User, Bid, JobPosting, db, Message
from config import Config
from datetime import datetime, timezone
from flasgger import Swagger, swag_from

# Initialize Flask app
app = Flask(__name__)
swagger = Swagger(app)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:5173"}}, supports_credentials=True)

# Configure the app
app.config.from_object(Config)

# Initialize extensions
metadata = MetaData()
db.init_app(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
api = Api(app)

@app.before_request
def log_request_info():
    app.logger.debug('Headers: %s', request.headers)
    app.logger.debug('Body: %s', request.get_data())

# User Resource for handling user operations
class Users(Resource):
    @jwt_required()
    @swag_from({
        'responses': {
            200: {
                'description': 'List of users',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'count': {'type': 'integer'},
                        'users': {
                            'type': 'array',
                            'items': {'type': 'object'}
                        },
                        'user': {'type': 'object'}
                    }
                }
            },
            401: {
                'description': 'Unauthorized'
            }
        }
    })
    def get(self):
        if request.method == 'OPTIONS':
            response = app.make_default_options_response()
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Authorization, Content-Type'
            return response
        current_user = get_jwt_identity()
        if current_user:
            users = User.query.all()
            users_list = [user.to_dict() for user in users]
            body = {
                "count": len(users_list),
                "users": users_list,
                "user": current_user
            }
            return make_response(body, 200)
        else:
            return make_response({"message": "Unauthorized"}, 401)

    @swag_from({
        'responses': {
            201: {
                'description': 'User created successfully',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'user': {'type': 'object'},
                        'access_token': {'type': 'string'}
                    }
                }
            },
            422: {
                'description': 'Email already taken'
            },
            500: {
                'description': 'Internal server error'
            }
        }
    })
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
@swag_from({
    'responses': {
        200: {
            'description': 'User signed in successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'user': {'type': 'object'},
                    'access_token': {'type': 'string'}
                }
            }
        },
        401: {
            'description': 'Invalid credentials'
        },
        400: {
            'description': 'Request must be JSON'
        },
        500: {
            'description': 'Internal server error'
        }
    }
})
def signin():
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        }
        return '', 204, headers

    try:
        if request.is_json:
            data = request.get_json()
            email = data.get('email')
            password = data.get('password')

            user = User.query.filter_by(email=email).first()

            if user and bcrypt.check_password_hash(user.password, password):
                access_token = create_access_token(identity=user.id)
                return make_response({
                    "user": user.to_dict(),
                    "access_token": access_token
                }, 200)
            else:
                return make_response({"message": "Invalid credentials"}, 401)
        else:
            return make_response({"message": "Request must be JSON"}, 400)

    except Exception as e:
        return make_response({"message": str(e)}, 500)
    
@app.route('/api/jobs', methods=['POST'])
@swag_from({
    'responses': {
        201: {
            'description': 'Job posted successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string'},
                    'job': {'type': 'object'}
                }
            }
        }
    }
})
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
@swag_from({
    'responses': {
        200: {
            'description': 'List of jobs',
            'schema': {
                'type': 'array',
                'items': {'type': 'object'}
            }
        }
    }
})
def get_jobs():
    jobs = JobPosting.query.all()
    return jsonify([job.to_dict() for job in jobs])

@app.route('/api/jobs/<int:job_id>', methods=['GET'])
@swag_from({
    'responses': {
        200: {
            'description': 'Job details',
            'schema': {'type': 'object'}
        },
        404: {
            'description': 'Job not found'
        }
    }
})
def get_job(job_id):
    job = JobPosting.query.get(job_id)
    if job is None:
        return jsonify({"error": "Job not found"}), 404
    return jsonify(job.to_dict())

class BidResource(Resource):
    @jwt_required()
    @swag_from({
        'responses': {
            201: {
                'description': 'Bid placed successfully',
                'schema': {'type': 'object'}
            },
            401: {
                'description': 'User not authenticated'
            },
            404: {
                'description': 'Job not found'
            }
        }
    })
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
    @swag_from({
        'responses': {
            200: {
                'description': 'List of bids',
                'schema': {
                    'type': 'array',
                    'items': {'type': 'object'}
                }
            },
            401: {
                'description': 'User not authenticated'
            },
            404: {
                'description': 'Job not found'
            }
        }
    })
    def get(self, job_id):
        if request.method == 'OPTIONS':
            response = app.make_default_options_response()
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Authorization, Content-Type'
            return response
        current_user_id = get_jwt_identity()
        if not current_user_id:
            return {'message': 'User not authenticated'}, 401

        job = JobPosting.query.get(job_id)
        if not job:
            return {'message': 'Job not found'}, 404

        bids = Bid.query.filter_by(job_id=job_id).all()
        serialized_bids = [{'id': bid.id, 'amount': bid.amount, 'freelancer': {'username': bid.freelancer.username, 'email': bid.freelancer.email}, 'job': bid.job.to_dict()} for bid in bids]

        return {'bids': serialized_bids}, 200

    @jwt_required()
    @swag_from({
        'responses': {
            200: {
                'description': 'Bid selected successfully'
            },
            401: {
                'description': 'User not authenticated'
            },
            403: {
                'description': 'Only the client who posted the job can select a bid'
            },
            404: {
                'description': 'Job not found or Bid not found for this job'
            }
        }
    })
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
    
@app.route('/api/messages', methods=['POST'])
@jwt_required()
@swag_from({
    'responses': {
        201: {
            'description': 'Message created successfully',
            'schema': {'type': 'object'}
        },
        400: {
            'description': 'User ID and message text are required'
        },
        404: {
            'description': 'Recipient not found or Sender not found'
        }
    }
})
def create_message():
    data = request.get_json()

    recipient_id = data.get('user_id')
    message_text = data.get('message')

    if not recipient_id or not message_text:
        return jsonify({"error": "User ID and message text are required"}), 400

    # Get the recipient user
    recipient = User.query.get(recipient_id)
    if not recipient:
        return jsonify({"error": "Recipient not found"}), 404

    # Get the logged-in user
    sender_id = get_jwt_identity()
    sender = User.query.get(sender_id)
    if not sender:
        return jsonify({"error": "Sender not found"}), 404

    # Create the message
    new_message = Message(
        sender_id=sender.id,
        recipient_id=recipient.id,
        message=message_text,
        time=datetime.now(timezone.utc())
    )

    db.session.add(new_message)
    db.session.commit()

    return jsonify(new_message.to_dict()), 201

@app.route('/api/messages', methods=['GET'])
@jwt_required()
@swag_from({
    'responses': {
        200: {
            'description': 'List of messages',
            'schema': {
                'type': 'array',
                'items': {'type': 'object'}
            }
        },
        404: {
            'description': 'User not found'
        }
    }
})
def get_messages():
    user_id = get_jwt_identity()

    # Get the logged-in user
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Get messages where the user is either the sender or recipient
    sent_messages = Message.query.filter_by(sender_id=user.id).order_by(Message.time.desc()).all()
    received_messages = Message.query.filter_by(recipient_id=user.id).order_by(Message.time.desc()).all()
    all_messages = sent_messages + received_messages

    return jsonify([message.to_dict() for message in all_messages]), 200

# Add resources to API
api.add_resource(Users, '/users')
api.add_resource(BidResource, '/api/bids', '/api/bids/<int:job_id>', '/api/bids/<int:job_id>/<float:amount>')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
