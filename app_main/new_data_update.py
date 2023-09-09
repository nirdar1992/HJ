import csv
import os

from app_main.helper_functions import *


def update_data(
    new_data_file, families_file="../data/families.json", json_file="../data/stats.json"
):
    try:
        families = open_json_file(families_file)
        stats_dict = open_json_file(json_file)
        try:
            new_data_file.save("temp_file.csv")
            new_data_file = "temp_file.csv"
        except:
            pass

        # Open the CSV file for reading
        with open(new_data_file, "r", newline="", encoding="utf-8") as csvfile:
            # Create a CSV reader
            csvreader = csv.reader(csvfile)
            # Read the first row which contains the header
            header = next(csvreader)
            # Find the index of the drill column
            drill_column_index = header.index("Drill Title")
            distance_column_index = header.index("Total Distance")
            player_column_index = header.index("Player Last Name")
            parameters_list = [param for param in header[distance_column_index:]]
            # Iterate through each row in the CSV
            for row in csvreader:
                session_num = row[0]
                raw_drill_name = row[drill_column_index]
                drill_name = remove_set_num_from_drill_name(raw_drill_name)
                # if it's a game stats or player's Distance value is zero, he did not played - skip it
                if "half" in drill_name or float(row[distance_column_index]) == 0:
                    continue

                for parameter in parameters_list:
                    parameter_index = header.index(parameter)

                    # if drill is not in the previous stats - initialize its variables
                    if drill_name not in stats_dict:
                        stats_dict[drill_name] = {
                            "num of sets": 0,
                            "sets list": [],
                            "parameters": {},
                        }
                    if parameter not in stats_dict[drill_name]["parameters"]:
                        stats_dict[drill_name]["parameters"][parameter] = {
                            "team's mean": 0,
                            "team's variance": 0,
                            "players": {},
                        }

                    # update number of sets
                    temp_sets = stats_dict[drill_name].get("sets list", [])
                    if (session_num, raw_drill_name) not in temp_sets:
                        # save pairs of sessions and drills
                        temp_sets.append((session_num, raw_drill_name))
                        stats_dict[drill_name]["sets list"] = temp_sets
                        stats_dict[drill_name]["num of sets"] = (
                            stats_dict[drill_name]["num of sets"] + 1
                        )

                    # get player's previous stats
                    player_name = row[player_column_index]
                    player_value = stats_dict[drill_name]["parameters"][parameter][
                        "players"
                    ].get(player_name, [0, 0])
                    # player's current set value - format for each player : [player's mean, [set1 value, precintile], [set2 value, precintile]...]
                    player_value.append([float(row[parameter_index]), -1])
                    stats_dict[drill_name]["parameters"][parameter]["players"][
                        player_name
                    ] = player_value

        for drill_name in stats_dict:
            try:
                del stats_dict[drill_name]["sets list"]
            except:
                pass
            for parameter in stats_dict[drill_name]["parameters"]:
                player_mean, player_squared_mean = 0, 0
                team_mean, team_squared_mean = 0, 0
                val_counter = 0
                for player_name in stats_dict[drill_name]["parameters"][parameter][
                    "players"
                ]:
                    player_value = stats_dict[drill_name]["parameters"][parameter][
                        "players"
                    ].get(player_name, [0, 0])
                    player_value.pop(0)
                    player_value.pop(0)
                    # sort player's stats by the parameter value
                    player_value = sorted(player_value, key=lambda x: x[0])
                    # calculate precintile
                    for i in range(len(player_value)):
                        player_value[i][1] = (
                            str(round(((i + 1) / len(player_value) * 100), 1)) + "%"
                        )
                        player_mean += player_value[i][0]
                        player_squared_mean += player_value[i][0] ** 2
                        team_mean += player_value[i][0]
                        team_squared_mean += player_value[i][0] ** 2
                        val_counter += 1
                    player_mean /= len(player_value)
                    player_var = (player_squared_mean / len(player_value)) - (
                        player_mean**2
                    )
                    # update player's stats
                    player_value.insert(0, [round(player_var, 2), "player's variance"])
                    player_value.insert(0, [round(player_mean, 2), "player's mean"])
                    stats_dict[drill_name]["parameters"][parameter]["players"][
                        player_name
                    ] = player_value

                # updates team's distance mean and variance
                if val_counter != 0:
                    team_var = round(
                        (team_squared_mean / val_counter)
                        - ((team_mean / val_counter) ** 2),
                        2,
                    )
                    team_mean = round(team_mean / val_counter, 2)
                else:
                    team_var = 0
                    team_mean = 0
                stats_dict[drill_name]["parameters"][parameter][
                    "team's mean"
                ] = team_mean
                stats_dict[drill_name]["parameters"][parameter][
                    "team's variance"
                ] = team_var

                # update families dict
                fam_name = extract_family_name(drill_name)
                if families.get(fam_name, {}) == {}:
                    families[fam_name] = {}
                if families[fam_name].get(drill_name, {}) == {}:
                    families[fam_name][drill_name] = {"parameters": {}}
                if (
                    families[fam_name][drill_name]["parameters"].get(parameter, {})
                    == {}
                ):
                    families[fam_name][drill_name]["parameters"][parameter] = {
                        "team's mean": 0,
                        "team's variance": 0,
                    }
                families[fam_name][drill_name]["parameters"][parameter][
                    "team's mean"
                ] = team_mean
                families[fam_name][drill_name]["parameters"][parameter][
                    "team's variance"
                ] = team_var

        # sort families dict by family name
        families = dict(sorted(families.items(), key=lambda x: x[0]))
        # sort each family drills by "Distance per Minute (alt.)" parameter
        for fam in families:
            families[fam] = dict(
                sorted(
                    families[fam].items(),
                    key=lambda x: x[1]["parameters"]["Total Distance"]["team's mean"],
                )
            )

        # sort stats dict by drill name
        stats_dict = dict(sorted(stats_dict.items(), key=lambda x: x[0]))

        # write the updated stats to the 'stats' json file
        write_to_json_file(json_file, stats_dict)

        # write the updated family groups to the 'families' json file
        write_to_json_file(families_file, families)
        return 0
    except Exception as error_message:
        return error_message
    finally:
        if new_data_file == "temp_file.csv":
            os.remove(new_data_file)
