import unittest
from src.sense_disambiguation.wsd_handler import WsdHandler


class TestWsdHandler(unittest.TestCase):

    def setUp(self):
        self.wsd = WsdHandler()

    def test_clustering_with_mixed_senses(self):
        sentences = [
            "הם זכו בנקודה במשחק האחרון",
            "הבקיעו גול וקיבלו נקודה נוספת",
            "זו נקודה מעניינת בדיון",
            "העלה נקודה חשובה בוויכוח",
            "הקבוצה צברה עוד נקודה בטבלה",
        ]
        clusters = self.wsd.disambiguate("נקודה", sentences, n_clusters=2)
        
        self.assertEqual(len(clusters), 2)
        total_sentences = sum(len(sents) for sents in clusters.values())
        self.assertGreater(total_sentences, 0)

    def test_auto_cluster_detection(self):
        sentences = [
            "הם זכו בנקודה במשחק האחרון",
            "הבקיעו גול וקיבלו נקודה נוספת",
            "זו נקודה מעניינת בדיון",
            "העלה נקודה חשובה בוויכוח",
            "הקבוצה צברה עוד נקודה בטבלה",
        ]
        clusters = self.wsd.disambiguate("נקודה", sentences)
        
        self.assertGreater(len(clusters), 0)
        total_sentences = sum(len(sents) for sents in clusters.values())
        self.assertGreater(total_sentences, 0)

    def test_clustering_too_few_sentences(self):
        sentences = ["נקודה אחת"]
        clusters = self.wsd.disambiguate("נקודה", sentences, n_clusters=3)
        
        self.assertEqual(len(clusters), 1)
        self.assertIn(0, clusters)

    def test_extract_collocations(self):
        sentences = [
            "הם זכו בנקודה במשחק",
            "הבקיעו עוד נקודה במשחק",
        ]
        patterns = self.wsd.extract_collocational_patterns("נקודה", sentences, window=2)
        
        self.assertIn("במשחק", patterns)
        self.assertGreater(patterns["במשחק"], 0)


if __name__ == '__main__':
    unittest.main()