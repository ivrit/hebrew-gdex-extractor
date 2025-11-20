import unittest
from src.lemmatizer.hebrew_lemmatizer import HebrewLemmatizer

class TestHebrewLemmatizer(unittest.TestCase):

    def setUp(self):
        self.lemmatizer = HebrewLemmatizer()

    def test_lemmatize_single_word(self):
        word = "נקודה"
        expected_lemma = "נקודה"  # Adjust based on the actual lemmatization logic
        result = self.lemmatizer.lemmatize(word)
        self.assertEqual(result, expected_lemma)

    def test_lemmatize_word_with_suffix(self):
        word = "נקודות"
        expected_lemma = "נקודה"  # Adjust based on the actual lemmatization logic
        result = self.lemmatizer.lemmatize(word)
        self.assertEqual(result, expected_lemma)

    def test_lemmatize_different_forms(self):
        words = ["נקודה", "נקודות", "נקודתי"]
        expected_lemmas = ["נקודה", "נקודה", "נקודה"]  # Adjust based on the actual lemmatization logic
        results = [self.lemmatizer.lemmatize(word) for word in words]
        self.assertEqual(results, expected_lemmas)

    def test_lemmatize_non_hebrew_word(self):
        word = "point"
        expected_lemma = None  # Assuming the lemmatizer returns None for non-Hebrew words
        result = self.lemmatizer.lemmatize(word)
        self.assertEqual(result, expected_lemma)

if __name__ == '__main__':
    unittest.main()