# models.py
from sqlalchemy import MetaData
from sqlalchemy.ext.associationproxy import association_proxy
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_serializer import SerializerMixin
from flask_bcrypt import check_password_hash

convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention = convention)

db = SQLAlchemy(metadata = metadata)

class Bid(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    freelancer_id = db.Column(db.Integer, nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('job_postings.id'), nullable=False)

    def __repr__(self):
        return f"Bid('{self.amount}', '{self.freelancer_id}')"

    def to_dict(self):
        return {
            "id": self.id,
            "amount": self.amount,
            "freelancer_id": self.freelancer_id,
            "job_id": self.job_id
        }