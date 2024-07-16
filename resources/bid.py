from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Bid, JobPosting

class BidResource(Resource):
    
    @jwt_required()
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('amount', type=float, required=True, help='Amount must be provided')
        parser.add_argument('job_id', type=int, required=True, help='Job ID must be provided')
        args = parser.parse_args()

        current_user_id = get_jwt_identity()
        if not current_user_id:
            return {'message': 'User not authenticated'}, 401

        job = JobPosting.query.get(args['job_id'])
        if not job:
            return {'message': 'Job not found'}, 404

        bid = Bid(
            amount=args['amount'],
            job_id=args['job_id'],
            freelancer_id=current_user_id
        )

        db.session.add(bid)
        db.session.commit()

        return {'message': 'Bid placed successfully', 'bid_id': bid.id}, 201

    @jwt_required()
    def get(self, job_id):
        current_user_id = get_jwt_identity()
        if not current_user_id:
            return {'message': 'User not authenticated'}, 401

        job = JobPosting.query.get(job_id)
        if not job:
            return {'message': 'Job not found'}, 404

        bids = Bid.query.filter_by(job_id=job_id).all()
        serialized_bids = [{'id': bid.id, 'amount': bid.amount, 'freelancer_id': bid.freelancer_id} for bid in bids]

        return {'bids': serialized_bids}, 200

    @jwt_required()
    def put(self, job_id):
        parser = reqparse.RequestParser()
        parser.add_argument('bid_id', type=int, required=True, help='Bid ID must be provided')
        args = parser.parse_args()

        current_user_id = get_jwt_identity()
        if not current_user_id:
            return {'message': 'User not authenticated'}, 401

        job = JobPosting.query.get(job_id)
        if not job:
            return {'message': 'Job not found'}, 404

        if job.client_id != current_user_id:
            return {'message': 'Only the client who posted the job can select a bid'}, 403

        bid = Bid.query.get(args['bid_id'])
        if not bid or bid.job_id != job_id:
            return {'message': 'Bid not found for this job'}, 404

        # Mark all bids for this job as not selected
        Bid.query.filter_by(job_id=job_id).update({'selected': False})

        # Mark the chosen bid as selected
        bid.selected = True
        db.session.commit()

        return {'message': 'Bid selected successfully'}, 200
