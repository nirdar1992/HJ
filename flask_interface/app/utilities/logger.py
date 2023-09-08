import logging
import inspect
import os
from datetime import datetime
from flask_login import current_user, AnonymousUserMixin


CURRENT_TIME = str(datetime.now().strftime("%d%m%Y"))

def handle_log_and_error(log_type: str, message: str) -> None:
    """
    Handling all types of logging events by log_type, raising error if occurred.
    :param log_type: string defining the log type: info, debug, warning, error, exception.
    :param message: log message that will be printed to the logging file
    :return: None
    """
    try:
        frame = inspect.stack()[1]
        function_name = frame.function
        line_number = frame.lineno
        filename = os.path.basename(frame.filename)
        if 'login.py' == filename or current_user == None or isinstance(current_user, AnonymousUserMixin):
            username = "SYSTEM"
        else:
            username = current_user.id
    except (IndexError, ValueError):
        function_name = "unknown"
        line_number = -1
        filename = "unknown"
        username = "unknown"
    extra_dict = {
        "func_name": function_name,
        "line_number": line_number,
        "file_name": filename,
        "user_name": username,
    }
    if log_type == "info":
        logging.info(
            message,
            extra=extra_dict,
        )
    elif log_type == "debug":
        logging.debug(
            message,
            extra=extra_dict,
        )
    elif log_type == "warning":
        logging.warning(
            message,
            extra=extra_dict,
        )
    elif log_type == "error":
        logging.error(
            message,
            extra=extra_dict,
            exc_info=True,
        )
    elif log_type == "exception":
        logging.exception(
            message,
            extra=extra_dict,
            exc_info=True,
        )


def init_logging() -> None:
    """ּ
    Initializing logger file by date & time naming.ּּ
    """
    class PWFormatter(logging.Formatter):
        """
        Overriding the logging format.
        """
        def format(self, record):
            extra_dict = {}
            fmt = (
                "%(asctime)s | %(levelname)s | %(filename)s | Line:%(lineno)d | "
                "Function: %(funcName)s | Message: %(message)s"
            )
            if hasattr(record, "file_name"):
                record.__dict__.update(record.__dict__.get("extra", extra_dict))
                fmt = (
                    "%(asctime)s | %(levelname)s | %(user_name)s | %(file_name)s | Line:%(line_number)d | "
                    "Function: %(func_name)s | Message: %(message)s"
                )
            setattr(self._style, "_fmt", fmt)
            self.datefmt = "%Y-%m-%d %H:%M:%S"
            return super().format(record)

    log = logging.getLogger()
    for handler in log.handlers:
        if isinstance(handler, logging.StreamHandler):
            log.removeHandler(handler)
    log.setLevel(logging.DEBUG)
    logger_file_name = r'C:\Users\nird\PycharmProjects\HJ\flask_interface\logs\HJ_log_{CURRENT_TIME}.txt'
    file_handler = logging.FileHandler(filename=logger_file_name)
    file_handler.setFormatter(PWFormatter())
    log.addHandler(file_handler)
    handle_log_and_error("info", "app_main and logger initialized successfully")


def finalize_logging(log_handler: logging.Logger) -> None:
    """
    Finalizing the logger and closing its handler.
    :param log_handler : the looger to finalize
    """
    handle_log_and_error("info", "finish logging")
    logging.getLogger().removeHandler(log_handler)
