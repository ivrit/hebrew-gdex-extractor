import unittest
from src.lemmatizer.hebrew_lemmatizer import HebrewLemmatizer


class TestHebrewLemmatizer(unittest.TestCase):

    def setUp(self):
        self.lemmatizer = HebrewLemmatizer()

    def test_lemmatize_plural_to_singular(self):
        result = self.lemmatizer.lemmatize("ספרים")
        self.assertEqual(result, "ספר")

    def test_lemmatize_verb_conjugation(self):
        result = self.lemmatizer.lemmatize("הלכתי")
        self.assertEqual(result, "הלך")

    def test_lemmatize_with_definite_article(self):
        result = self.lemmatizer.lemmatize("הספר")
        self.assertEqual(result, "ספר")

    def test_lemmatize_sentence(self):
        sentence = "הילדים הלכו לבית הספר"
        results = self.lemmatizer.lemmatize_sentence(sentence)
        
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
        self.assertIsInstance(results[0], tuple)

    def test_get_lemmas_only(self):
        sentence = "הילדים הלכו"
        lemmas = self.lemmatizer.get_lemmas_only(sentence)
        
        self.assertIsInstance(lemmas, list)
        self.assertIn("ילד", lemmas)


if __name__ == '__main__':
    unittest.main()