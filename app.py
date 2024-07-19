from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
from flasgger import Swagger, swag_from
from config import Config
from models import User, db  # Import your existing User model and db

# Initialize Flask app
app = Flask(__name__)
swagger = Swagger(app)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:5173"}}, supports_credentials=True)

# Configure the app
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

@app.before_request
def log_request_info():
    app.logger.debug('Headers: %s', request.headers)
    app.logger.debug('Body: %s', request.get_data())

# User Resource for handling user operations
@app.route('/api/users', methods=['POST'])
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
def create_user():
    try:
        data = request.get_json()
        email = data.get('email')
        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            return make_response({"message": "Email already taken"}, 422)

        new_user = User(
            username=data.get("username"),
            email=email,
            role=data.get("role"),
            password=bcrypt.generate_password_hash(data.get("password")).decode('utf-8')
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
        app.logger.error(f"Error creating user: {e}")
        return make_response({"message": str(e)}, 500)

@app.route('/api/login', methods=['POST'])
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
def login():
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
        app.logger.error(f"Error during login: {e}")
        return make_response({"message": str(e)}, 500)

if __name__ == '__main__':
    app.run(debug=True)
