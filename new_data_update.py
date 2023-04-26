import pandas as pd
import json
from helper_functions import *

# load previous stats
json_file = "data/stats.json"
global stats_dict
with open(json_file) as js_file:
    stats_dict = json.load(js_file)

# load families dict
families_file = "data/families.json"
global families
with open(families_file) as js_file:
    families = json.load(js_file)

# load new data csv file
new_data = pd.read_csv(r'C:\Users\nird\PycharmProjects\HJ\data\feb23.csv')
players_idx = list(new_data.index)
drills = list(new_data.columns)
didnt_particpated = dict()

column_num = len(drills) - 1
while column_num != -1:
    # remove duplicated column names
    if '.' in drills[column_num]:
        drills[column_num] = remove_num_of_parameter_from_drill_name(drills[column_num])

    # concat columns titles to the real drill name due to coma in the original drill name
    if drills[column_num].startswith(" ") or (drills[column_num-1].startswith("16") and drills[column_num].startswith("12M)") or drills[column_num].startswith("8M)")):
        temp_iter = column_num - 1
        temp_name = drills[column_num]
        drills.pop(column_num)
        while drills[temp_iter].startswith(" ") or drills[temp_iter].startswith("16"):
            # remove duplicated column names
            if '.' in drills[temp_iter]:
                drills[temp_iter] = remove_num_of_parameter_from_drill_name(drills[temp_iter])
            temp_name = drills[temp_iter] + temp_name
            drills.pop(temp_iter)
            temp_iter -= 1
        # remove duplicated column names
        if '.' in drills[temp_iter]:
            drills[temp_iter] = remove_num_of_parameter_from_drill_name(drills[temp_iter])
        drills[temp_iter] += temp_name
        column_num = temp_iter
    column_num -= 1

# set the new fixed columns names
new_data = new_data.iloc[:, :len(drills)]
new_data.set_axis(drills, axis=1, inplace=True)


for drill in drills:
    # initialize list that stores name of players which did not participate in the drill
    didnt_particpated[drill] = []
