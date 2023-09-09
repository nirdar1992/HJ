import os
from flask import flash, make_response, send_file, redirect, url_for
from app_main.helper_functions import open_json_file, write_to_json_file
from flask_interface.app import app
from flask_interface.app.utilities.logger import handle_log_and_error


@app.template_filter("format_int_with_commas")
def format_int_with_commas(value: int) -> str:
    """
    format an integer with commas for more convenient display
    :param value: integer
    :return: string of the integer - formatted with commas
    """
    return f"{value:,}"


def convert_path(windows_path: str) -> str:
    """
    converts given path to linux path
    :param windows_path: string of somefile path
    :return: linux format path
    """
    linux_path = windows_path.replace("\\", "/")
    linux_path = linux_path.replace("//", "")
    if "V:/" in linux_path:
        linux_path = linux_path.replace("V:/", "/projects/vbu_projects/")
    if "giant_nas/CDNN" in linux_path:
        linux_path = linux_path.replace("giant_nas/", "/projects/")
    elif "giant_nas" in linux_path:
        linux_path = linux_path.replace("giant_nas", "")
    if linux_path[0] != "/":
        linux_path = "/" + linux_path
    handle_log_and_error("info", "function executed successfully")
    return linux_path


# prompts messages - should be replaced with a better solution
def show_message(message: str) -> None:
    """
    sends the message to current html file
    """
    handle_log_and_error("info", f"user got the following message: {message}")
    flash(message, "info")


def make_drills_list(families_path: str = "../data/families.json") -> dict:
    """
    strips onnx and tensor flow file names (if exist)
    :param families_path: path to families file
    :return: dict of family names and their drills
    """
    try:
        families = open_json_file(families_path)
        drills = dict()
        for fam in families.keys():
            drills[fam] = list(families[fam].keys())
        handle_log_and_error("info", "function executed successfully")
    except Exception as error_message:
        handle_log_and_error("error", f"ERROR: {error_message}")
    return drills


def write_and_send_file(file_path: str, data: list or dict, redirect_to: str) -> None:
    """
    :param file_path: file's path to write and download
    :param data: data to write
    :param redirect_to: page to redirect in an error situation
    :return: None, starts file downloading
    """
    try:
        write_to_json_file(file_path, data)
        handle_log_and_error("info", "wrote to json file")
        response = make_response(send_file(file_path, as_attachment=True))
        response.headers[
            "Content-Disposition"
        ] = f"attachment; filename={os.path.basename(file_path)}"
        handle_log_and_error("info", "sent json file")
        return response
    except Exception as error_message:
        if os.path.exists(file_path):
            os.remove(file_path)
        show_message("Could not send file")
        handle_log_and_error(
            "error",
            f"catched an ERROR: {error_message} while trying to write and send the file",
        )
        return redirect(url_for(redirect_to))
