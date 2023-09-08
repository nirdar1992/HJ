# postgres configs

SECRET_KEY = "HJ"
FLASK_FOLDER = r"C:\Users\nird\PycharmProjects\HJ"
DATABASE_NAME = "ModelZoo"
DATABASE_USER = "postgres"
DATABASE_HOST = "localhost"
DATABASE_PASSWORD = "Welcome4$"
USERS = {"nird": "3012"}

# gunicorn configs
bind = "0.0.0.0:8000"
workers = 8
threads = 5
