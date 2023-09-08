import pprint
from app_main.helper_functions import *
from app_main.project_classes import SessionBuild
from scipy.stats import norm

# define the precent we would consider to exceed from our distance target value
SD_MEAN = 0.2


def rec_sum(families, drills, val, fam_name, parameter, sd, sub_drills=[]):
    '''
    helper recursive function which finds a drill/s or drills combinations that sums up to a specific drill
    :param drills: list of family related drills names
    :param val: the target value we want to reach
    :param fam_name: drill's family name
    :param parameter: parameter's name to search by
    :param sd: val param * SD_MEAN global definition
    :param sub_drills: list of sub drills that were already found
    :return: list of lists of drills combinations that could replace the target drill
    '''
    # if the sub drills are in the right value range - return it
    if sd >= val >= (sd * (-1)):
        return sub_drills
    # if there is no more drills to check - return an empty list
    elif len(drills) == 0:
        return []
    else:
        # subtract the new drill parameter value from our target value
        find_parameter(parameter, families[fam_name][drills[0]])
        temp_val = val - families[fam_name][drills[0]]["parameters"][parameter]["team's mean"]
        # remove the drill from our family drills because we've just iterated over it
        temp_drills = [drill for drill in drills]
        # get that drill name
        d = temp_drills.pop(0)
        # add it to our sub drills list
        new_sbd = [drill for drill in sub_drills]
        new_sbd.append(d)
        # call the function recursively, once without taking the last drill in consider and once with it
        return rec_sum(families, temp_drills, val, fam_name, parameter, sd, sub_drills),\
               rec_sum(families, temp_drills, temp_val, fam_name, parameter, sd, new_sbd)


def find_equal_drill(drill_name, sd, families_file="../data/families.json", parameter="Total Distance"):
    '''
    function which finds a drill/s or drills combinations that sums up to a specific drill parameter value
    :param families_file: frills families file path
    :param drill_name: drill's name we would like to replace
    :param sd: accuracy range
    :param parameter: parameter's name we search by
    :return: list of lists of drills combinations that could replace the target drill
    '''
    families = open_json_file(families_file)
    # find drill's family name
    fam_name = extract_family_name(drill_name)
    # extract the target value
    find_parameter(parameter, families[fam_name][drill_name])
    mean_to_reach = families[fam_name][drill_name]["parameters"][parameter]["team's mean"]
    # create list of the drills names from the same family and remove the drill we want to replace
    fam_drills = list(families[fam_name].keys())
    fam_drills.remove(drill_name)
    # call the "rec_sum" function and find our drills, print/return it
    result = rec_sum(families, fam_drills, mean_to_reach, fam_name, parameter, mean_to_reach*sd)
    print("len", len(result))
    print("type", type(result))
    for i in result:
        print(i)
        print("\n\n\n\n")
    return result


def get_session_val(drills, families_file="../data/families.json", parameter="Total Distance"):
    '''
    :param families_file: frills families file path
    :param drills: unlimited drills names that represents a training session
    :param parameter: by which parameter to sum the session. Distance param by default.
    :return: dictionary which contains the training session's parameter by drill and the total sum of it
    '''
    families = open_json_file(families_file)
    total_dist = 0
    session_dict = {parameter: 0, "session's drills": {}}
    # iterate over each drill in the input
    for drill in drills:
        # find drill's family name
        drill_fam = extract_family_name(drill)
        # copy drill's parameter values to the training session dict
        session_dict["session's drills"][drill] = families[drill_fam][drill]["parameters"]
        # update the total training session "Distance per Minute (alt.)" parameter
        find_parameter(parameter, families[drill_fam][drill])
        total_dist += families[drill_fam][drill]["parameters"][parameter]["team's mean"]
    session_dict[parameter] = total_dist
    pprint.pprint(session_dict)
    return session_dict


