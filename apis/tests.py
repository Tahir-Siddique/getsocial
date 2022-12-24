import pytest
import requests
import jwt

# Constants for the test
EMAIL = 'admin1@gmail.com'
PASSWORD = 'admin'


def test_signup():
    # Send a request to the signup endpoint
    response = requests.post('http://127.0.0.1:8000/api/user/signup', json={
        'email': EMAIL,
        'password': PASSWORD
    })

    # Assert that the response status code is 201 (Created)
    assert response.status_code == 201

    # Assert that the response body contains the user's JWT token
    token = response.json()['access']
    assert token is not None


def test_login():
    # Send a request to the login endpoint
    response = requests.post('http://127.0.0.1:8000/api/user/login', json={
        'email': EMAIL,
        'password': PASSWORD
    })

    # Assert that the response status code is 200 (OK)
    assert response.status_code == 200

    # Assert that the response body contains the user's JWT token
    token = response.json()['access']
    assert token is not None


def test_get_user_data():
    # Log in to get a JWT token
    login_response = requests.post('http://127.0.0.1:8000/api/user/login', json={
        'email': EMAIL,
        'password': PASSWORD
    })
    token = login_response.json()["access"]

    # Send a request to the get user data endpoint
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(
        'http://127.0.0.1:8000/api/user/get_user', headers=headers)

    # Assert that the response status code is 200 (OK)
    assert response.status_code == 200

    # Assert that the response body contains the user's data
    data = response.json()
    assert data['email'] == EMAIL
    assert 'ip_address' in data
    assert 'holiday' in data


def test_like_unlike():
    # Log in to get a JWT token
    login_response = requests.post('http://127.0.0.1:8000/api/user/login', json={
        'email': EMAIL,
        'password': PASSWORD
    })
    token = login_response.json()["access"]
    headers = {'Authorization': f'Bearer {token}'}

    # Create a new post
    post_response = requests.post('http://127.0.0.1:8000/api/posts/', json={
        'text': 'Post to like.'
    }, headers=headers)
    assert post_response.status_code == 201
    post_id = post_response.json()['id']

    # Like the post
    like_response = requests.put(
        f'http://127.0.0.1:8000/api/posts/{post_id}/like/', headers=headers)
    assert like_response.status_code == 200
    like_data = like_response.json()
    assert len(like_data['likes']) == 1

    # Unlike the post
    unlike_response = requests.put(
        f'http://127.0.0.1:8000/api/posts/{post_id}/unlike/', headers=headers)
    assert unlike_response.status_code == 200
    unlike_data = unlike_response.json()
    assert len(unlike_data['likes']) == 0


def test_post_crud():
    # Log in to get a JWT token
    login_response = requests.post('http://127.0.0.1:8000/api/user/login', json={
        'email': EMAIL,
        'password': PASSWORD
    })
    token = login_response.json()["access"]
    headers = {'Authorization': f'Bearer {token}'}

    # Get user detail with a JWT token
    login_response = requests.get(
        'http://127.0.0.1:8000/api/user/get_user', headers=headers)
    user_details = login_response.json()

    # Create a new post
    post_response = requests.post('http://127.0.0.1:8000/api/posts/', json={
        'text': 'Test post'
    }, headers=headers)
    assert post_response.status_code == 201
    post_id = post_response.json()['id']

    # Get the list of posts
    posts_response = requests.get(
        'http://127.0.0.1:8000/api/posts/', headers=headers)
    assert posts_response.status_code == 200
    assert post_id in [post['id'] for post in posts_response.json()]

    # Get the details of post_id
    post_response = requests.get(
        f'http://127.0.0.1:8000/api/posts/{str(post_id)}/', headers=headers)
    assert post_response.status_code == 200
    post_data = post_response.json()
    assert post_data['text'] == 'Test post'

    # Update the post of post_id
    post_response = requests.put(
        f'http://127.0.0.1:8000/api/posts/{str(post_id)}/', data={"text": "hello"}, headers=headers)
    assert post_response.status_code == 200
    post_data = post_response.json()
    assert post_data['text'] == 'hello'

    # Delete the post of post_id
    post_response = requests.delete(
        f'http://127.0.0.1:8000/api/posts/{str(post_id)}/', headers=headers)
    assert post_response.status_code == 200
