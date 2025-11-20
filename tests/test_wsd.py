import unittest
from src.sense_disambiguation.wsd_handler import WsdHandler

class TestWsdHandler(unittest.TestCase):

    def setUp(self):
        self.wsd_handler = WsdHandler()

    def test_disambiguate_single_sense(self):
        word = "נקודה"
        context = "הנקודה במשחק הייתה חשובה"
        expected_sense = "sport"
        result = self.wsd_handler.disambiguate(word, context)
        self.assertEqual(result, expected_sense)

    def test_disambiguate_multiple_senses(self):
        word = "נקודה"
        context = "הנקודה בדיון הייתה מעניינת"
        expected_sense = "argument"
        result = self.wsd_handler.disambiguate(word, context)
        self.assertEqual(result, expected_sense)

    def test_disambiguate_no_context(self):
        word = "נקודה"
        context = ""
        expected_sense = None
        result = self.wsd_handler.disambiguate(word, context)
        self.assertEqual(result, expected_sense)

    def test_disambiguate_unknown_word(self):
        word = "לא_קיים"
        context = "אין כאן שום דבר"
        expected_sense = None
        result = self.wsd_handler.disambiguate(word, context)
        self.assertEqual(result, expected_sense)

if __name__ == '__main__':
    unittest.main()