# Hebrew GDEX Extractor

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Automatically extract high-quality, sense-diverse dictionary examples for Hebrew words from large corpora.

This library uses **unsupervised clustering** to distinguish word senses and **multi-criteria GDEX scoring** to rank examples by quality, without requiring manually annotated sense inventories.

## Features

- ✅ **Neural lemmatization** using Stanza (handles Hebrew morphology)
- ✅ **Automatic cluster detection** via silhouette score (no manual k selection)
- ✅ **POS-filtered collocations** (content words only: nouns, verbs, adjectives, adverbs)
- ✅ **TF-IDF cluster-specific collocation extraction** (filters out cross-cluster noise)
- ✅ **Multi-criteria GDEX scoring** (length, completeness, typicality, informativeness)
- ✅ **Parallel processing** with dynamic CPU allocation
- ✅ **JSON + TXT output** with Hebrew-formatted results

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
max_corpus_lines = 50000  # Adjust based on needs

# Window size for collocations
window = 4  # Words before/after target (in WsdHandler)

# Output
num_examples = 20  # Number of examples to generate
```

Note: Cluster number (k) is automatically determined using silhouette score.

### Example Output

#### Understanding the Results

The pipeline generates two output files:
1. **TXT file** - Human-readable analysis with examples
2. **JSON file** - Structured data for programmatic use

#### Real Example: נקודה (point/dot)

When running on 50,000 sentences from Hebrew news corpus, the system found **102 sentences** containing the lemma `נקודה` and **automatically detected 8 distinct sense clusters** using silhouette score:

**Cluster 0 (Geographic/Strategic):** "strategic point", locations
- Cluster-specific collocations: `כנראה`, `אסטרטגי`, `ישראל`, `תל`, `אביב`
- Example:
  > אז נכון שאת האפקט הנורא של הקרינה אין שם, אבל זה מפוזר על ראשי נפץ מדויקים של כ-200 אלף טילים שיודעים להגיע לכל נקודה אסטרטגית בישראל.

**Cluster 1 (Sports/Competition):** "point" in games/scores
- Cluster-specific collocations: `ויתר`, `יובנטוס`, `יתרון`, `לאציו`
- Example:
  > אבל העונה הופסקה הליגה אחרי 26 מחזורים כשליובנטוס יתרון של נקודה בלבד על לאציו.

**Cluster 2 (Time/Decision):** "point in time", critical moments
- Cluster-specific collocations: `untitled`, `סימן`, `זמן`, `אלבום`, `החלטה`
- Example:
  > אבל בנקודה הזאת האלבום משתנה ומגלה את הפנים האמיתיות שלו.

#### How to Read the Output

**GDEX Scores (0.0-1.0):**
- **0.85-1.0**: Excellent examples - ideal length, complete sentences, clear context
- **0.70-0.84**: Good examples - usable but may have minor issues
- **Below 0.70**: Acceptable but may be fragments or too short

**Cluster IDs:**
- **0, 1, 2...**: Primary sense clusters (distinct usage patterns)
- **-1**: Overflow cluster (examples that don't fit main clusters clearly)

**Collocation Patterns** help validate sense distinction:
- Uses **POS filtering** to show only content words (NOUN, PROPN, VERB, ADJ, ADV)
- **TF-IDF filtering** removes words common across all clusters
- Shows cluster-specific collocations (>50% of occurrences in that cluster)

**Full TXT Output Structure:**
```
תוצאות GDEX עבור: נקודה
נוצר ב: 21/11/2025 11:15
================================================================================

גודל קורפוס: 50,000 משפטים
משפטים עם 'נקודה': 102
מספר אשכולות משמעות: 8

================================================================================

אשכול 0
גודל: 5 משפטים
קולוקציות: כנראה (1), עבד (1), אין (1), כסף (1), אסטרטגי (1)

דוגמאות:
1. אז נכון שאת האפקט הנורא של הקרינה אין שם, אבל זה מפוזר על ראשי נפץ מדויקים של כ-200 אלף טילים שיודעים להגיע לכל **נקודה** אסטרטגית בישראל.
2. אז הגענו ל**נקודה** שבה אנחנו מתמקחים על היקף החלת הריבונות.
...
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
4. **Automatic Clustering**: Determine optimal k using silhouette score, then apply K-means
5. **POS-filtered Collocations**: Extract content words (4-word window) for each cluster
6. **TF-IDF Cluster Filtering**: Keep only cluster-specific collocations
7. **GDEX Scoring**: Rank sentences by quality criteria
8. **Output**: Save top-scored examples with Hebrew formatting

## Advanced Usage

### Programmatic API

```python
from src.lemmatizer.hebrew_lemmatizer import HebrewLemmatizer
from src.collocations.cooccurrence_extractor import CooccurrenceExtractor
from src.sense_disambiguation.wsd_handler import WsdHandler
from src.example_generator.gdex_scorer import GdexScorer

# Load corpus into memory
with open('data/heb_news_2020_1M/heb_news_2020_1M-sentences.txt') as f:
    corpus = [line.strip().split('\t')[1].strip('"') for line in f if line.strip()]

# Initialize components (no file paths needed)
lemmatizer = HebrewLemmatizer()
extractor = CooccurrenceExtractor()
wsd = WsdHandler()
scorer = GdexScorer(extractor, wsd)

# Extract examples for a lemma
target = 'שלום'
sentences = extractor.extract_sentences_with_lemma(target, corpus, lemmatizer, n_jobs=4)
clusters = wsd.disambiguate(target, sentences)  # Auto-detects k
cluster_collocations = wsd.extract_cluster_specific_collocations(target, clusters, window=4)
examples = scorer.generate_examples(target, sentences, top_n=10, diversity=True)

print(f"Found {len(sentences)} examples for '{target}' in {len(clusters)} clusters")
for i, ex in enumerate(examples, 1):
    print(f"{i}. [{ex['score']:.2f}] (Cluster: {ex['sense_cluster']}) {ex['sentence']}")
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
  author={Noam Ordan},
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

## References

```bibtex
@inproceedings{kilgarriff2008gdex,
  title={GDEX: Automatically finding good dictionary examples in a corpus},
  author={Kilgarriff, Adam and Hus{\'a}k, Milos and McAdam, Katy and Rundell, Michael and Rychl{\`y}, Pavel},
  booktitle={Proceedings of the XIII EURALEX international congress},
  volume={1},
  pages={425--432},
  year={2008},
  organization={Universitat Pompeu Fabra Barcelona}
}
