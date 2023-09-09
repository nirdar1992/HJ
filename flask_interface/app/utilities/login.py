from flask import Request
from flask_login import UserMixin, LoginManager, login_user
from flask_interface.app import app
from flask_interface.app.utilities.logger import handle_log_and_error


# login initialization
login_manager = LoginManager(app)
handle_log_and_error("info", "LoginManager instantiated")


class User(UserMixin):
    """
    user class, in order to handle flask login method
    """

    def __init__(self, user_id):
        self.id = user_id
        handle_log_and_error("info", "User instantiated")


@login_manager.user_loader
def load_user(user_id: str) -> User:
    """
    simple function, in use in the flask login method
    """
    handle_log_and_error("info", "function executed successfully")
    return User(user_id)


def validate_login(request: Request) -> bool:
    """
    validates entered username and password
    :param request: user's input
    :return: True if loged in, otherwise - False
    """
    try:
        # get user's input
        username = request.form["username"]
        password_enterd = request.form["password"]
        handle_log_and_error("info", "got user's input")
        # get user's password from database
        database_password = app.config["USERS"].get(username, 0)
        handle_log_and_error("info", f"{database_password} returned from query")
        # check if password matches and login
        if database_password == password_enterd:
            login_user(User(username))
            handle_log_and_error("info", f"{username} has logged-in successfully")
            return True
        # password is incorrect
        handle_log_and_error(
            "info", f"{username} has enterd wrong password: {password_enterd}"
        )
        return False
    except Exception:
        # username is incorrect
        handle_log_and_error("info", f"{username} is not registered")
        return False
