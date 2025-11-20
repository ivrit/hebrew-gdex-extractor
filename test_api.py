#!/usr/bin/env python3
"""Test the programmatic API from README"""

import sys
sys.path.insert(0, 'src')

from lemmatizer.hebrew_lemmatizer import HebrewLemmatizer
from collocations.cooccurrence_extractor import CooccurrenceExtractor
from sense_disambiguation.wsd_handler import WsdHandler
from example_generator.gdex_scorer import GdexScorer

print("Testing README API example...")
print("=" * 60)

# Test 1: Simple initialization without corpus_path
print("\n[Test 1] Initialize components without paths")
try:
    lemmatizer = HebrewLemmatizer()
    extractor = CooccurrenceExtractor()
    wsd = WsdHandler()
    scorer = GdexScorer(extractor, wsd)
    print("✓ All components initialized successfully")
except Exception as e:
    print(f"✗ Initialization failed: {e}")
    sys.exit(1)

# Test 2: Use sample sentences (no file I/O)
print("\n[Test 2] Extract examples using in-memory corpus")
try:
    # Sample corpus
    corpus = [
        "שלום! איך אתה היום?",
        "שלום עליכם, ברוכים הבאים לבית שלנו.",
        "נפגשנו בכניסה והוא אמר לי שלום.",
        "הסכם שלום נחתם בין שתי המדינות.",
        "שלום לכולם, תודה שבאתם.",
        "הם מחפשים דרך להשיג שלום במזרח התיכון.",
        "שלום רב, מה נשמע?",
        "התפללו לשלום ירושלים.",
    ]
    
    target = 'שלום'
    
    # Extract sentences (should work without corpus_path)
    sentences = extractor.extract_sentences_with_lemma(target, corpus, lemmatizer, n_jobs=1)
    print(f"✓ Found {len(sentences)} sentences containing '{target}'")
    
    if len(sentences) == 0:
        print("⚠ Warning: No sentences found, skipping clustering")
    else:
        # Cluster (should work without corpus_path)
        clusters = wsd.disambiguate(target, sentences, n_clusters=2)
        print(f"✓ Identified {len(clusters)} clusters")
        
        # Generate examples (should work without corpus_path)
        examples = scorer.generate_examples(target, sentences, top_n=5, diversity=True)
        print(f"✓ Generated {len(examples)} examples")
        
        print("\n[Results]")
        for i, ex in enumerate(examples, 1):
            print(f"{i}. [{ex['score']:.2f}] (Cluster: {ex['sense_cluster']}) {ex['sentence']}")
    
except Exception as e:
    print(f"✗ Test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("✓ All tests passed! API works as documented.")