def build_drills_combination(families, fam1, fam2, parameter):
    '''
    helper function to the "build_session" function - find all unite drills combinations by families
    :param families: dictionary of all family drills
    :param fam1: family name as a string
    :param fam2: family name as a string OR list of drills combinations
    :param parameter: the parameter to sum
    :return: list of all drills combinations between two or more families
    '''
    combinations = []
    # get family 1 data from the families dict
    fam1_dict = families.get(fam1)
    # check if 'fam2' parameter is a list or just a name of family
    if str == type(fam2):
        # if yes - get family 2 data from the families dict
        fam2_dict = families.get(fam2)
        # iterate over each drill in the two families and save the combinations into a list
        for drill1 in fam1_dict:
            find_parameter(parameter, fam1_dict[drill1])
            for drill2 in fam2_dict:
                find_parameter(parameter, fam2_dict[drill2])
                drill1_val = fam1_dict[drill1]['parameters'][parameter]["team's mean"]
                drill2_val = fam2_dict[drill2]['parameters'][parameter]["team's mean"]
                # save to list as a list - [(drill from fam1, it's distance value), (drill from fam2, it's distance value), there total distance sum]
                temp_combo = [(drill1, drill1_val), (drill2, drill2_val), drill1_val + drill2_val]
                combinations.append(temp_combo)
    else:
        # fam 2 is a list
        # iterate over each drill in the two families and save the combinations into a list
        for drill1 in fam1_dict:
            find_parameter(parameter, fam1_dict[drill1])
            # iterate over all previous combinations that were found
            for drills_combo in fam2:
                temp_combo = [stat for stat in drills_combo]
                drill1_val = fam1_dict[drill1]['parameters'][parameter]["team's mean"]
                # add the new drill to the drill combination
                temp_combo.insert(0, (drill1, drill1_val))
                # update the combination's total sum of distance
                temp_combo[-1] += drill1_val
                combinations.append(temp_combo)
    return combinations


def build_session(sb, families_file="../data/families.json"):
    '''
    builds a training session by a distance value training and specific families of drills
    :param families_file: frills families file path
    :param sb: sessions build params as a SessionBuild class
    :return: dictionary of training session options - total sum of the session and of each drill
    '''
    families = open_json_file(families_file)
    drill_fams, parameter, low_val, high_val = sb.get_session_params()
    combos = list()
    session_options = dict()
    # use our "build_drills_combination" helper function to find drills combinations
    for drill_index in range(len(drill_fams) - 1):
        # if first iteration - the func should get two strings as an input
        if drill_index == 0:
            combos = build_drills_combination(families, drill_fams[drill_index], drill_fams[drill_index + 1], parameter)
        # we used the second drill in the first iteration
        elif drill_index != 1:
            combos = build_drills_combination(families, drill_fams[drill_index], combos, parameter)
    # sort all combinations by the total distance value - from the highest to lowest
    combos.sort(key=lambda combo_lam: combo_lam[-1], reverse=True)
    # get the session's last family data
    last_fam = families.get(drill_fams[-1])
    # compute our value edges we should not exceed
    option_num = 1
    if len(drill_fams) == 2:
        last_fam = ["one iteration"]
    # iterate over each drill
    for drill in last_fam:
        if len(drill_fams) == 2:
            drill_val = 0
        else:
            find_parameter(parameter, last_fam[drill])
            drill_val = last_fam[drill]['parameters'][parameter]["team's mean"]
        # iterate over each combination that was found
        for combo in combos:
            # add the last family drill val to the combination's total sum
            total_mean = drill_val + combo[-1]
            # if it exceeds the higher boundary - check the next combination (sorted from the highest value to the lowest)
            if total_mean > high_val:
                continue
            # if it exceeds the lower boundary - check the next drill from the last family (families are sorted from the lowest value to the highest)
            elif total_mean < low_val:
                break
            # if it's in the right range - update the session options dict
            else:
                # align option title
                option_num_str = str(option_num)
                while len(option_num_str) != 3:
                    option_num_str = "0" + option_num_str
                session_title = "session option number " + option_num_str
                option_num += 1
                session_options[session_title] = {"drills": {}}
                if len(drill_fams) != 2:
                    session_options[session_title]["drills"][drill] = families[extract_family_name(drill)].get(drill)
                    total_variance = families[extract_family_name(drill)][drill]['parameters'][parameter].get("team's variance")
                else:
                    total_variance = 0
                for dr in combo:
                    if not tuple == type(dr):
                        break
                    session_options[session_title]["drills"][dr[0]] = families[extract_family_name(dr[0])].get(dr[0])
                    total_variance += families[extract_family_name(dr[0])][dr[0]]['parameters'][parameter].get("team's variance")
                session_options[session_title]["total mean"] = round(total_mean, 3)
                session_options[session_title]["total variance"] = round(total_variance, 3)
                # calculate low dan high val probabilities
                mean = session_options[session_title]["total mean"]
                variance = session_options[session_title]["total variance"]
                standard_deviation = variance ** 0.5
                # Calculate the z-score for the boundary values
                z_low = (low_val - mean) / standard_deviation
                z_high = (high_val - mean) / standard_deviation
                # CDF to calculate the probability of exceeding top and bottom boundaries
                proba_low = norm.cdf(z_low)
                proba_high = 1 - norm.cdf(z_high)
                session_options[session_title]["exceeded limit probabilities"] = (round(proba_low, 3),
                                                                                  round(proba_high, 3))
                if not sb.check_constrains(session_options[session_title]["drills"]):
                    # constrains did not meet with the training session option
                    del session_options[session_title]
                    option_num -= 1
    pprint.pprint(session_options)
    return session_options
