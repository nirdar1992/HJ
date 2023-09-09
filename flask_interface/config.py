# postgres configs

SECRET_KEY = "HJ"
FLASK_FOLDER = "..\\"
USERS = {"nird": "3012"}

# gunicorn configs
bind = "0.0.0.0:8000"
workers = 8
threads = 5
