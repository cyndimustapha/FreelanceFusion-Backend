from flask_restful import Resource, reqparse
from sqlalchemy import and_, not_
from flask_jwt_extended import jwt_required, get_jwt
from models import db, Bid  

class BidResource(Resource):
    
    @jwt_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('amount', type=float, required=True, help='Amount must be provided')
        parser.add_argument('job_id', type=int, required=True, help='Job ID must be provided')
        args = parser.parse_args()

        current_user = get_jwt().identity
        if not current_user:
            return {'message': 'User not authenticated'}, 401

        bid = Bid(
            amount=args['amount'],
            job_id=args['job_id'],
            freelancer_id=current_user.id
        )

        db.session.add(bid)
        db.session.commit()

        return {'message': 'Bid placed successfully', 'bid_id': bid.id}, 201
