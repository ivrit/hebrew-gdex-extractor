from typing import List, Dict, Tuple
from collections import Counter, defaultdict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import numpy as np
import stanza


ALLOWED_POS = {'NOUN', 'PROPN', 'VERB', 'ADJ', 'ADV'}


class WsdHandler:
    def __init__(self, corpus_path: str = None):
        self.corpus_path = corpus_path
        self.sense_dict = {}
        self.context_patterns = defaultdict(list)
        self.nlp = None
        
    def disambiguate(self, lemma: str, sentences: List[str], 
                     n_clusters: int = None, max_examples_per_cluster: int = 5) -> Dict[int, List[str]]:
        if len(sentences) < 3:
            return {0: sentences[:max_examples_per_cluster]}
        
        vectorizer = TfidfVectorizer(max_features=100, ngram_range=(1, 2))
        try:
            X = vectorizer.fit_transform(sentences)
        except ValueError:
            return {0: sentences[:max_examples_per_cluster]}
        
        if n_clusters is None:
            n_clusters = self._find_optimal_clusters(X, sentences)
        else:
            n_clusters = min(n_clusters, len(sentences))
        
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        cluster_labels = kmeans.fit_predict(X)
        
        clustered_sentences = defaultdict(list)
        for idx, label in enumerate(cluster_labels):
            clustered_sentences[label].append(sentences[idx])
        
        result = {}
        for cluster_id, cluster_sentences in clustered_sentences.items():
            result[cluster_id] = cluster_sentences[:max_examples_per_cluster]
        
        return result
    
    def _find_optimal_clusters(self, X, sentences: List[str]) -> int:
        n = len(sentences)
        max_k = min(8, n // 3)
        
        if max_k < 2:
            return 1
        
        best_k = 2
        best_score = -1
        
        for k in range(2, max_k + 1):
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            labels = kmeans.fit_predict(X)
            score = silhouette_score(X, labels)
            
            if score > best_score:
                best_score = score
                best_k = k
        
        return best_k

    def extract_collocational_patterns(self, lemma: str, sentences: List[str], 
                                       window: int = 4) -> Dict[str, int]:
        if self.nlp is None:
            import torch
            torch.serialization.add_safe_globals([type(lambda: None)])
            self.nlp = stanza.Pipeline('he', processors='tokenize,pos,lemma', 
                                      use_gpu=False, verbose=False)
        
        collocations = Counter()
        
        for sentence in sentences:
            doc = self.nlp(sentence)
            for sent in doc.sentences:
                target_indices = []
                for i, word in enumerate(sent.words):
                    if word.lemma == lemma or word.text == lemma:
                        target_indices.append(i)
                
                for target_idx in target_indices:
                    for i, word in enumerate(sent.words):
                        if i == target_idx:
                            continue
                        
                        if abs(i - target_idx) <= window:
                            if word.upos in ALLOWED_POS:
                                collocations[word.lemma] += 1
        
        return dict(collocations.most_common(20))

    def extract_cluster_specific_collocations(self, lemma: str, 
                                             all_clusters: Dict[int, List[str]], 
                                             window: int = 4) -> Dict[int, Dict[str, int]]:
        cluster_collocations = {}
        all_collocations = defaultdict(lambda: defaultdict(int))
        
        for cluster_id, sentences in all_clusters.items():
            collocations = self.extract_collocational_patterns(lemma, sentences, window=window)
            cluster_collocations[cluster_id] = collocations
            for word, count in collocations.items():
                all_collocations[word][cluster_id] = count
        
        filtered_results = {}
        for cluster_id, collocations in cluster_collocations.items():
            filtered = {}
            for word, count in collocations.items():
                cluster_count = all_collocations[word][cluster_id]
                total_clusters = len(all_collocations[word])
                
                if total_clusters == 1 or cluster_count / sum(all_collocations[word].values()) > 0.5:
                    filtered[word] = count
            
            filtered_results[cluster_id] = dict(sorted(filtered.items(), 
                                                       key=lambda x: x[1], 
                                                       reverse=True)[:10])
        
        return filtered_results

    def generate_senses(self, lemma: str, sentences: List[str]) -> List[Dict]:
        clusters = self.disambiguate(lemma, sentences)
        
        senses = []
        for cluster_id, examples in clusters.items():
            patterns = self.extract_collocational_patterns(lemma, examples, window=4)
            
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
        if lemma not in self.sense_dict:
            return []
        
        if sense_id is not None:
            for sense in self.sense_dict[lemma]:
                if sense['sense_id'] == sense_id:
                    return list(sense['collocations'].keys())
        else:
            all_collocations = []
            for sense in self.sense_dict[lemma]:
                all_collocations.extend(sense['collocations'].keys())
            return list(set(all_collocations))
        
        return []

    def generate_examples(self, lemma: str, sense_id: int = None) -> List[str]:
        if lemma not in self.sense_dict:
            return []
        
        if sense_id is not None:
            for sense in self.sense_dict[lemma]:
                if sense['sense_id'] == sense_id:
                    return sense['examples']
        else:
            all_examples = []
            for sense in self.sense_dict[lemma]:
                all_examples.extend(sense['examples'])
            return all_examples
        
        return []