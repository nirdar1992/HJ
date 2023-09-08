# initialize HJ web-app_main

import os
from flask import Flask

TEMPLATE_DIR = "C:\\Users\\nird\PycharmProjects\\HJ\\flask_interface\\templates\\"
STATIC_DIR = "C:\\Users\\nird\PycharmProjects\\HJ\\flask_interface\\static\\"

app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)

app.config.from_pyfile("../config.py")

from flask_interface.app import routes
from flask_interface.app.utilities.logger import init_logging, handle_log_and_error

init_logging()
files_to_delete = os.listdir(app.config["FLASK_FOLDER"])
files_counter = 0
for file in files_to_delete:
    if file.endswith(".json"):
        os.remove(os.path.join(app.config["FLASK_FOLDER"], file))
        files_counter += 1
handle_log_and_error("info", f"deleted {files_counter} from home folder")
