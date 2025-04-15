"""
Tests that parallel betacode work correctly
"""

import sys
import unittest
import json
import pprint
from pathlib import Path
from parallel_betacode.parallel_betacode import hb_betacode, BetacodeTransformer

# Ajoutez le dossier `src` au chemin d'importation
sys.path.append(str(Path(__file__).resolve().parent.parent))

TEST_FOLDER_DATA = Path(__file__).resolve().parent / "test_data"


class TestParallelBetacode(unittest.TestCase):
    """
    Tests that the parallel_betacode works as expected.
    """
    def test_hb_betacode(self):
        hb_entry = "{..^KY} 3"
        hb_expected = "{..^כי} 3"
        result = hb_betacode(hb_entry)

    def test_parallel_betacode_standard(self):
        with open(TEST_FOLDER_DATA / "text_to_convert_standard.json", "r", encoding="utf-8") as f:
            expected_result = json.load(f)
        text = BetacodeTransformer(TEST_FOLDER_DATA / "text_to_convert_standard.par")
        converted = text.convert()
        self.assertDictEqual(expected_result, converted)

    def test_parallel_betacode_short(self):
        expected_result = {
            "Gen": {
                "1": {
                    "1": {
                        "1": {
                            "hb": "בראשׁית",
                            "gr": "ἐν ἀρχῇ"
                        },
                        "2": {
                            "hb": "ברא",
                            "gr": "ἐποίησεν"
                        }
                    }
                }
            }
        }
        text = BetacodeTransformer(TEST_FOLDER_DATA / "text_to_convert_short.par")
        converted = text.convert()
        self.assertDictEqual(expected_result, converted)
    
    def test_parallel_betacode_empty_file(self):
        """
        Test that the converter handles an empty file.
        """
        empty_file = TEST_FOLDER_DATA / "empty.par"
        text = BetacodeTransformer(empty_file)
        converted = text.convert()
        self.assertDictEqual({}, converted)

if __name__ == "__main__":
    unittest.main()