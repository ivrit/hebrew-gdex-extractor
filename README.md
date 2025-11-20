# Hebrew GDEX Library

This project is a library designed to generate profiles of typical uses for Hebrew lemmas, often referred to as Good Dictionary Examples (GDEX). The library leverages various natural language processing techniques, including lemmatization, tokenization, word sense disambiguation, and co-occurrence extraction, to provide meaningful examples for each lemma.

## Features

- **Lemmatization**: Efficiently lemmatizes Hebrew words to their base forms.
- **Tokenization**: Implements a tokenizer specifically for Hebrew text.
- **Word Sense Disambiguation**: Provides lightweight methods to determine the correct sense of a word based on context.
- **Co-occurrence Extraction**: Analyzes text to find common co-occurrences of words, aiding in the generation of relevant examples.
- **Example Generation**: Produces good dictionary examples based on the extracted co-occurrence patterns.

## Project Structure

```
hebrew-gdex-library
├── src                     # Source code for the library
│   ├── lemmatizer         # Lemmatization module
│   ├── tokenizer           # Tokenization module
│   ├── sense_disambiguation # Word sense disambiguation module
│   ├── collocations        # Co-occurrence extraction module
│   ├── example_generator    # Example generation module
│   └── utils               # Utility functions
├── tests                   # Unit tests for the library
├── data                    # Data directories for corpus and models
├── config                  # Configuration files
├── .env.example            # Example environment variables
├── .gitignore              # Git ignore file
├── requirements.txt        # Project dependencies
└── setup.py                # Packaging information
```

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/hebrew-gdex-library.git
   cd hebrew-gdex-library
   ```

2. Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables by copying `.env.example` to `.env` and modifying it as needed.

## Usage

To use the library, import the necessary modules in your Python script. Here’s a simple example:

```python
from src.lemmatizer.hebrew_lemmatizer import HebrewLemmatizer
from src.tokenizer.rf_tokenizer import RfTokenizer
from src.sense_disambiguation.wsd_handler import WsdHandler
from src.collocations.cooccurrence_extractor import CooccurrenceExtractor
from src.example_generator.gdex_scorer import GdexScorer

# Initialize components
lemmatizer = HebrewLemmatizer()
tokenizer = RfTokenizer()
wsd_handler = WsdHandler()
cooccurrence_extractor = CooccurrenceExtractor()
gdex_scorer = GdexScorer()

# Example usage
text = "הנקודה במשחק הייתה חשובה"
tokens = tokenizer.tokenize(text)
lemmas = [lemmatizer.lemmatize(token) for token in tokens]
senses = wsd_handler.disambiguate(lemmas)
cooccurrences = cooccurrence_extractor.extract(lemmas)
examples = gdex_scorer.generate_examples(cooccurrences)
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.