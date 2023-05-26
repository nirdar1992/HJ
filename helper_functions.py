import json


def find_parameter(parameter, drill_dict):
    if parameter not in drill_dict["parameters"]:
        raise ValueError(parameter, "wasn't found in the drill's dict, please check your spelling.")


def extract_family_name(drill_name):
    '''
    :param drill_name: drill's name as a string
    :return: family name

    will be replaced by "map_drill_fam" function after orin's family grouping
    '''
    try:
        first_word = drill_name[:drill_name.index(" ")]
    except:
        first_word = drill_name
    if first_word == "ATTACKING" or first_word == "OFFENCE" or drill_name.startswith("SET PIECES"):
        return "OFFENCE"
    elif "VS" in first_word:
        return "INNER GAMES"
    else:
        return first_word


def map_drill_fam(drill):
    '''
    finds drill's family group
    :param drill: drill's name
    :return: drill's family name
    '''
    # load families json file
    families_file = "data/families.json"
    with open(families_file) as js_file:
        families = json.load(js_file)
    # iterate over each family until found
    for fam in families:
        if drill in families[fam]:
            return fam
    # if not found - raise an Error
    raise ValueError(drill + " was not found in the families dict, please check you've spelled it right.")


def remove_num_of_parameter_from_drill_name(drill):
    '''
    cleans csv add-ons to the column's name
    :param drill: drill's name
    :return: drill's name without the number of occurrence
    '''
    # find the '.' before the number of the occurrence and return the original name
    dot_index = drill.index('.')
    return drill[:dot_index]
