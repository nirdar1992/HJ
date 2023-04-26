from helper_functions import *

# define the precent we would consider to exceed from our distance target value
SD_MEAN = 0.2
# load families dict
families_file = "data/families.json"
global families
with open(families_file) as js_file:
    families = json.load(js_file)


def rec_sum(drills, val, fam_name, parameter, sd, sub_drills=[]):
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
    if val <= sd and val >= (sd*(-1)):
        return sub_drills
    # if there is no more drills to check - return an empty list
    elif len(drills) == 0:
        return []
    else:
        # subtract the new drill parameter value from our target value
        temp_val = val - families[fam_name][drills[0]]["parameters"][parameter]["team's mean"]
        # remove the drill from our family drills because we've just iterated over it
        temp_drills = [drill for drill in drills]
        # get that drill name
        d = temp_drills.pop(0)
        # add it to our sub drills list
        new_sbd = [drill for drill in sub_drills]
        new_sbd.append(d)
        # call the function recursively, once without taking the last drill in consider and once with it
        return rec_sum(temp_drills, val, fam_name, parameter, sd, sub_drills), rec_sum(temp_drills, temp_val, fam_name, parameter, sd, new_sbd)


def find_equal_drill(drill_name, parameter="Distance per Minute (alt.)"):
    '''
    function which finds a drill/s or drills combinations that sums up to a specific drill parameter value
    :param drill_name: drill's name we would like to replace
    :param parameter: parameter's name we search by
    :return: list of lists of drills combinations that could replace the target drill
    '''
    # find drill's family name
    fam_name = extract_family_name(drill_name)
    # extract the target value
    mean_to_reach = families[fam_name][drill_name]["parameters"][parameter]["team's mean"]
    var_to_reach = families[fam_name][drill_name]["parameters"][parameter]["team's variance"]
    # create list of the drills names from the same family and remove the drill we want to replace
    fam_drills = list(families[fam_name].keys())
    fam_drills.remove(drill_name)
    # call the "rec_sum" function and find our drills, print/return it
    result = rec_sum(fam_drills, mean_to_reach, fam_name, parameter, mean_to_reach*SD_MEAN)
    #print(result)
    return result


def get_session_val(*drills):
    '''
    :param drills: unlimited drills names that represents a training session
    :return: dictionary which contains the training session's "Distance per Minute (alt.)" by drill and the total sum fo it
    '''
    total_dist = 0
    session_dict = {"session's total Distance per Minute (alt.)": 0, "session's drills": {}}
    # iterate over each drill in the input
    for drill in drills:
        # find drill's family name
        drill_fam = map_drill_fam(drill)
        # copy drill's parameter values to the training session dict
        session_dict["session's drills"][drill] = families[drill_fam][drill]["parameters"]
        # update the total training session "Distance per Minute (alt.)" parameter
        total_dist += families[drill_fam][drill]["parameters"]["Distance per Minute (alt.)"]["team's mean"]
    session_dict["session's total Distance per Minute (alt.)"] = total_dist
    #print(session_dict)
    return session_dict

def build_drills_combination(fam1, fam2):
    '''
    helper function to the "build_session" function - find all unite drills combinations by families
    :param fam1: family name as a string
    :param fam2: family name as a string OR list of drills combinations
    :return:
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
            for drill2 in fam2_dict:
                drill1_val = fam1_dict[drill1]['parameters']["Distance per Minute (alt.)"]["team's mean"]
                drill2_val = fam2_dict[drill2]['parameters']["Distance per Minute (alt.)"]["team's mean"]
                # save to list as a list - [(drill from fam1, it's distance value), (drill from fam2, it's distance value), there total distance sum]
                temp_combo = [(drill1, drill1_val), (drill2, drill2_val), drill1_val + drill2_val]
                combinations.append(temp_combo)
    else:
        # fam 2 is a list
        # iterate over each drill in the two families and save the combinations into a list
        for drill1 in fam1_dict:
            # iterate over all previous combinations that were found
            for drills_combo in fam2:
                temp_combo = drills_combo
                drill1_val = fam1_dict[drill1]['parameters']["Distance per Minute (alt.)"]["team's mean"]
                # add the new drill to the drill combination
                temp_combo.insert(0, (drill1, drill1_val))
                # update the combination's total sum of distance
                temp_combo[-1] += drill1_val
                combinations.append(temp_combo)
    return combinations


def build_session(target_distance, *drill_fams):
    '''
    builds a training session by a distance value training and specific families of drills
    :param target_distance: target value for the training session
    :param drill_fams: unlimited number of families that should build the training session
    :return: dictionary of training session options - total sum of the session and of each drill
    '''
    combos = list()
    session_options = dict()
    # use our "build_drills_combination" helper function to find drills combinations
    for drill_index in range(len(drill_fams) - 1):
        # if first iteration - the func should get two strings as an input
        if drill_index == 0:
            combos = build_drills_combination(drill_fams[drill_index], drill_fams[drill_index + 1])
        # we used the second drill in the first iteration
        elif drill_index != 1:
            combos = build_drills_combination(drill_fams[drill_index], combos)
    # sort all combinations by the total distance value - from the highest to lowest
    combos.sort(key=lambda combo: combo[-1], reverse=True)
    # get the session's last family data
    last_fam = families.get(drill_fams[-1])
    # compute our value edges we should not exceed
    low_val = (1 - SD_MEAN) * target_distance
    high_val = (1 + SD_MEAN) * target_distance
    option_num = 1
    # iterate over each drill
    for drill in last_fam:
        drill_val = last_fam[drill]['parameters']["Distance per Minute (alt.)"]["team's mean"]
        # iterate over each combination that was found
        for combo in combos:
            # add the last family drill val to the combination's total sum
            total_dist = drill_val + combo[-1]
            # if it exceeds the higher boundary - check the next combination (sorted from the highest value to the lowest)
            if total_dist > high_val:
                continue
            # if it exceeds the lower boundary - check the next drill from the last family (families are sorted from the lowest value to the highest)
            elif total_dist < low_val:
                break
            # if it's in the right range - update the session options dict
            else:
                session_title = "session option number " + str(option_num)
                option_num += 1
                session_options[session_title] = {"total distance": total_dist, "drills": {}}
                session_options[session_title]["drills"][drill] = drill_val
                for dr in combo:
                    if not tuple == type(dr):
                        break
                    session_options[session_title]["drills"][dr] = dr[1]
    return session_options