for column_idx in range(len(drills)):
    # players column
    if column_idx == 0:
        continue
    full_drill_name = drills[column_idx]
    # remove duplicated column names
    if '.' in full_drill_name:
        full_drill_name = remove_num_of_parameter_from_drill_name(full_drill_name)
    # extract drill's name without set num
    if full_drill_name[-1] == ")" and full_drill_name[-3] == "(":
        drill_name = full_drill_name[:-4]
    else:
        drill_name = full_drill_name

    # extract parameter name
    parameter = new_data.iloc[0, column_idx]

    # if drill is not in the previous stats - initialize it's variables
    if drill_name not in stats_dict:
        stats_dict[drill_name] = {'num of sets': 0, 'parameters':{'Distance per Minute (alt.)': {'dist. type': 'normal', "team's mean": 0, "team's variance": 0, 'players':{}}, 'SpeedZone >=4m/s (km)': {'dist. type': 'normal', "team's mean": 0, "team's variance": 0, 'players':{}}, 'SpeedZone >=5m/s (km)': {'dist. type': 'normal', "team's mean": 0, "team's variance": 0, 'players':{}}, 'SpeedZone >=7m/s (km)': {'dist. type': 'normal', "team's mean": 0, "team's variance": 0, 'players':{}}, 'Accel Zone >= 3m/s²': {'dist. type': 'poisson', "team's mean": 0, "team's variance": 0, 'players':{}}, 'Decel Zone <= -3m/s²': {'dist. type': 'poisson', "team's mean": 0, "team's variance": 0, 'players':{}}}}
    drill_values = stats_dict[drill_name]['parameters'][parameter].get('players', {})

    # update number of sets
    if parameter.startswith('Distance'):
        stats_dict[drill_name]['num of sets'] = stats_dict[drill_name].get('num of sets') + 1

    # three variables in order to calculate team's distance mean and variance:
    team_mean = 0
    val_counter = 0
    team_squared_mean = 0
    # iterate over all players that participated in the drill
    for player_idx in players_idx:
        # column header
        if player_idx == 0:
            continue
        player_name = new_data.iloc[player_idx,0]
        # get player's previous stats
        player_value = stats_dict[drill_name]['parameters'][parameter]['players'].get(player_name, [0,0])
        player_mean = 0
        player_squared_mean = 0
        # player's current set value - format for each player : [player's mean, [set1 value, precintile], [set2 value, precintile]...]
        curr_player_val = float(new_data.iloc[player_idx, column_idx])
        if parameter.startswith('Distance') and curr_player_val == 0:
            temp_dp = didnt_particpated.get(full_drill_name,[])
            temp_dp.append(player_name)
            didnt_particpated[full_drill_name] = temp_dp
            continue
        if player_name in didnt_particpated.get(full_drill_name,[]):
            continue
        # remove current mean and variance
        player_value.pop(0)
        player_value.pop(0)

        player_value.append([curr_player_val, -1])
        # sort player's stats by the parameter value
        player_value = sorted(player_value,key=lambda x: x[0])
        # calculate precintile
        for i in range(len(player_value)):
            player_value[i][1] = str(round(((i + 1)/len(player_value)*100), 1)) + '%'
            player_mean += player_value[i][0]
            player_squared_mean += (player_value[i][0] ** 2)
            team_mean += player_value[i][0]
            team_squared_mean += (player_value[i][0] ** 2)
            val_counter += 1
        player_mean /= len(player_value)
        player_var = (player_squared_mean / len(player_value)) - (player_mean**2)
        # update player's stats
        player_value.insert(0, [round(player_var,2), "player's variance"])
        player_value.insert(0, [round(player_mean,2), "player's mean"])
        stats_dict[drill_name]['parameters'][parameter]['players'][player_name] = player_value

    # updates team's distance mean and variance
    if val_counter != 0:
        team_var = round((team_squared_mean / val_counter) - ((team_mean/val_counter)**2), 2)
        team_mean = round(team_mean/val_counter, 2)
    else:
        team_var = 0
        team_mean = 0
    stats_dict[drill_name]['parameters'][parameter]["team's mean"] = team_mean
    stats_dict[drill_name]['parameters'][parameter]["team's variance"] = team_var

    # update families dict
    fam_name = extract_family_name(drill_name)
    if families.get(fam_name, {}) == {}:
        families[fam_name] = {}
    if families[fam_name].get(drill_name, {}) == {}:
        families[fam_name][drill_name] = {'parameters': {'Distance per Minute (alt.)': {"team's mean": 0, "team's variance": 0}, 'SpeedZone >=4m/s (km)': {"team's mean": 0, "team's variance": 0}, 'SpeedZone >=5m/s (km)': {"team's mean": 0, "team's variance": 0}, 'SpeedZone >=7m/s (km)': {"team's mean": 0, "team's variance": 0}, 'Accel Zone >= 3m/s²': {"team's mean": 0, "team's variance": 0}, 'Decel Zone <= -3m/s²': {"team's mean": 0, "team's variance": 0}}}
    families[fam_name][drill_name]['parameters'][parameter]["team's mean"] = team_mean
    families[fam_name][drill_name]['parameters'][parameter]["team's variance"] = team_var

# sort families dict by family name
families = dict(sorted(families.items(), key=lambda x: x[0]))
# sort each family drills by "Distance per Minute (alt.)" parameter
for fam in families:
    families[fam] = dict(sorted(families[fam].items(), key=lambda x: x[1]['parameters']["Distance per Minute (alt.)"]["team's mean"]))

# sort stats dict by drill name
stats_dict = dict(sorted(stats_dict.items(), key=lambda x: x[0]))

'''
# display table
df = pd.DataFrame.from_dict(stats_dict)
from tabulate import tabulate
print(tabulate(df, headers='keys', tablefmt='psql'))
'''

# write the updated stats to the 'stats' json file
out_file = open(json_file, "w")
json.dump(stats_dict, out_file, indent="")
out_file.close()

# write the updated family groups to the 'families' json file
out_file = open(families_file, "w")
json.dump(families, out_file, indent="")
out_file.close()
