import os
from datetime import timedelta
from flask import Flask
from flask_migrate import Migrate
from flask_restful import Resource, Api
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from config import Config
from models import db
from resources.bid import BidResource
from routes import init_routes

app = Flask(__name__)
api = Api(app)

app.config.from_object(Config)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///test.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'super-secret-key')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

CORS(app, resources={r"/job/*": {"origins": "http://localhost:5174"}})
migrate = Migrate(app, db)
db.init_app(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

api.add_resource(BidResource, '/bids', '/bids/<int:job_id>')

with app.app_context():
    db.create_all()

init_routes(app)

if __name__ == '__main__':
    app.run(debug=True)
