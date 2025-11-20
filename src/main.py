from lemmatizer.hebrew_lemmatizer import HebrewLemmatizer
from sense_disambiguation.wsd_handler import WsdHandler
from collocations.cooccurrence_extractor import CooccurrenceExtractor
from example_generator.gdex_scorer import GdexScorer
import os
import multiprocessing as mp
from tqdm import tqdm
import json
from datetime import datetime


def main():
    """
    Main pipeline for generating good dictionary examples (GDEX) for Hebrew lemmas.
    """
    # Configuration
    corpus_path = os.path.join('data', 'heb_news_2020_1M', 'heb_news_2020_1M-sentences.txt')
    target_lemma = 'נקודה'  # Example: can mean "point" (argument) or "point" (score)
    max_corpus_lines = 10000  # Load first 10k sentences for faster testing
    n_jobs = min(4, mp.cpu_count())  # Use up to 4 cores
    
    print("=" * 60)
    print("Hebrew GDEX Library - Example Generation Pipeline")
    print("=" * 60)
    
    # Step 1: Initialize components
    print("\n[1] Initializing components...")
    lemmatizer = HebrewLemmatizer(download_model=False)
    cooccurrence_extractor = CooccurrenceExtractor(corpus_path)
    wsd_handler = WsdHandler(corpus_path)
    gdex_scorer = GdexScorer(cooccurrence_extractor, wsd_handler)
    print("✓ Components initialized")
    
    # Step 2: Load and prepare corpus
    print(f"\n[2] Loading corpus (max {max_corpus_lines:,} sentences)...")
    print(f"   Using {n_jobs} parallel jobs")
    # For demo purposes, use sample sentences if corpus file doesn't exist
    if os.path.exists(corpus_path):
        sentences = cooccurrence_extractor.load_corpus(max_lines=max_corpus_lines)
    else:
        print("   (Using sample sentences - no corpus file found)")
        sentences = [
            "העלה נקודה מאוד מעניינת בוויכוח הזה על העתיד של החינוך.",
            "הם שברו שיוויון בדקה התשעים שהבקיעו עוד גול וזכו בנקודה נוספת.",
            "נקודה חשובה שצריך לזכור היא שהחינוך משתנה עם הזמן.",
            "הקבוצה צברה נקודה בלבד במשחק האחרון נגד היריבה.",
            "זו נקודה מעניינת שראוי להעלות בדיון הבא.",
            "הם הפסידו נקודה חשובה במאבק על המקום הראשון.",
            "נקודה נוספת לדיון היא השפעת הטכנולוגיה על החברה.",
            "הבקיעו גול וקיבלו נקודה אחת בטבלה.",
        ]
    print(f"✓ Loaded {len(sentences):,} sentences")
    
    # Step 3: Extract sentences containing the target lemma
    print(f"\n[3] Extracting sentences with lemma '{target_lemma}'...")
    matching_sentences = cooccurrence_extractor.extract_sentences_with_lemma(
        target_lemma, sentences, lemmatizer, n_jobs=n_jobs
    )
    print(f"✓ Found {len(matching_sentences)} sentences")
    
    if not matching_sentences:
        print(f"\n⚠ No sentences found for lemma '{target_lemma}'")
        return
    
    # Step 4: Perform sense disambiguation (clustering)
    print(f"\n[4] Performing sense disambiguation...")
    sense_clusters = wsd_handler.disambiguate(target_lemma, matching_sentences, n_clusters=2)
    print(f"✓ Identified {len(sense_clusters)} sense clusters:")
    for cluster_id, cluster_sents in sense_clusters.items():
        print(f"   Cluster {cluster_id}: {len(cluster_sents)} sentences")
        # Show sample collocations
        patterns = wsd_handler.extract_collocational_patterns(target_lemma, cluster_sents, window=2)
        top_patterns = list(patterns.items())[:5]
        print(f"   Top collocations: {top_patterns}")
    
    # Step 5: Extract co-occurrences
    print(f"\n[5] Extracting co-occurrences...")
    cooccurrences = cooccurrence_extractor.extract_cooccurrences(target_lemma, matching_sentences)
    top_cooccurrences = cooccurrence_extractor.get_top_cooccurrences(target_lemma, n=10)
    print(f"✓ Top 10 co-occurring words:")
    for word, count in top_cooccurrences:
        print(f"   {word}: {count}")
    
    # Step 6: Generate and score examples
    print(f"\n[6] Generating GDEX examples...")
    num_examples = 20  # Increased from 5 to 20
    examples = gdex_scorer.generate_examples(
        target_lemma, 
        matching_sentences, 
        top_n=num_examples,
        diversity=True
    )
    
    print(f"✓ Top {len(examples)} examples:")
    print("\n" + "=" * 60)
    for i, example in enumerate(examples, 1):
        print(f"\n[Example {i}] (Score: {example['score']:.2f}, Cluster: {example['sense_cluster']})")
        print(f"  {example['sentence']}")
    
    # Step 7: Save results to file
    print("\n" + "=" * 60)
    print("\n[7] Saving results to file...")
    
    # Create output directory if it doesn't exist
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(output_dir, f"gdex_results_{target_lemma}_{timestamp}.json")
    
    # Prepare results data
    results = {
        "lemma": target_lemma,
        "timestamp": timestamp,
        "corpus_size": int(len(sentences)),
        "matching_sentences_count": int(len(matching_sentences)),
        "n_clusters": int(len(sense_clusters)),
        "clusters": {},
        "top_cooccurrences": {k: int(v) for k, v in top_cooccurrences},
        "examples": [
            {
                "sentence": ex["sentence"],
                "score": float(ex["score"]),
                "sense_cluster": int(ex["sense_cluster"]),
                "lemma": ex["lemma"]
            }
            for ex in examples
        ]
    }
    
    # Add cluster information
    for cluster_id, cluster_sents in sense_clusters.items():
        patterns = wsd_handler.extract_collocational_patterns(target_lemma, cluster_sents, window=2)
        results["clusters"][str(cluster_id)] = {
            "size": int(len(cluster_sents)),
            "top_collocations": {k: int(v) for k, v in list(patterns.items())[:10]}
        }
    
    # Save to JSON
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"✓ Results saved to: {output_file}")
    
    # Also save a readable text version
    text_file = os.path.join(output_dir, f"gdex_results_{target_lemma}_{timestamp}.txt")
    with open(text_file, 'w', encoding='utf-8') as f:
        f.write("=" * 60 + "\n")
        f.write(f"GDEX Results for: {target_lemma}\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 60 + "\n\n")
        
        f.write(f"Corpus size: {len(sentences):,} sentences\n")
        f.write(f"Matching sentences: {len(matching_sentences)}\n")
        f.write(f"Sense clusters: {len(sense_clusters)}\n\n")
        
        f.write("=" * 60 + "\n")
        f.write("SENSE CLUSTERS\n")
        f.write("=" * 60 + "\n\n")
        for cluster_id, cluster_sents in sense_clusters.items():
            f.write(f"Cluster {cluster_id}: {len(cluster_sents)} sentences\n")
            patterns = wsd_handler.extract_collocational_patterns(target_lemma, cluster_sents, window=2)
            f.write(f"Top collocations: {list(patterns.items())[:10]}\n\n")
        
        f.write("=" * 60 + "\n")
        f.write("TOP CO-OCCURRING WORDS\n")
        f.write("=" * 60 + "\n\n")
        for word, count in top_cooccurrences:
            f.write(f"  {word}: {count}\n")
        
        f.write("\n" + "=" * 60 + "\n")
        f.write("TOP EXAMPLES (GDEX)\n")
        f.write("=" * 60 + "\n\n")
        for i, example in enumerate(examples, 1):
            f.write(f"[Example {i}] (Score: {example['score']:.2f}, Cluster: {example['sense_cluster']})\n")
            f.write(f"{example['sentence']}\n\n")
    
    print(f"✓ Text version saved to: {text_file}")
    
    print("\n" + "=" * 60)
    print("Pipeline completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()