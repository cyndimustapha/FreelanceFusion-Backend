from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Bid, Job

class BidResource(Resource):
    
    @jwt_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('amount', type=float, required=True, help='Amount must be provided')
        parser.add_argument('job_id', type=int, required=True, help='Job ID must be provided')
        args = parser.parse_args()

        current_user_id = get_jwt_identity()
        if not current_user_id:
            return {'message': 'User not authenticated'}, 401

        job = Job.query.get(args['job_id'])
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

    @jwt_required
    def get(self, job_id):
        current_user_id = get_jwt_identity()
        if not current_user_id:
            return {'message': 'User not authenticated'}, 401

        job = Job.query.get(job_id)
        if not job:
            return {'message': 'Job not found'}, 404

        bids = Bid.query.filter_by(job_id=job_id).all()
        serialized_bids = [{'id': bid.id, 'amount': bid.amount, 'freelancer_id': bid.freelancer_id} for bid in bids]

        return {'bids': serialized_bids}, 200
