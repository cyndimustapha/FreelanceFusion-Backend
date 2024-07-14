from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from models import db
from routes import init_routes
from flask_cors import CORS

app = Flask(__name__)
app.config.from_object(Config)

CORS(app, resources={r"/job/*": {"origins": "http://localhost:5174"}})

db.init_app(app)
migrate = Migrate(app, db)

with app.app_context():
    db.create_all()

init_routes(app)

if __name__ == '__main__':
    app.run(debug=True)
