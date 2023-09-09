import unittest
import os
import json
import tempfile
import csv
from app_main.build_training_session import *
from app_main.helper_functions import open_json_file, write_to_json_file, find_parameter, extract_family_name, remove_set_num_from_drill_name
from app_main.project_classes import SessionBuild
from app_main.new_data_update import update_data


class TestUpdateData(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.ref_families_file = os.path.join(self.temp_dir, "families.json")
        self.ref_stats_file = os.path.join(self.temp_dir, "stats.json")
        
        ref_families_data = {"family1": {}, "family2": {}}
        ref_stats_data = {"drill1": {"parameters": {}}}
        
        with open(self.ref_families_file, "w") as ref_families_file:
            json.dump(ref_families_data, ref_families_file)
        
        with open(self.ref_stats_file, "w") as ref_stats_file:
            json.dump(ref_stats_data, ref_stats_file)
        
        self.ref_csv_file = os.path.join(self.temp_dir, "ref.csv")
        with open(self.ref_csv_file, "w", newline="", encoding="utf-8") as csvfile:
            csvwriter = csv.writer(csvfile)
            header = ["Session Number", "Drill Title", "Player Last Name", "Total Distance"]
            csvwriter.writerow(header)
            data_row = ["1", "Drill 1 Set 1", "Player1", "100"]
            csvwriter.writerow(data_row)

    def tearDown(self):
        os.rmdir(self.temp_dir)

    def test_update_data(self):
        result = update_data(self.ref_csv_file, self.ref_families_file, self.ref_stats_file)
        self.assertEqual(result, 0)
        
        with open(self.ref_stats_file, "r") as stats_file:
            updated_stats_data = json.load(stats_file)
        
        with open(self.ref_families_file, "r") as families_file:
            updated_families_data = json.load(families_file)
            
        self.assertIn("Drill 1 Set 1", updated_stats_data)
        self.assertIn("Drill 1 Set 1", updated_families_data.get("family1", {}))


class TestSessionBuildClass(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.ref_families_file = os.path.join(self.temp_dir, "families.json")
        with open(self.ref_families_file, "w") as ref_families_file:
            json.dump({"family1": "data1", "family2": "data2"}, ref_families_file)

        self.ref_session_file = os.path.join(self.temp_dir, "BuildSession.json")
        ref_session_data = {
            "session": {
                "fams": ["family1", "family2"],
                "parameter": "Total Distance",
                "min_val": 0,
                "max_val": 100,
            },
            "constrains": [
                {
                    "fams": ["family1"],
                    "operator": "range",
                    "parameter": "Total Distance",
                    "min_val": 10,
                    "max_val": 50,
                },
                {
                    "fams": ["family2"],
                    "operator": "sum range",
                    "parameter": "Total Distance",
                    "min_val": 30,
                    "max_val": 80,
                },
            ],
        }
        with open(self.ref_session_file, "w") as ref_session_file:
            json.dump(ref_session_data, ref_session_file)

    def tearDown(self):
        os.rmdir(self.temp_dir)

    def test_session_build_init(self):
        session_build = SessionBuild(session_dict_path=self.ref_session_file)        
        self.assertEqual(session_build.session_fams, ["family1", "family2"])
        self.assertEqual(session_build.parameter, "Total Distance")
        self.assertEqual(session_build.min_val, 0)
        self.assertEqual(session_build.max_val, 100)

    def test_check_session_params(self):
        invalid_session_data = {
            "session": {
                "fams": ["invalid_family"],
                "parameter": "Invalid Parameter",
                "min_val": -10,
                "max_val": 5,
            }
        }
        invalid_session_path = os.path.join(self.temp_dir, "InvalidSession.json")
        with open(invalid_session_path, "w") as invalid_session_file:
            json.dump(invalid_session_data, invalid_session_file)

        with self.assertRaises(ValueError):
            SessionBuild(session_dict_path=invalid_session_path)

    def test_check_constrain_params(self):
        invalid_constraints_data = {
            "session": {
                "fams": ["family1", "family2"],
                "parameter": "Total Distance",
                "min_val": 0,
                "max_val": 100,
            },
            "constrains": [
                {
                    "fams": "invalid_family",  # Invalid: should be a list
                    "operator": "range",
                    "parameter": "Total Distance",
                    "min_val": 10,
                    "max_val": 50,
                }]}
        
        invalid_constraints_path = os.path.join(self.temp_dir, "InvalidConstraints.json")
        with open(invalid_constraints_path, "w") as invalid_constraints_file:
            json.dump(invalid_constraints_data, invalid_constraints_file)
        with self.assertRaises(ValueError):
            SessionBuild(session_dict_path=invalid_constraints_path)


class TestHelperFunctions(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.reference_json_path = os.path.join(self.temp_dir, "reference.json")
        with open(self.reference_json_path, "w") as reference_json_file:
            json.dump({"test": "test"}, reference_json_file)
            
    def tearDown(self):
        os.rmdir(self.temp_dir)

    def test_open_json_file(self):
        data = open_json_file(self.reference_json_path)
        self.assertEqual(data, {"key": "value"})

    def test_write_to_json_file(self):
        output_json_path = os.path.join(self.temp_dir, "output.json")
        data_dict = {"key": "value"}
        write_to_json_file(output_json_path, data_dict)
        with open(output_json_path, "r") as output_json_file:
            output_data = json.load(output_json_file)
        
        self.assertEqual(output_data, data_dict)

    def test_find_parameter(self):
        drill_dict = {"parameters": ["param1", "param2", "param3"]}
        with self.assertRaises(ValueError):
            find_parameter("param4", drill_dict)

    def test_extract_family_name(self):
        self.assertEqual(extract_family_name("Ball Passing Drill"), "possession")
        self.assertEqual(extract_family_name("Large Group Drill"), "lsg")
        self.assertEqual(extract_family_name("Vs+ Drill"), "joker games")
        self.assertEqual(extract_family_name("Warm-up Drill"), "fitness")
        self.assertEqual(extract_family_name("Sided Drill"), "sided games")

    def test_remove_set_num_from_drill_name(self):
        self.assertEqual(remove_set_num_from_drill_name("Drill 1 Set 1"), "drill")


class TestBuildTrainingSession(unittest.TestCase):
    def test_get_session_val(self):
        output = get_session_val(
            "tests/data/bsGSV/families.json",
            [
                "Tactical Defense & Offence",
                "SSG 6vs6+12F",
                "Split: Offense, Finishing Competition",
            ],
            "Total Distance",
        )
        ref_file = open_json_file("tests/data/bsGSV/reference.json")
        self.assertEqual(output, ref_file, "output and reference doesn't match.")

    def test_build_drills_combination(self):
        families_dict = open_json_file("tests/data/bsBDC/families.json")
        output = build_drills_combination(
            families_dict, "lsg", "rondo", "Total Distance"
        )
        write_to_json_file("tests/data/bsBDC/temp_output.json", output)
        output = open_json_file("tests/data/bsBDC/temp_output.json")
        ref_file = open_json_file("tests/data/bsBDC/reference.json")
        self.assertEqual(output, ref_file, "output and reference doesn't match.")
        if os.path.exists("tests/data/bsBDC/temp_output.json"):
            os.remove("tests/data/bsBDC/temp_output.json")

    def test_build_session(self):
        families_file_path = "tests/data/bsBS/families.json"
        sb_params = SessionBuild("tests/data/bsBS/BuildSession.json")
        output = build_session(families_file_path, sb_params)
        ref_file = open_json_file("tests/data/bsBS/reference.json")
        self.assertEqual(
            len(output), len(ref_file), "output and reference doesn't match."
        )
        self.assertEqual(
            ref_file.keys(), output.keys(), "output and reference doesn't match."
        )


if __name__ == "__main__":
    unittest.main()
