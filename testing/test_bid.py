import json
from flask_jwt_extended import create_access_token
from models import User, JobPosting, Bid

def test_place_bid(test_client, init_database):
    # Login and get access token
    user = User.query.filter_by(email='test@example.com').first()
    access_token = create_access_token(identity=user.id)
    
    # Place a bid
    response = test_client.post(
        '/bids',
        headers={'Authorization': f'Bearer {access_token}'},
        data=json.dumps({'amount': 200, 'job_id': 1}),
        content_type='application/json'
    )
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert 'bid_id' in data

def test_get_bids(test_client, init_database):
    # Login and get access token
    user = User.query.filter_by(email='test@example.com').first()
    access_token = create_access_token(identity=user.id)
    
    # Get bids for a job
    response = test_client.get(
        '/bids/1',
        headers={'Authorization': f'Bearer {access_token}'}
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'bids' in data
    assert len(data['bids']) > 0
    assert data['bids'][0]['amount'] == 200
    assert data['bids'][0]['job_id'] == 1
    assert data['bids'][0]['freelancer_id'] == user.id

def test_select_bid(test_client, init_database):
    # Login as client and get access token
    client = User.query.filter_by(email='client@example.com').first()
    access_token = create_access_token(identity=client.id)

    # Select a bid
    response = test_client.put(
        '/bids/1',
        headers={'Authorization': f'Bearer {access_token}'},
        data=json.dumps({'bid_id': 1}),
        content_type='application/json'
    )

    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['message'] == 'Bid selected successfully'

    # Verify the selected bid
    selected_bid = Bid.query.filter_by(id=1).first()
    assert selected_bid.selected is True
    non_selected_bids = Bid.query.filter(Bid.id != 1, Bid.job_id == 1).all()
    for bid in non_selected_bids:
        assert bid.selected is False
