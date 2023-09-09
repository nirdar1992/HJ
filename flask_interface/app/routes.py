import os
from flask_login import login_required, logout_user
from flask import render_template, redirect, url_for, request
from app_main.new_data_update import update_data
from app_main.helper_functions import write_to_json_file
from app_main.build_training_session import (
    find_equal_drill,
    build_session,
    get_session_val,
)
from app_main.project_classes import SessionBuild
from flask_interface.app import app
from flask_interface.app.utilities.login import validate_login
from flask_interface.app.utilities.general import (
    show_message,
    make_drills_list,
    write_and_send_file,
)
from flask_interface.app.utilities.logger import handle_log_and_error


######################################
##      login / logout route        ##
######################################


@app.route("/login", methods=["GET", "POST"])
def login():
    """
    login user to ModelZoo
    """
    if request.method == "POST":
        # validate user's input
        login_retval = validate_login(request)
        # if password or username was incorrect, redirect to login page with an error meesagae, if all good - redirect to home page
        return (
            redirect(url_for("home_page"))
            if login_retval
            else render_template("001.2wrong_login.html")
        )
    return render_template("001.1login.html")


@app.route("/logout")
@login_required
def logout():
    """
    logout user and redirect to login page
    """
    logout_user()
    return redirect(url_for("login"))


######################################
##          home page route         ##
######################################


@app.route("/", methods=["GET", "POST"])
@login_required
def home_page():
    return render_template("002home.html")


@app.route("/update_new_data", methods=["GET", "POST"])
@login_required
def update_database():
    if request.method == "POST":
        """
        update with new data
        """
        if request.method == "POST":
            # get file uploaded by user
            csv_file = request.files.get("csv_file", None)
            handle_log_and_error("info", "got user's input")
            # update database
            if csv_file and csv_file.filename != "":
                retval = update_data(csv_file)
                if retval != 0:
                    show_message(
                        f"Error :{retval} occurred while trying to update data"
                    )
                    handle_log_and_error("error", f"ERROR: {retval}")
                    return render_template("003update_data.html")

            else:
                handle_log_and_error(
                    "info", "user pressed update button with no uploaded file"
                )
                show_message("Error: Please upload file.")
                return render_template("003update_data.html")
            show_message("Data updated successfully")
            return render_template("002home.html")
    return render_template("003update_data.html")


######################################
##        find equal drills         ##
######################################


@app.route("/find_equal_drills", methods=["GET", "POST"])
@login_required
def find_similar():
    if request.method == "POST":
        drill = request.form.get("drill", None)
        parameter = request.form.get("parameter", None)
        sd = "default"
        try:
            sd = request.form.get("deviation", None)
            if sd == "":
                sd = 1
            elif float(sd) <= 0 or float(sd) > 1:
                show_message("Please insert a number in the range of (0, 1]")
                handle_log_and_error(
                    "error", f"user entered {sd}, not in the right range"
                )
                return redirect(url_for("find_similar"))
            handle_log_and_error("info", "got user's input")
        except Exception as error_message:
            show_message("Please insert a number in the range of (0, 1]")
            handle_log_and_error(
                "error",
                f"user entered {sd}, {parameter}, {drill} as inputs: {error_message}",
            )
            return redirect(url_for("find_similar"))
        file_path = os.path.join(
            app.config["FLASK_FOLDER"], f"{drill}_equal_drills.json"
        )
        try:
            data = find_equal_drill(drill, parameter=parameter, sd=float(sd))
        except Exception as error_message:
            show_message("Could not send file")
            handle_log_and_error(
                "error",
                f"catched an ERROR: {error_message} while trying to execute find equal drill function",
            )
            return redirect(url_for("find_similar"))
        return write_and_send_file(file_path, data, "find_similar")

    drills = make_drills_list()
    return render_template("004find_equal_drills.html", drills_data=drills)


######################################
##       get session values         ##
######################################


@app.route("/get_session_val", methods=["GET", "POST"])
@login_required
def get_sess_val():
    if request.method == "POST":
        try:
            parameter = request.form.get("parameter", None)
            user_input = request.form
            drills = []
            for choise in user_input:
                if choise.startswith("category_"):
                    if user_input[choise] == "None":
                        continue
                    drills.append(user_input[choise])

            file_path = os.path.join(app.config["FLASK_FOLDER"], "ger_session_val.json")
            try:
                data = get_session_val(drills, parameter=parameter)
            except Exception as error_message:
                show_message("Could not send file")
                handle_log_and_error(
                    "error",
                    f"catched an ERROR: {error_message} while trying to execute get_session_val function",
                )
                return redirect(url_for("find_similar"))

            handle_log_and_error("info", "got user's input")
            return write_and_send_file(file_path, data, "get_sess_val")
        except Exception as error_message:
            show_message("Could not get user's input")
            handle_log_and_error("error", f"ERROR: {error_message}")
            drills = make_drills_list()
            return render_template("005get_session_val.html", drills_data=drills)

    drills = make_drills_list()
    return render_template("005get_session_val.html", drills_data=drills)


######################################
##          build session           ##
######################################


