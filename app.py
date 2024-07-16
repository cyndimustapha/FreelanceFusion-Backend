from flask import Flask, make_response, request, jsonify
from flask_migrate import Migrate
from flask_restful import Api, Resource
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy import MetaData
from models import User, Bid, db
from config import Config
from routes import init_routes
from resources.bid import BidResource

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

# Initialize routes
init_routes(app)

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

api.add_resource(Users, '/users')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
