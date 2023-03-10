# Django Social Network (GetSocial) API

This is a simple REST API-based social network built with Django and the Django Rest Framework (DRF). It allows users to sign up, login, create text posts, and view, like, and unlike other users' posts.

## Features

- User signup with email validation and IP-based geolocation data enrichment using AbstractAPI
- User login with JWT authentication
- CRUD actions for posts
- Like and unlike posts

## Requirements

- Python 3.6 or higher
- Django 3.1 or higher
- Django Rest Framework 3.11 or higher
- Celery 4.4 or higher (optional, for asynchronous data enrichment)
- Redis (Use as Message Broker)

## Setup

1. Clone the repository and navigate to the project directory:

```bash
git clone https://github.com/Tahir-Siddique/getsocial.git
cd getsocial
```
2. Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```
3. Install the required packages:
```bash
pip install -r requirements.txt
```
4. Set up the database:
```bash
python manage.py makemigrations
python manage.py migrate
```
5. (Optional) If you want to use Celery for asynchronous data enrichment, you will need to set up a message broker. I recommend using Redis. Follow the Celery documentation for instructions on how to set up Redis and configure Celery to use it.

## Running the API

To start the API locally, run the following command:
```bash
python manage.py runserver
```
- Need of a server (redis)
- I'm using MacOS so the command for me will be
```bash
brew install redis
redis-server
redis-cli
```
You can ping and check if redis is running by these commands:
```bash
redis-cli
127.0.0.1:6379> ping
PONG
```
If the response say `PONG` that means the server is running.
Also make sure to place the address of the redis server in the file
`getsocial/settings.py`
In my case its `127.0.0.1:6379` so i will place like this
```python
CELERY_BROKER_URL = "redis://127.0.0.1:6379"
CELERY_RESULT_BACKEND = "redis://127.0.0.1:6379"
```
To start the Celery worker and beat processes for asynchronous tasks, run the following commands in separate terminal:
```bash
celery -A getsocial worker -l info
celery -A getsocial beat -l info
```
## Postman Collection
The postman collection is available at `postman/GetSocial.postman_collection.json` that you can use to test apis by importing collection in Postman


## Testing
To run the pytests, use the following command:

```bash 
pytest apis/tests.py
```
