import json
import re


def open_json_file(path):
    """
    :param path: path to json file
    :return: file's data as dictionary
    """
    with open(path) as js_file:
        jf = json.load(js_file)
    return jf


def write_to_json_file(json_file, data_dict):
    """
    :param json_file: path to json file
    :param data_dict: dict to write to the json file
    :return: writes data to json file, void func
    """
    out_file = open(json_file, "w")
    json.dump(data_dict, out_file, indent="")
    out_file.close()
    return


def find_parameter(parameter, drill_dict):
    if parameter not in drill_dict["parameters"]:
        raise ValueError(
            parameter, "wasn't found in the drill's dict, please check your spelling."
        )


def extract_family_name(drill_name):
    """
    :param drill_name: drill's name as a string
    :return: family name
    """
    if drill_name[0] == " ":
        drill_name = drill_name[1:]
    try:
        first_word = drill_name[: drill_name.index(" ")].lower()
    except:
        first_word = drill_name.lower()
    if "ball" in first_word:
        return "possession"
    elif "large" in first_word:
        return "lsg"
    elif "vs" in first_word and "+" in first_word:
        return "joker games"
    elif "warm" in first_word or "intervals" in first_word:
        return "fitness"
    elif "sided" in first_word:
        return "sided games"
    else:
        return first_word.lower().strip(",").replace(":", "")


def remove_set_num_from_drill_name(drill):
    """
    cleans csv add-ons to the column's name
    :param drill: drill's name
    :return: drill's name without the number of set
    """
    if "half" in drill:
        return drill
    # find the '.' before the number of the occurrence and return the original name
    substrings = drill.split(",")
    result = drill.lstrip().rstrip()
    if "set" in substrings[-1].lower():
        result = substrings[0]
        substrings.pop(-1)
        for sub in substrings:
            if sub == result:
                continue
            result = result + "," + sub
    result = result.lower()

    if "set" in result:
        result = result[: result.index(" set")]
    result = re.sub(r"(\s*\d+th$)", "", result)
    result = re.sub(r"(\s*\d+nd$)", "", result)
    result = re.sub(r"(\s*\d+st$)", "", result)
    result = re.sub(r"(\s*\d+rd$)", "", result)
    result = re.sub(r"(\s*\d+th$)", "", result)
    result = re.sub(r"(\s*\d+nd$)", "", result)
    result = re.sub(r"(\s*\d$)", "", result)
    return result
