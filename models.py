from . import db

class Bid(db.Model):
    id = db.column(db.Integer, primary_key=True)
    amount = db.column(db.Float, nullable = False)
    job_id = db.column(db.Integer, db.foreign_key('job.id'), nullable=False)
    freelancer_id = db.column(db.Integer, db.foreign_key('user.id'), nullable=False)

    job = db.relationship('job', back_populates='bids')