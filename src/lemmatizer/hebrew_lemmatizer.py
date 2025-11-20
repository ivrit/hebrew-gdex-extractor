import stanza
from typing import List, Dict, Tuple
import torch


class HebrewLemmatizer:
    def __init__(self, download_model: bool = False):
        """
        Initialize Hebrew lemmatizer with Stanza.
        
        :param download_model: Whether to download the Hebrew model if not present.
        """
        if download_model:
            stanza.download('he', verbose=False)
        
        # Disable weights_only mode for compatibility with older Stanza models
        torch.serialization.add_safe_globals([type(lambda: None)])
        
        # Initialize pipeline with just tokenization and lemmatization for efficiency
        self.nlp = stanza.Pipeline(
            'he', 
            processors='tokenize,pos,lemma',
            use_gpu=False,
            verbose=False,
            download_method=None  # Don't auto-download
        )

    def lemmatize(self, word: str) -> str:
        """
        Lemmatizes a given Hebrew word and returns its lemma.
        
        :param word: A Hebrew word to be lemmatized.
        :return: The lemma of the given word.
        """
        doc = self.nlp(word)
        if doc.sentences and doc.sentences[0].words:
            return doc.sentences[0].words[0].lemma
        return word

    def lemmatize_sentence(self, sentence: str) -> List[Tuple[str, str]]:
        """
        Lemmatizes all words in a given Hebrew sentence and returns a list of (word, lemma) tuples.
        
        :param sentence: A Hebrew sentence to be lemmatized.
        :return: A list of (word, lemma) tuples for the words in the sentence.
        """
        doc = self.nlp(sentence)
        result = []
        for sent in doc.sentences:
            for word in sent.words:
                result.append((word.text, word.lemma))
        return result

    def get_lemmas_only(self, sentence: str) -> List[str]:
        """
        Returns just the lemmas from a sentence.
        
        :param sentence: A Hebrew sentence to be lemmatized.
        :return: A list of lemmas.
        """
        doc = self.nlp(sentence)
        lemmas = []
        for sent in doc.sentences:
            for word in sent.words:
                lemmas.append(word.lemma)
        return lemmas

    def get_lemma_info(self, lemma: str) -> Dict:
        """
        Retrieves information about a given lemma, such as its senses and usage examples.
        This is a placeholder for future corpus-based statistics.
        
        :param lemma: A lemma for which to retrieve information.
        :return: A dictionary containing information about the lemma.
        """
        return {
            'lemma': lemma,
            'senses': [],  # To be populated from corpus analysis
            'frequency': 0,  # To be calculated from corpus
            'examples': []  # To be extracted from corpus
        }