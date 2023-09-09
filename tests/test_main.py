import unittest
import os
from app_main.build_training_session import *
from app_main.helper_functions import open_json_file, write_to_json_file


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
