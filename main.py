import sys
import traceback
import argparse
import time
import os
import subprocess
from app_main.helper_functions import open_json_file, write_to_json_file


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Available arguments are:\n", add_help=True
    )
    parser.add_argument(
        "--input_file",
        help="Json input file path. ./data/InputFile.json by default.",
        required=False,
        type=str,
        default="./data/InputFile.json",
    )
    args = parser.parse_args()

    retval = 0
    output = None
    input_params = open_json_file(args.input_file)
    operation = input_params["operation"]

    try:
        completed_process = subprocess.run(
            [
                "python",
                "C:\\Users\\nird\\PycharmProjects\\HJ/tests/test_build_session.py",
            ],
            capture_output=True,
            text=True,
        )
        if completed_process.returncode == 0:
            print("Tests finished successfully!")
        else:
            print("Please run the tests and check last update!")
            exit()
        if operation == "build training session":
            from app_main.build_training_session import build_session
            from app_main.project_classes import SessionBuild

            sb = SessionBuild(input_params["build_session_file"])
            output = build_session(input_params["families_file"], sb)
        elif operation == "replace drill":
            from app_main.build_training_session import find_equal_drill

            output = find_equal_drill(
                input_params["families_file"],
                input_params["drills"],
                input_params["parameter"],
            )
        elif operation == "get training session value":
            from app_main.build_training_session import get_session_val

            output = get_session_val(
                input_params["families_file"],
                input_params["drills"],
                input_params["parameter"],
            )
        elif operation == "update new data":
            from app_main.new_data_update import update_data

            update_data(
                input_params["new_data_file"],
                input_params["families_file"],
                input_params["stats_file"],
            )
        else:
            raise ValueError(operation + " is not a valid operations.")
    except Exception as e:
        print(operation + " failed: " + str(e))
        traceback.print_exc(file=sys.stdout)
        retval = 1
    finally:
        if retval == 0:
            if output is None:
                print(operation + " has finished successfully.")
            else:
                cur_dir = os.getcwd().replace("\\", "/")
                if input_params["output_folder"] == "/data/out":
                    output_file_dir = (
                        f"{cur_dir}/{input_params['output_folder'].strip('/')}"
                    )
                else:
                    output_file_dir = f"{input_params['output_folder'].strip('/')}/"
                if not os.path.exists(output_file_dir):
                    os.makedirs(output_file_dir)
                output_file_dir += f"/{time.strftime('%d_%m_%Y_%H_%M_%S')}.json"
                write_to_json_file(output_file_dir, output)
                print(operation + " finished. Results are ready at " + output_file_dir)
        sys.exit(retval)
