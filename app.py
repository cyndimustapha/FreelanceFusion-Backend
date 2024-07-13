from flask import Flask, make_response, request
from flask_migrate import Migrate
from flask_restful import Api, Resource
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

from models import db, User

# Initialize the flask application
app = Flask(__name__)

# Configure the database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["JWT_SECRET_KEY"] = "super-secret"



migrate = Migrate(app, db)

bcrypt = Bcrypt(app)

jwt = JWTManager(app)

db.init_app(app)

api = Api(app)

class Users(Resource):
    @jwt_required()
    def get(self):
        current_user = get_jwt_identity()
        print(current_user)
        users = User.query.all()
        users_list = []

        for user in users:
            users_list.append(user.to_dict())

        body = {
            "count": len(users_list),
            "users": users_list
        }

        return make_response(body, 200)

    def post(self):
       
        email = User.query.filter_by(email=request.json.get('email')).first();

        if email:
            return make_response({ "message": "Email already taken" }, 422)

        new_user = User(
            username=request.json.get("username"),
            email=request.json.get("email"),
            password=bcrypt.generate_password_hash(request.json.get("password"))
        )

        db.session.add(new_user)
        db.session.commit()

        access_token = create_access_token(identity=new_user.id)

        response = {
            "user": new_user.to_dict(),
            "access_token": access_token
        }

        response = make_response(response, 201)

        return response


api.add_resource(Users, '/users')