# Data Directory

This directory is for corpus files used by the Hebrew GDEX extractor.

## Required Corpus

Download the Hebrew News 2020 corpus (1M sentences):
- Source: [Provide source link]
- Extract to: `data/heb_news_2020_1M/`
- Required file: `heb_news_2020_1M-sentences.txt`

## Directory Structure

```
data/
├── README.md                    # This file
├── corpus/                      # Optional: Place custom corpora here
│   └── sentences.txt            # Example corpus file
└── heb_news_2020_1M/           # Main corpus (not in git)
    └── heb_news_2020_1M-sentences.txt
```

## Format

Corpus files should be tab-separated:
```
<line_id><TAB>"<sentence_text>"
```

Example:
```
1	"זוהי משפט לדוגמה בעברית."
2	"משפט נוסף עם נקודה בסוף."
```

## Notes

- Large corpus files are excluded from git (see `.gitignore`)
- Users must download and place corpus files manually
- Sample corpora can be provided in `corpus/` subdirectory for testing
