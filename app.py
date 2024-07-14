from flask import Flask, make_response, request
from flask_migrate import Migrate
from flask_restful import Api, Resource
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
import re

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["JWT_SECRET_KEY"] = "super-secret"

# Initialize Extensions
metadata = MetaData()
db = SQLAlchemy(app, metadata=metadata)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
api = Api(app)

# Models
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80))
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(129))
    created_at = db.Column(db.DateTime, default=db.func.now())

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
            "created_at": self.created_at
        }

# Resources
class Users(Resource):
    @jwt_required()
    def get(self):
        current_user = get_jwt_identity()
        users = User.query.all()
        users_list = [user.to_dict() for user in users]

        body = {
            "count": len(users_list),
            "users": users_list
        }

        return make_response(body, 200)

    def post(self):
        email = User.query.filter_by(email=request.json.get('email')).first()
        if email:
            return make_response({"message": "Email already taken"}, 422)

        new_user = User(
            username=request.json.get("username"),
            email=request.json.get("email"),
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

class Login(Resource):
    def post(self):
        email = request.json.get("email")
        password = request.json.get("password")

        user = User.query.filter_by(email=email).first()

        if not user or not bcrypt.check_password_hash(user.password, password):
            return make_response({"message": "Invalid email or password"}, 401)

        access_token = create_access_token(identity=user.id)
        response = {
            "user": user.to_dict(),
            "access_token": access_token
        }

        return make_response(response, 200)

# Add resources
api.add_resource(Users, '/users')
api.add_resource(Login, '/login')

# Main entry
if __name__ == '__main__':
    app.run(debug=True)