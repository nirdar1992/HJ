import unittest
import os
import json
import tempfile
from app_main.build_training_session import *
from app_main.helper_functions import open_json_file, write_to_json_file, find_parameter, extract_family_name, remove_set_num_from_drill_name


class TestYourFunctions(unittest.TestCase):
    def setUp(self):
        # create a temporary directory to store test json file
        self.temp_dir = tempfile.mkdtemp()
        
        self.reference_json_path = os.path.join(self.temp_dir, "reference.json")
        with open(self.reference_json_path, "w") as reference_json_file:
            json.dump({"test": "test"}, reference_json_file)
            
    def tearDown(self):
        # remove the temporary directory and its contents.
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
