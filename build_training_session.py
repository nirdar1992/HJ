import json
from helper_functions import *

SD_MEAN = 0.2
families_file = "data/families.json"
global families
with open(families_file) as js_file:
    families = json.load(js_file)

def rec_sum(drills, val, fam_name, parameter, sd, sub_drills=[]):
    if val <= sd and val >= (sd*(-1)):
        return sub_drills
    elif len(drills) == 0:
        return []
    else:
        temp_val = val - families[fam_name][drills[0]]["parameters"][parameter]["team's mean"]
        temp_drills = [drill for drill in drills]
        d = temp_drills.pop(0)
        new_sbd = [drill for drill in sub_drills]
        new_sbd.append(d)
        return rec_sum(temp_drills, val, fam_name, parameter, sd, sub_drills), rec_sum(temp_drills, temp_val, fam_name, parameter, sd, new_sbd)

def find_equal_drill(drill_name, paramter="Distance per Minute (alt.)"):
    fam_name = extract_family_name(drill_name)

    mean_to_reach = families[fam_name][drill_name]["parameters"][paramter]["team's mean"]
    var_to_reach = families[fam_name][drill_name]["parameters"][paramter]["team's variance"]

    fam_drills = list(families[fam_name].keys())
    fam_drills.remove(drill_name)
    result = rec_sum(fam_drills, mean_to_reach, fam_name, paramter, mean_to_reach*SD_MEAN)
    #while type(result[0]) != list:
       # result = result[0]
    print(result)





find_equal_drill("OFFENCE")



