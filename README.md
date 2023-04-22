# HAPOEL JERUSALEM FC PROJECT
## Project Repo
### Data Folder
1. **Training history data csv files by month.**

2. **stats.json file:**

Dictionary that contains for each training drill it's computed values [for the "Distance per Minute", "SpeedZone >=4m/s (km)", "SpeedZone >=5m/s (km)", "SpeedZone >=7m/s (km)", "Accel Zone >= 3m/s²" and "Decel Zone <= -3m/s²" parameters] for the all team and for each player seperately.

The dictionary is arranged as follows:
```
{
  "Drill_1_Name": {
                  "num of sets": number of sets recorded and computed, 
                  "parameters": {
                                  "Distance per Minute (alt.)": {
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

3. **families.json file:**

Dictionary that contains all the drills seperated by groups of context, as we call "family".

The dictionary is arranged as follows:
```
{
  "Family_1_Name": {
                    "Drill_1_Name": {
                                      "parameters": {
                                                      "Distance per Minute (alt.)": {
                                                                                      "team's mean": all team's mean,
                                                                                      "team's variance": all team's variance
                                                                                    }, // end of "Distance per Minute (alt.)" dict
                                                      "SpeedZone >=4m/s (km)": {
                                                                                  "team's mean": all team's mean,
                                                                                  "team's variance": all team's variance
                                                                                }, // end of "SpeedZone >=4m/s (km)" dict
                                                      "SpeedZone >=5m/s (km)": {
                                                                                  "team's mean": all team's mean,
                                                                                  "team's variance": all team's variance
                                                                                }, // end of "SpeedZone >=5m/s (km)" dict
                                                      "SpeedZone >=7m/s (km)": {
                                                                                  "team's mean": all team's mean,
                                                                                  "team's variance": all team's variance
                                                                               }, // end of "SpeedZone >=7m/s (km)" dict
                                                      "Accel Zone >= 3m/s²": {
                                                                              "team's mean": all team's mean,
                                                                              "team's variance": all team's variance
                                                                              }, // end of "Accel Zone >= 3m/s²" dict
                                                      "Decel Zone <= -3m/s²": {
                                                                                "team's mean": all team's mean,
                                                                                "team's variance": all team's variance
                                                                              } // end of "Decel Zone <= -3m/s²" dict
                                                      } // end of "parameters" dict
                                        }, // end of "Drill_1_Name" dict
                    "Drill_2_Name": {...}, ...             
                   }, // end of "Family_1_Name" dict
  "Family_2_Name": {...}, ...
} // end of families dict
```


### new_data_update.py file
Updating the stats.json and families.json files when reciving new data csv file.

**functions explanations marks are inside the file.**


### build_training_session.py file
1. Building training session according to given type of drills and a "Distance per Minute (alt.)" target value.
2. Sums up the "Distance per Minute (alt.)" parameter for a given training session.
3. Finding alternative drill/s for a giving drill by it's "Distance per Minute (alt.)" value.
4. 
**functions explanations marks are inside the file.**

### helper_functions.py file
Contains different commonly used functions.

**functions explanations marks are inside the file.**
