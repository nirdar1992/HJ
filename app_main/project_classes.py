from app_main.helper_functions import *

families_file = "../data/families.json"


class SessionBuild:
    def __init__(self, session_dict_path="../data/BuildSession.json"):
        '''
        :param session_dict_path: path to the desired session json file, "data/BuildSession.json" by default
        '''
        self.session_dict = open_json_file(session_dict_path)
        self.session_fams = self.session_dict["session"].get("fams")
        self.parameter = self.session_dict["session"].get("parameter")
        self.min_val = self.session_dict["session"].get("min_val")
        self.max_val = self.session_dict["session"].get("max_val")
        self.constrains_dict = self.session_dict.get("constrains", [])
        self.valid_parameters = ["Total Distance", "Distance Zone 4 (Absolute)", "Distance Zone 5 (Absolute)",
                                 "Distance Zone 6 (Absolute)", "HSR Per Minute (Absolute)", "Sprint Distance",
                                 "Accelerations Per Min", "Decelerations Per Min", "Max Speed", "Distance Per Min",
                                 "Accelerations", "Decelerations", "HMLD Per Minute", "HML Distance"]
        # validate input params
        self.check_session_params()
        self.check_constrain_params()

    def check_session_params(self):
        '''
        :return: runs at initialization, checks the validation of the session's parameters
        '''
        if type(self.session_fams) != list:
            raise ValueError("Session's families input should be a list of families.")
        for fam in self.session_fams:
            families = open_json_file(families_file)
            if fam not in families:
                raise ValueError(fam + " is not in families json file, Please check your spelling.")
        if self.parameter not in self.valid_parameters:
            raise ValueError(self.parameter + " is not a valid parameter, please check your spelling.")
        if self.min_val < 0 or self.max_val < 0:
            raise ValueError("Minimum/Maximum value can not be negative.")
        if self.min_val > self.max_val:
            raise ValueError("Minimum val can not be greater than maximum val.")

    def check_constrain_params(self):
        '''
        :return: runs at initialization, checks the validation of the constrains parameters
        '''
        families = open_json_file(families_file)
        for con in self.constrains_dict:
            if type(self.constrains_dict[con]['fams']) != list:
                raise ValueError("In " + con + ": families input should be a list of families.")
            for fam in self.constrains_dict[con]['fams']:
                if fam not in families:
                    raise ValueError("In " + con + ": " + fam +
                                     " is not in families json file, Please check your spelling.")
            if self.constrains_dict[con]['parameter'] not in self.valid_parameters:
                raise ValueError("In " + con + ": " + self.constrains_dict[con]['parameter'] +
                                 " is not a valid parameter, please check your spelling.")
            if self.constrains_dict[con]['operator'] not in ['range', 'sum range']:
                raise ValueError("In " + con + ": operator must be 'range' or 'sum range'.")
            if self.constrains_dict[con]['min_val'] < 0 or self.constrains_dict[con]['max_val'] < 0:
                raise ValueError("In " + con + ": minimum/maximum value can not be negative.")
            if self.constrains_dict[con]['min_val'] > self.constrains_dict[con]['max_val']:
                raise ValueError("In " + con + ": minimum val can not be greater than maximum val.")

    def get_session_params(self):
        '''
        :return: extract session's parameters
        '''
        return self.session_fams, self.parameter, self.min_val, self.max_val

    def check_constrains(self, drills_dict):
        '''
        :param drills_dict: optional session dictionary (drills with their parameters)
        :return: True if suggested session meets constrains, False if not
        '''
        for con in self.constrains_dict:
            total_sum = 0  # for the 'sum range' constrain
            # extract constrain's parameters
            cons_fams = self.constrains_dict[con]['fams']
            operator = self.constrains_dict[con]['operator']
            parameter = self.constrains_dict[con]['parameter']
            min_val = self.constrains_dict[con]['min_val']
            max_val = self.constrains_dict[con]['max_val']
            fam_summed = []  # ensures constrain activated on family once
            for drill in drills_dict:
                fam_name = extract_family_name(drill)
                if (fam_name not in cons_fams) or fam_name in fam_summed:
                    continue
                if operator == 'range':
                    if not min_val <= drills_dict[drill]["parameters"][parameter]["team's mean"] <= max_val:
                        return False
                else:  # sum range and check it at the end
                    total_sum += drills_dict[drill]["parameters"][parameter]["team's mean"]
                    fam_summed.append(fam_name)
            if operator == 'sum range' and not min_val <= total_sum <= max_val:
                return False
        return True