@app.route("/build_session", methods=["GET", "POST"])
@login_required
def build_training_session():
    drills = make_drills_list()
    if request.method == "POST":
        try:
            output = {}
            configs = dict(request.form)
            if configs["userChoices"] == "":
                show_message("Please select at least one drills family")
                handle_log_and_error(
                    "error", "ERROR: Please select at least one drills family"
                )
                return render_template("006build_session.html", drills_data=drills)

            if configs["min_session_range"] == "":
                configs["min_session_range"] = 0
            if configs["max_session_range"] == "":
                configs["max_session_range"] = 0

            if float(configs["min_session_range"]) > float(
                configs["max_session_range"]
            ):
                show_message("minimum of range can not be bigger than maximum!")
                handle_log_and_error(
                    "error", "ERROR: minimum of range can not be bigger than maximum!"
                )
                return render_template("006build_session.html", drills_data=drills)

            output["session"] = {
                "fams": configs["userChoices"].split(","),
                "parameter": configs["parameter"],
                "min_val": float(configs["min_session_range"]),
                "max_val": float(configs["max_session_range"]),
            }

            constrains = {}
            if configs["con_drill2"] != "None":
                if configs["con_drill2"] not in configs["userChoices"]:
                    show_message(
                        f"{configs['con_drill2']} is not included in session's drills families!"
                    )
                    handle_log_and_error(
                        "error",
                        f"{configs['con_drill2']} is not included in session's drills families!",
                    )
                    return render_template("006build_session.html", drills_data=drills)
                if configs["min_cons_range"] == "":
                    configs["min_cons_range"] = 0
                if configs["max_cons_range"] == "":
                    configs["max_cons_range"] = 0

                if float(configs["min_cons_range"]) > float(configs["max_cons_range"]):
                    show_message("minimum of range can not be bigger than maximum!")
                    handle_log_and_error(
                        "error",
                        "ERROR: minimum of range can not be bigger than maximum!",
                    )
                    return render_template("006build_session.html", drills_data=drills)
                constrains["constrain1"] = {
                    "fams": [configs["con_drill2"]],
                    "parameter": configs["const_parameter2"],
                    "operator": "range",
                    "min_val": float(configs["min_cons_range"]),
                    "max_val": float(configs["max_cons_range"]),
                }

            if configs["con_drill3"] != "None":
                if configs["con_drill3"] not in configs["userChoices"]:
                    show_message(
                        f"{configs['con_drill3']} is not included in session's drills families!"
                    )
                    handle_log_and_error(
                        "error",
                        f"{configs['con_drill3']} is not included in session's drills families!",
                    )
                    return render_template("006build_session.html", drills_data=drills)
                if configs["min_cons_range3"] == "":
                    configs["min_cons_range3"] = 0
                if configs["max_cons_range3"] == "":
                    configs["max_cons_range3"] = 0

                if float(configs["min_cons_range3"]) > float(
                    configs["max_cons_range3"]
                ):
                    show_message("minimum of range can not be bigger than maximum!")
                    handle_log_and_error(
                        "error",
                        "ERROR: minimum of range can not be bigger than maximum!",
                    )
                    return render_template("006build_session.html", drills_data=drills)
                constrains["constrain2"] = {
                    "fams": [configs["con_drill3"]],
                    "parameter": configs["const_parameter3"],
                    "operator": "range",
                    "min_val": float(configs["min_cons_range3"]),
                    "max_val": float(configs["max_cons_range3"]),
                }

            if configs["con_drill4"] != "None":
                if configs["con_drill4"] not in configs["userChoices"]:
                    show_message(
                        f"{configs['con_drill4']} is not included in session's drills families!"
                    )
                    handle_log_and_error(
                        "error",
                        f"{configs['con_drill4']} is not included in session's drills families!",
                    )
                    return render_template("006build_session.html", drills_data=drills)
                if configs["min_cons_range4"] == "":
                    configs["min_cons_range4"] = 0
                if configs["max_cons_range4"] == "":
                    configs["max_cons_range4"] = 0

                if float(configs["min_cons_range4"]) > float(
                    configs["max_cons_range4"]
                ):
                    show_message("minimum of range can not be bigger than maximum!")
                    handle_log_and_error(
                        "error",
                        "ERROR: minimum of range can not be bigger than maximum!",
                    )
                    return render_template(
                        "005get_session_val.html", drills_data=drills
                    )
                constrains["constrain3"] = {
                    "fams": [configs["con_drill4"]],
                    "parameter": configs["const_parameter4"],
                    "operator": "range",
                    "min_val": float(configs["min_cons_range4"]),
                    "max_val": float(configs["max_cons_range4"]),
                }
            output["constrains"] = constrains
            write_to_json_file("../data/BuildSession.json", output)
            sb = SessionBuild()
            data = build_session(sb)
            file_path = os.path.join(app.config["FLASK_FOLDER"], "build_session.json")
            return write_and_send_file(file_path, data, "home_page")
        except Exception as error_message:
            show_message(error_message)
            handle_log_and_error("error", f"ERROR: {error_message}")
            return render_template("006build_session.html", drills_data=drills)
    drills = make_drills_list()
    return render_template("006build_session.html", drills_data=drills)
