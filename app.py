from flask import Flask, make_response, request
from flask_migrate import Migrate
from flask_restful import Api, Resource
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy import MetaData

# Import the User model and Resources module
from models import User  # Make sure this import path is correct
import Resources

#Added for jobposting
from config import Config
from models import db
from routes import init_routes
######


# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["JWT_SECRET_KEY"] = "super-secret"

migrate = Migrate(app, db)
db.init_app(app)

# Initialize Extensions
metadata = MetaData()
db = SQLAlchemy(app, metadata=metadata)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
api = Api(app)

# Login resource
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

@app.route('/api/jobs', methods=['GET'])
def get_jobs():
    jobs = Job.query.all()
    return jsonify([job.to_dict() for job in jobs])

@app.route('/api/jobs/<int:job_id>', methods=['GET'])
def get_job(job_id):
    job = Job.query.get(job_id)
    if job is None:
        return jsonify({"error": "Job not found"}), 404
    return jsonify(job.to_dict())

# Add resources
api.add_resource(Resources.Users, '/users')
api.add_resource(Login, '/login')

if __name__ == '__main__':
    app.run(port=5555, debug=True)

 ###   