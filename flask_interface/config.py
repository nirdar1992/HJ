# general configs

SECRET_KEY = "HJ"
FLASK_FOLDER = "..\\"
USERS = {"username": "password"}

# gunicorn configs
bind = "0.0.0.0:8000"
workers = 8
threads = 5
