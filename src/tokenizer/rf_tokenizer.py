class RfTokenizer:
    def __init__(self):
        pass

    def tokenize(self, text):
        # Basic tokenization logic for Hebrew text
        tokens = text.split()  # Simple whitespace-based tokenization
        return [token for token in tokens if token]  # Filter out empty tokens

    def preprocess(self, text):
        # Preprocessing steps can be added here (e.g., normalization)
        return text.strip()

    def tokenize_with_preprocessing(self, text):
        preprocessed_text = self.preprocess(text)
        return self.tokenize(preprocessed_text)