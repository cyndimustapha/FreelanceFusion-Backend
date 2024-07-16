from flask_restful import Resource
from flask import request, make_response
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from models import db, User  # Ensure this import path is correct
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

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
