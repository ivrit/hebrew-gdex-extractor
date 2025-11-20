from typing import List, Dict, Tuple
from collections import Counter, defaultdict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import numpy as np


class WsdHandler:
    def __init__(self, corpus_path: str = None):
        """
        Initialize WSD handler with lightweight heuristics.
        
        :param corpus_path: Path to corpus file (optional, can set later)
        """
        self.corpus_path = corpus_path
        self.sense_dict = {}
        self.context_patterns = defaultdict(list)
        
    def disambiguate(self, lemma: str, sentences: List[str], 
                     n_clusters: int = 3, max_examples_per_cluster: int = 5) -> Dict[int, List[str]]:
        """
        Disambiguate word senses by clustering sentences containing the lemma.
        
        :param lemma: The lemma to disambiguate
        :param sentences: List of sentences containing the lemma
        :param n_clusters: Number of sense clusters to create
        :param max_examples_per_cluster: Maximum examples to return per cluster
        :return: Dictionary mapping cluster_id to list of example sentences
        """
        if len(sentences) < n_clusters:
            # Not enough data for clustering, return all sentences in one group
            return {0: sentences[:max_examples_per_cluster]}
        
        # Use TF-IDF vectorization for lightweight clustering
        vectorizer = TfidfVectorizer(max_features=100, ngram_range=(1, 2))
        try:
            X = vectorizer.fit_transform(sentences)
        except ValueError:
            # If vectorization fails, return all in one cluster
            return {0: sentences[:max_examples_per_cluster]}
        
        # Perform K-means clustering
        kmeans = KMeans(n_clusters=min(n_clusters, len(sentences)), random_state=42, n_init=10)
        cluster_labels = kmeans.fit_predict(X)
        
        # Group sentences by cluster
        clustered_sentences = defaultdict(list)
        for idx, label in enumerate(cluster_labels):
            clustered_sentences[label].append(sentences[idx])
        
        # Return top examples from each cluster
        result = {}
        for cluster_id, cluster_sentences in clustered_sentences.items():
            result[cluster_id] = cluster_sentences[:max_examples_per_cluster]
        
        return result

    def extract_collocational_patterns(self, lemma: str, sentences: List[str], 
                                       window: int = 2) -> Dict[str, int]:
        """
        Extract common words that appear near the target lemma.
        
        :param lemma: The target lemma
        :param sentences: Sentences containing the lemma
        :param window: Context window size (words before/after)
        :return: Dictionary of collocating words with their frequencies
        """
        collocations = Counter()
        
        for sentence in sentences:
            words = sentence.split()
            for i, word in enumerate(words):
                if lemma in word or word == lemma:
                    # Extract context window
                    start = max(0, i - window)
                    end = min(len(words), i + window + 1)
                    context = words[start:i] + words[i+1:end]
                    collocations.update(context)
        
        return dict(collocations.most_common(20))

    def generate_senses(self, lemma: str, sentences: List[str]) -> List[Dict]:
        """
        Generate sense representations based on clustering.
        
        :param lemma: The lemma to analyze
        :param sentences: Sentences containing the lemma
        :return: List of sense dictionaries with patterns and examples
        """
        # Cluster sentences into sense groups
        clusters = self.disambiguate(lemma, sentences)
        
        senses = []
        for cluster_id, examples in clusters.items():
            # Extract collocations for this cluster
            patterns = self.extract_collocational_patterns(lemma, examples)
            
            sense = {
                'sense_id': cluster_id,
                'examples': examples,
                'collocations': patterns,
                'count': len(examples)
            }
            senses.append(sense)
        
        self.sense_dict[lemma] = senses
        return senses

    def get_cooccurrence_patterns(self, lemma: str, sense_id: int = None) -> List[str]:
        """
        Get co-occurrence patterns for a specific sense of a lemma.
        
        :param lemma: The target lemma
        :param sense_id: Optional specific sense ID
        :return: List of co-occurring words
        """
        if lemma not in self.sense_dict:
            return []
        
        if sense_id is not None:
            for sense in self.sense_dict[lemma]:
                if sense['sense_id'] == sense_id:
                    return list(sense['collocations'].keys())
        else:
            # Return all collocations across all senses
            all_collocations = []
            for sense in self.sense_dict[lemma]:
                all_collocations.extend(sense['collocations'].keys())
            return list(set(all_collocations))
        
        return []

    def generate_examples(self, lemma: str, sense_id: int = None) -> List[str]:
        """
        Generate example usages for a lemma or specific sense.
        
        :param lemma: The target lemma
        :param sense_id: Optional specific sense ID
        :return: List of example sentences
        """
        if lemma not in self.sense_dict:
            return []
        
        if sense_id is not None:
            for sense in self.sense_dict[lemma]:
                if sense['sense_id'] == sense_id:
                    return sense['examples']
        else:
            # Return examples from all senses
            all_examples = []
            for sense in self.sense_dict[lemma]:
                all_examples.extend(sense['examples'])
            return all_examples
        
        return []