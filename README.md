# Hebrew GDEX Extractor

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Automatically extract high-quality, sense-diverse dictionary examples for Hebrew words from large corpora.

This library uses **unsupervised clustering** to distinguish word senses and **multi-criteria GDEX scoring** to rank examples by quality, without requiring manually annotated sense inventories.

## Features

- ✅ **Neural lemmatization** using Stanza (handles Hebrew morphology)
- ✅ **Unsupervised word sense disambiguation** via TF-IDF + K-means clustering
- ✅ **Multi-criteria GDEX scoring** (length, completeness, typicality, informativeness)
- ✅ **Parallel processing** for efficient corpus analysis
- ✅ **Collocation analysis** to validate sense clusters
- ✅ **JSON + TXT output** for both machine and human use

## Installation

### Prerequisites
- Python 3.12+
- 4-core CPU, 7GB RAM (recommended)

### Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/ivrit/hebrew-gdex-extractor.git
   cd hebrew-gdex-extractor
   ```

2. **Create virtual environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Download Stanza Hebrew model:**
   ```bash
   python3 -c "import stanza; stanza.download('he')"
   ```

## Data Setup

Download the Hebrew News 2020 corpus (1M sentences):
- Source: [Wortschatz Leipzig Corpora](https://downloads.wortschatz-leipzig.de/corpora/heb_news_2020_1M.tar.gz)
- Extract to: `data/heb_news_2020_1M/`
- Required file: `heb_news_2020_1M-sentences.txt`

```bash
# Example extraction
cd data
wget https://downloads.wortschatz-leipzig.de/corpora/heb_news_2020_1M.tar.gz
tar -xzf heb_news_2020_1M.tar.gz
```

## Quick Start

### Basic Usage

Run the pipeline for a Hebrew lemma:

```bash
python3 src/main.py
```

By default, this extracts examples for `נקודה` (point). Results saved to `output/`.

### Configuration

Edit `src/main.py` to customize:

```python
# Target lemma
target_lemma = 'נקודה'  # Change to any Hebrew lemma

# Corpus settings
max_corpus_lines = 10000  # Use 10k for testing, 1M for production

# Clustering
n_clusters = 2  # Number of sense clusters

# Output
num_examples = 20  # Number of examples to generate
```

### Example Output

#### Understanding the Results

The pipeline generates two output files:
1. **TXT file** - Human-readable analysis with examples
2. **JSON file** - Structured data for programmatic use

#### Real Example: נקודה (point/dot)

When running on 10,000 sentences from Hebrew news corpus, the system found **25 sentences** containing the lemma `נקודה` and identified **2 distinct sense clusters**:

**Cluster 0 (Temporal/Metaphorical):** "point in time", "turning point"
- Top collocations: `בלבד` (only), `אנחנו` (we), `כדי` (in order to), `לסמן` (to mark), `בזמן` (in time)
- Example (Score: 0.92):
  > אבל בנקודה הזאת האלבום משתנה ומגלה את הפנים האמיתיות שלו.
  > 
  > *"But at this point the album changes and reveals its true face."*

**Cluster 1 (Argumentative/Abstract):** "the point is", "main point", abstract argument
- Top collocations: `אבל` (but), `עלייה` (rise), `הנמוכה` (lowest), `נאום` (speech)
- Example (Score: 0.86):
  > אבל האקלים הפוליטי בסין, והידרדרות היחסים עם ארה״ב, כנראה הגיעו לנקודה שבה כבר אין צורך במדיניות רשמית בנושא.
  > 
  > *"But the political climate in China, and deteriorating relations with the US, have apparently reached a point where there is no longer a need for official policy on the matter."*

#### How to Read the Output

**GDEX Scores (0.0-1.0):**
- **0.85-1.0**: Excellent examples - ideal length, complete sentences, clear context
- **0.70-0.84**: Good examples - usable but may have minor issues
- **Below 0.70**: Acceptable but may be fragments or too short

**Cluster IDs:**
- **0, 1, 2...**: Primary sense clusters (distinct usage patterns)
- **-1**: Overflow cluster (examples that don't fit main clusters clearly)

**Collocation Patterns** help validate sense distinction:
- **Cluster 0**: `בזמן` (in time), `לסמן` (to mark) → temporal usage
- **Cluster 1**: `עלייה` (rise), `הנמוכה` (lowest) → statistical/political discourse

**Full TXT Output Structure:**
```
============================================================
GDEX Results for: נקודה
============================================================

