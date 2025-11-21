import unittest
from src.collocations.cooccurrence_extractor import CooccurrenceExtractor


class TestCooccurrenceExtractor(unittest.TestCase):

    def setUp(self):
        self.extractor = CooccurrenceExtractor()

    def test_extract_basic_cooccurrences(self):
        sentences = [
            "נקודה חשובה בדיון",
            "נקודה נוספת במשחק",
        ]
        cooccurrences = self.extractor.extract_cooccurrences("נקודה", sentences)
        
        self.assertIsInstance(cooccurrences, dict)
        self.assertIn("חשובה", cooccurrences)
        self.assertIn("במשחק", cooccurrences)

    def test_empty_sentences(self):
        cooccurrences = self.extractor.extract_cooccurrences("נקודה", [])
        self.assertEqual(cooccurrences, {})

    def test_no_matching_lemma(self):
        sentences = ["אין כאן שום דבר"]
        cooccurrences = self.extractor.extract_cooccurrences("נקודה", sentences)
        self.assertIsInstance(cooccurrences, dict)


if __name__ == '__main__':
    unittest.main()