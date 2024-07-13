import requests

url = 'http://localhost:5000/users'
headers = {'Content-Type': 'application/json'}
data = {
    'first_name': 'John',
    'last_name': 'Doe',
    'email': 'john.doe@example.com',
    'password': 'securepassword'
}

try:
    response = requests.post(url, json=data, headers=headers)
    print(f'Status Code: {response.status_code}')
    print(f'Response JSON: {response.json()}')
except requests.exceptions.RequestException as e:
    print(f'Error: {e}')