Corpus size: 10,000 sentences
Matching sentences: 25
Sense clusters: 2

============================================================
SENSE CLUSTERS
============================================================

Cluster 0: 5 sentences
Top collocations: [('בלבד', 2), ('אנחנו', 2), ('כדי', 1), ...]

Cluster 1: 5 sentences  
Top collocations: [('אבל', 2), ('עלייה', 1), ('הנמוכה', 1), ...]

============================================================
TOP CO-OCCURRING WORDS (across all clusters)
============================================================

  אבל: 13
  שבה: 4
  היא: 4
  ...

============================================================
TOP EXAMPLES (GDEX) - Ranked by quality score
============================================================

[Example 1] (Score: 0.92, Cluster: 0)
אבל בנקודה הזאת האלבום משתנה ומגלה את הפנים האמיתיות שלו.

[Example 2] (Score: 0.90, Cluster: 2)
אבל הנקודה היא שאנחנו לא צריכים לבנות עליו להיות אמבאפה...
```

**JSON format** includes the same data in structured form for programmatic processing.

## Project Structure

```
hebrew-gdex-extractor/
├── src/
│   ├── lemmatizer/           # Stanza-based Hebrew lemmatization
│   ├── sense_disambiguation/ # TF-IDF + K-means clustering
│   ├── collocations/         # Co-occurrence extraction
│   ├── example_generator/    # GDEX scoring
│   └── main.py               # Pipeline orchestration
├── data/                     # Corpus files (not in repo)
├── output/                   # Generated results (gitignored)
├── tests/                    # Unit tests
├── config/                   # Configuration files
├── requirements.txt          # Python dependencies
└── README.md
```

## How It Works

1. **Corpus Loading**: Load Hebrew sentences from corpus
2. **Lemmatization**: Use Stanza to find all forms of target lemma
3. **Sentence Extraction**: Filter sentences containing the lemma
4. **Sense Clustering**: Group sentences by usage context (TF-IDF + K-means)
5. **Collocation Analysis**: Extract typical context words for each sense
6. **GDEX Scoring**: Rank sentences by quality criteria
7. **Output**: Save top-scored examples with metadata

## Advanced Usage

### Programmatic API

```python
from src.lemmatizer.hebrew_lemmatizer import HebrewLemmatizer
from src.collocations.cooccurrence_extractor import CooccurrenceExtractor
from src.sense_disambiguation.wsd_handler import WsdHandler
from src.example_generator.gdex_scorer import GdexScorer

# Load corpus
with open('data/heb_news_2020_1M/heb_news_2020_1M-sentences.txt') as f:
    corpus = [line.strip().split('\t')[1].strip('"') for line in f if line.strip()]

# Initialize pipeline
lemmatizer = HebrewLemmatizer()
extractor = CooccurrenceExtractor('data/heb_news_2020_1M/heb_news_2020_1M-sentences.txt')
wsd = WsdHandler('data/heb_news_2020_1M/heb_news_2020_1M-sentences.txt')
scorer = GdexScorer(extractor, wsd)

# Extract examples for a lemma
target = 'שלום'
sentences = extractor.extract_sentences_with_lemma(target, corpus, lemmatizer, n_jobs=4)
clusters = wsd.disambiguate(target, sentences, n_clusters=2)
examples = scorer.generate_examples(target, sentences, top_n=10, diversity=True)

print(f"Found {len(sentences)} examples for '{target}'")
for i, ex in enumerate(examples, 1):
    print(f"{i}. [{ex['score']:.2f}] {ex['sentence']}")
```

## Performance

Processing time on 4-core Intel i5 (3.5 GHz):
- 10,000 sentences: ~6 seconds
- 100,000 sentences: ~1 minute
- 1,000,000 sentences: ~10 minutes

## Citation

If you use this library in academic work, please cite:

```bibtex
@software{hebrew_gdex_2025,
  title={Hebrew GDEX Extractor: Unsupervised Example Extraction},
  author={Ivrit Organization},
  year={2025},
  url={https://github.com/ivrit/hebrew-gdex-extractor}
}
```

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## Acknowledgments

- [Stanza NLP](https://stanfordnlp.github.io/stanza/) for Hebrew lemmatization
- [Universal Dependencies](https://universaldependencies.org/) for Hebrew treebanks
- [Wortschatz Leipzig](https://wortschatz.uni-leipzig.de/) for the Hebrew news corpus
- GDEX methodology by Kilgarriff et al. (2008)
