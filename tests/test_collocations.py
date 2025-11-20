import unittest
from src.collocations.cooccurrence_extractor import CooccurrenceExtractor

class TestCooccurrenceExtractor(unittest.TestCase):

    def setUp(self):
        self.extractor = CooccurrenceExtractor()
        self.sample_text = "נקודה היא מונח בשפה העברית. נקודה יכולה להיות גם מונח בספורט."
        self.lemma = "נקודה"

    def test_extract_cooccurrences(self):
        cooccurrences = self.extractor.extract_cooccurrences(self.sample_text, self.lemma)
        expected_cooccurrences = {"מונח": 2, "בשפה": 1, "העברית": 1, "יכולה": 1, "גם": 1, "בספורט": 1}
        self.assertEqual(cooccurrences, expected_cooccurrences)

    def test_empty_text(self):
        cooccurrences = self.extractor.extract_cooccurrences("", self.lemma)
        self.assertEqual(cooccurrences, {})

    def test_no_cooccurrences(self):
        cooccurrences = self.extractor.extract_cooccurrences("אין כאן שום דבר שקשור", self.lemma)
        self.assertEqual(cooccurrences, {})

    def test_multiple_lemmas(self):
        another_lemma = "מונח"
        cooccurrences = self.extractor.extract_cooccurrences(self.sample_text, another_lemma)
        expected_cooccurrences = {"נקודה": 2, "היא": 1, "בשפה": 1, "העברית": 1, "יכולה": 1, "גם": 1, "בספורט": 1}
        self.assertEqual(cooccurrences, expected_cooccurrences)

if __name__ == '__main__':
    unittest.main()