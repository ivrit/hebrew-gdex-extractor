def load_config(config_file):
    import yaml
    with open(config_file, 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)
    return config

def preprocess_text(text):
    # TBD
    return text.strip()

def extract_lemma_from_word(word, lemmatizer):
    return lemmatizer.lemmatize(word)

def get_common_cooccurrences(lemma, cooccurrence_data):
    # Extract common co-occurrences for the given lemma
    return cooccurrence_data.get(lemma, [])

def format_example_usage(lemma, examples):
    return f"Examples for '{lemma}': " + ", ".join(examples)
