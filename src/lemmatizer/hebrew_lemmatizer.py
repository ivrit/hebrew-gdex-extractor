import stanza
from typing import List, Dict, Tuple
import torch


class HebrewLemmatizer:
    def __init__(self, download_model: bool = False):
        if download_model:
            stanza.download('he', verbose=False)
        
        torch.serialization.add_safe_globals([type(lambda: None)])
        
        self.nlp = stanza.Pipeline(
            'he', 
            processors='tokenize,pos,lemma',
            use_gpu=False,
            verbose=False
        )

    def lemmatize(self, word: str) -> str:
        doc = self.nlp(word)
        if doc.sentences and doc.sentences[0].words:
            return doc.sentences[0].words[0].lemma
        return word

    def lemmatize_sentence(self, sentence: str) -> List[Tuple[str, str]]:
        doc = self.nlp(sentence)
        result = []
        for sent in doc.sentences:
            for word in sent.words:
                result.append((word.text, word.lemma))
        return result

    def get_lemmas_only(self, sentence: str) -> List[str]:
        doc = self.nlp(sentence)
        lemmas = []
        for sent in doc.sentences:
            for word in sent.words:
                lemmas.append(word.lemma)
        return lemmas

    def get_lemma_info(self, lemma: str) -> Dict:
        return {
            'lemma': lemma,
            'senses': [],
            'frequency': 0,
            'examples': []
        }