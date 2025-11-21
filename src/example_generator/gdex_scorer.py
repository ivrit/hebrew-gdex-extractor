from typing import List, Dict, Tuple
import re
from collections import Counter


class GdexScorer:
    def __init__(self, cooccurrence_extractor=None, wsd_handler=None):
        self.cooccurrence_extractor = cooccurrence_extractor
        self.wsd_handler = wsd_handler
        
        self.weights = {
            'length': 0.2,
            'complexity': 0.15,
            'completeness': 0.2,
            'common_words': 0.2,
            'informativeness': 0.25
        }

    def score_sentence(self, sentence: str, lemma: str, 
                      common_words: set = None) -> float:
        scores = {}
        
        words = sentence.split()
        word_count = len(words)
        if 10 <= word_count <= 25:
            scores['length'] = 1.0
        elif 7 <= word_count <= 30:
            scores['length'] = 0.7
        else:
            scores['length'] = 0.3
        
        avg_word_length = sum(len(w) for w in words) / max(len(words), 1)
        if 3 <= avg_word_length <= 6:
            scores['complexity'] = 1.0
        else:
            scores['complexity'] = 0.5
        
        if sentence.strip().endswith(('.', '!', '?', ':', ';')):
            scores['completeness'] = 1.0
        else:
            scores['completeness'] = 0.3
        
        if common_words:
            common_count = sum(1 for w in words if w in common_words)
            scores['common_words'] = min(common_count / max(len(words), 1), 1.0)
        else:
            scores['common_words'] = 0.7
        
        unique_words = len(set(words))
        if unique_words >= 0.6 * len(words) and len(words) >= 5:
            scores['informativeness'] = 1.0
        else:
            scores['informativeness'] = 0.5
        
        total_score = sum(scores[k] * self.weights[k] for k in self.weights)
        return total_score

    def score_examples(self, sentences: List[str], lemma: str) -> List[Tuple[str, float]]:
        all_words = []
        for sent in sentences:
            all_words.extend(sent.split())
        word_freq = Counter(all_words)
        common_words = {word for word, count in word_freq.items() if count >= 2}
        
        scored = []
        for sentence in sentences:
            score = self.score_sentence(sentence, lemma, common_words)
            scored.append((sentence, score))
        
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored

    def generate_examples(self, lemma: str, sentences: List[str], 
                         top_n: int = 10, diversity: bool = True) -> List[Dict]:
        scored_sentences = self.score_examples(sentences, lemma)
        
        if diversity and self.wsd_handler:
            sense_clusters = self.wsd_handler.disambiguate(lemma, sentences)
            
            examples = []
            for cluster_id, cluster_sentences in sense_clusters.items():
                cluster_scored = [(s, score) for s, score in scored_sentences 
                                 if s in cluster_sentences]
                
                n_per_cluster = max(1, top_n // len(sense_clusters))
                for sentence, score in cluster_scored[:n_per_cluster]:
                    examples.append({
                        'sentence': sentence,
                        'score': score,
                        'sense_cluster': cluster_id,
                        'lemma': lemma
                    })
            
            if len(examples) < top_n:
                remaining = [{'sentence': s, 'score': score, 'sense_cluster': -1, 'lemma': lemma}
                           for s, score in scored_sentences 
                           if s not in [ex['sentence'] for ex in examples]]
                examples.extend(remaining[:top_n - len(examples)])
        else:
            examples = [{'sentence': s, 'score': score, 'sense_cluster': 0, 'lemma': lemma}
                       for s, score in scored_sentences[:top_n]]
        
        return examples

    def filter_by_quality(self, sentences: List[str], lemma: str, 
                         min_score: float = 0.5) -> List[str]:
        scored = self.score_examples(sentences, lemma)
        return [sent for sent, score in scored if score >= min_score]
