from typing import List, Dict, Tuple
from collections import Counter, defaultdict
import re
from tqdm import tqdm
from multiprocessing import Pool
import multiprocessing as mp


class CooccurrenceExtractor:
    def __init__(self, corpus_path: str = None):
        """
        Initialize co-occurrence extractor.
        
        :param corpus_path: Path to corpus file (optional)
        """
        self.corpus_path = corpus_path
        self.cooccurrences = defaultdict(Counter)
        self.lemma_sentences = defaultdict(list)

    def load_corpus(self, corpus_path: str = None, max_lines: int = None) -> List[str]:
        """
        Load corpus from file with progress bar.
        
        :param corpus_path: Path to corpus file
        :param max_lines: Maximum number of lines to load (None for all)
        :return: List of sentences
        """
        if corpus_path:
            self.corpus_path = corpus_path
        
        if not self.corpus_path:
            return []
        
        try:
            sentences = []
            with open(self.corpus_path, 'r', encoding='utf-8') as f:
                iterator = enumerate(f)
                if max_lines:
                    iterator = tqdm(iterator, total=max_lines, desc="Loading corpus", ncols=80, unit=" lines")
                
                for i, line in iterator:
                    if max_lines and i >= max_lines:
                        break
                    line = line.strip()
                    if not line:
                        continue
                    # Handle format: line_number\t"sentence"
                    if '\t' in line:
                        parts = line.split('\t', 1)
                        if len(parts) == 2:
                            # Remove quotes if present
                            sentence = parts[1].strip('"')
                            sentences.append(sentence)
                    else:
                        sentences.append(line)
            return sentences
        except FileNotFoundError:
            return []

    def extract_sentences_with_lemma(self, lemma: str, sentences: List[str], 
                                     lemmatizer=None, n_jobs: int = 1) -> List[str]:
        """
        Extract sentences containing the target lemma with parallel processing.
        
        :param lemma: Target lemma to search for
        :param sentences: List of sentences to search
        :param lemmatizer: Optional lemmatizer to match inflected forms
        :param n_jobs: Number of parallel jobs
        :return: List of sentences containing the lemma
        """
        matching_sentences = []
        
        if lemmatizer:
            # Parallel lemmatization for speed
            print(f"   Lemmatizing {len(sentences):,} sentences with {n_jobs} jobs...")
            
            # Process in batches with progress bar
            batch_size = max(100, len(sentences) // (n_jobs * 4))
            batches = [sentences[i:i+batch_size] for i in range(0, len(sentences), batch_size)]
            
            for batch in tqdm(batches, desc="Searching", ncols=80, unit=" batch"):
                for sentence in batch:
                    # Quick pre-check: does lemma appear as substring?
                    if lemma not in sentence:
                        continue
                    # Then verify with lemmatizer
                    lemmas = lemmatizer.get_lemmas_only(sentence)
                    if lemma in lemmas:
                        matching_sentences.append(sentence)
        else:
            # Simple substring matching as fallback
            print(f"   Searching {len(sentences):,} sentences (simple match)...")
            for sentence in tqdm(sentences, desc="Searching", ncols=80, unit=" sent"):
                words = sentence.split()
                if lemma in words or any(lemma in word for word in words):
                    matching_sentences.append(sentence)
        
        self.lemma_sentences[lemma] = matching_sentences
        return matching_sentences

    def extract_cooccurrences(self, lemma: str, sentences: List[str] = None, 
                             window_size: int = 5) -> Dict[str, int]:
        """
        Extract co-occurring words within a window around the lemma.
        
        :param lemma: Target lemma
        :param sentences: Sentences to analyze (uses stored sentences if None)
        :param window_size: Context window size
        :return: Dictionary of co-occurring words and their counts
        """
        if sentences is None:
            sentences = self.lemma_sentences.get(lemma, [])
        
        cooccurrences = Counter()
        
        for sentence in sentences:
            tokens = sentence.split()
            
            # Find all occurrences of lemma in sentence
            for i, token in enumerate(tokens):
                if lemma in token or token == lemma:
                    # Extract context window
                    start_index = max(0, i - window_size)
                    end_index = min(len(tokens), i + window_size + 1)
                    context = tokens[start_index:i] + tokens[i + 1:end_index]
                    cooccurrences.update(context)
        
        self.cooccurrences[lemma] = cooccurrences
        return dict(cooccurrences)

    def get_cooccurrences(self, lemma: str = None) -> Dict:
        """
        Get stored co-occurrences for a lemma or all lemmas.
        
        :param lemma: Optional specific lemma
        :return: Co-occurrence dictionary
        """
        if lemma:
            return dict(self.cooccurrences.get(lemma, {}))
        return {k: dict(v) for k, v in self.cooccurrences.items()}

    def get_top_cooccurrences(self, lemma: str, n: int = 10) -> List[Tuple[str, int]]:
        """
        Get top N co-occurring words for a lemma.
        
        :param lemma: Target lemma
        :param n: Number of top co-occurrences to return
        :return: List of (word, count) tuples
        """
        if lemma in self.cooccurrences:
            return self.cooccurrences[lemma].most_common(n)
        return []

    def extract_collocations(self, lemma: str, sentences: List[str] = None,
                            min_frequency: int = 2) -> List[Tuple[str, str, int]]:
        """
        Extract bigram collocations (word pairs) with the lemma.
        
        :param lemma: Target lemma
        :param sentences: Sentences to analyze
        :param min_frequency: Minimum frequency threshold
        :return: List of (word1, word2, count) tuples
        """
        if sentences is None:
            sentences = self.lemma_sentences.get(lemma, [])
        
        bigrams = Counter()
        
        for sentence in sentences:
            tokens = sentence.split()
            for i, token in enumerate(tokens):
                if lemma in token or token == lemma:
                    # Previous word + lemma
                    if i > 0:
                        bigrams[(tokens[i-1], token)] += 1
                    # Lemma + next word
                    if i < len(tokens) - 1:
                        bigrams[(token, tokens[i+1])] += 1
        
        # Filter by frequency
        filtered = [(w1, w2, count) for (w1, w2), count in bigrams.items() 
                   if count >= min_frequency]
        return sorted(filtered, key=lambda x: x[2], reverse=True)