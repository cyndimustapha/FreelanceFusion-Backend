class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///FreelanceFusion.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = 'super-secret'
    JWT_ACCESS_TOKEN_EXPIRES = 86400