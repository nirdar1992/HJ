# HAPOEL JERUSALEM FC PROJECT
## Project Repo
### Data Folder
Training history data csv files by month.

**stats.json file:**

Dictionary that contains for each training drill it's computed values [for the "Distance per Minute", "SpeedZone >=4m/s (km)", "SpeedZone >=5m/s (km)", "SpeedZone >=7m/s (km)", "Accel Zone >= 3m/s²" and "Decel Zone <= -3m/s²" parameters] for the all team and for each player seperately.

The dictionary is arranged as follows:
```
{
"Drill_1_Name": {
"num of sets": number of sets recorded and computed, 
"parameters": {
                "Distance per Minute": {
                                        "dist. type": parameter's distribution type,
                                        "team's mean": all team's mean,
                                        "team's variance": all team's variance,
                                        "players": {
                                                    "Player_1_Name": [[numerical value, "player's mean"],
                                                                      [numerical value, "player's variance"],
                                                                      [value_1, value's percentile according to the other player's values],
                                                                      [value_2, value's percentile according to the other player's values],...],
                                                    "Player_2_Name": [[numerical value, "player's mean"],
                                                    [numerical value, "player's variance"],
                                                    [value_1, value's percentile according to the other player's values],
                                                    [value_2, value's percentile according to the other player's values],...],...
                                                    } // end of "players dict"
                                          }, // end of "Distance per Minute" dict
                "SpeedZone >=4m/s (km)": {...},
                "SpeedZone >=5m/s (km)": {...},
                "SpeedZone >=7m/s (km)": {...},
                "Accel Zone >= 3m/s²": {...},
                "Decel Zone <= -3m/s²": {...}
              } // end of "parameters" dict                                                                    
            } // end of "Drill_1_Name" dict
"Drill_2_Name: {...}
...
} // end of stats dict
```
                                                     
