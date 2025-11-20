import unittest
from src.tokenizer.rf_tokenizer import RfTokenizer

class TestRfTokenizer(unittest.TestCase):

    def setUp(self):
        self.tokenizer = RfTokenizer()

    def test_tokenize_simple_sentence(self):
        text = "אני אוהב ללמוד"
        expected_output = ["אני", "אוהב", "ללמוד"]
        self.assertEqual(self.tokenizer.tokenize(text), expected_output)

    def test_tokenize_with_punctuation(self):
        text = "שלום! איך אתה?"
        expected_output = ["שלום", "איך", "אתה"]
        self.assertEqual(self.tokenizer.tokenize(text), expected_output)

    def test_tokenize_empty_string(self):
        text = ""
        expected_output = []
        self.assertEqual(self.tokenizer.tokenize(text), expected_output)

    def test_tokenize_numbers(self):
        text = "יש לי 2 תפוחים"
        expected_output = ["יש", "לי", "2", "תפוחים"]
        self.assertEqual(self.tokenizer.tokenize(text), expected_output)

    def test_tokenize_special_characters(self):
        text = "המחיר הוא 100₪"
        expected_output = ["המחיר", "הוא", "100₪"]
        self.assertEqual(self.tokenizer.tokenize(text), expected_output)

if __name__ == '__main__':
    unittest.main()