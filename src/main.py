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
    corpus_path = os.path.join('data', 'heb_news_2020_1M', 'heb_news_2020_1M-sentences.txt')
    target_lemma = 'נקודה'
    max_corpus_lines = 50000
    
    cores = mp.cpu_count()
    n_jobs = max(1, cores - 1) if cores > 2 else 1
    
    print("\nHebrew GDEX - Dictionary Example Generation\n")
    
    lemmatizer = HebrewLemmatizer(download_model=False)
    cooccurrence_extractor = CooccurrenceExtractor(corpus_path)
    wsd_handler = WsdHandler(corpus_path)
    gdex_scorer = GdexScorer(cooccurrence_extractor, wsd_handler)
    
    print(f"Loading corpus (using {n_jobs} cores)...")
    if os.path.exists(corpus_path):
        sentences = cooccurrence_extractor.load_corpus(max_lines=max_corpus_lines)
    else:
        print("No corpus found - using sample sentences")
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
    print(f"Loaded {len(sentences):,} sentences\n")
    
    print(f"Finding sentences with '{target_lemma}'...")
    matching_sentences = cooccurrence_extractor.extract_sentences_with_lemma(
        target_lemma, sentences, lemmatizer, n_jobs=n_jobs
    )
    print(f"Found {len(matching_sentences)} matches\n")
    
    if not matching_sentences:
        print(f"No examples found for '{target_lemma}'")
        return
    
    print("Clustering by sense...")
    sense_clusters = wsd_handler.disambiguate(target_lemma, matching_sentences)
    print(f"Identified {len(sense_clusters)} clusters:")
    
    # Extract cluster-specific collocations with TF-IDF filtering
    cluster_collocations = wsd_handler.extract_cluster_specific_collocations(
        target_lemma, sense_clusters, window=4
    )
    
    for cluster_id, cluster_sents in sense_clusters.items():
        top_patterns = list(cluster_collocations[cluster_id].items())[:5]
        print(f"  Cluster {cluster_id}: {len(cluster_sents)} sentences - {top_patterns}")
    
    print("\nExtracting co-occurrences...")
    cooccurrences = cooccurrence_extractor.extract_cooccurrences(target_lemma, matching_sentences)
    top_cooccurrences = cooccurrence_extractor.get_top_cooccurrences(target_lemma, n=10)
    print("Top co-occurring words:")
    for word, count in top_cooccurrences:
        print(f"  {word}: {count}")
    
    print("\nGenerating examples...")
    num_examples = 20
    examples = gdex_scorer.generate_examples(
        target_lemma, 
        matching_sentences, 
        top_n=num_examples,
        diversity=True
    )
    
    print(f"\nTop {len(examples)} examples:\n")
    for i, example in enumerate(examples, 1):
        print(f"{i}. [score: {example['score']:.2f}, cluster: {example['sense_cluster']}]")
        print(f"   {example['sentence']}\n")
    
    print("Saving results...")
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(output_dir, f"gdex_results_{target_lemma}_{timestamp}.json")
    
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
    
    for cluster_id, cluster_sents in sense_clusters.items():
        patterns = cluster_collocations[cluster_id]
        results["clusters"][str(cluster_id)] = {
            "size": int(len(cluster_sents)),
            "top_collocations": {k: int(v) for k, v in list(patterns.items())[:10]}
        }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    text_file = os.path.join(output_dir, f"gdex_results_{target_lemma}_{timestamp}.txt")
    with open(text_file, 'w', encoding='utf-8') as f:
        f.write(f"תוצאות GDEX עבור: {target_lemma}\n")
        f.write(f"נוצר ב: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n")
        f.write("=" * 80 + "\n\n")
        
        f.write(f"גודל קורפוס: {len(sentences):,} משפטים\n")
        f.write(f"משפטים עם '{target_lemma}': {len(matching_sentences)}\n")
        f.write(f"מספר אשכולות משמעות: {len(sense_clusters)}\n\n")
        f.write("=" * 80 + "\n\n")
        
        for cluster_id, cluster_sents in sorted(sense_clusters.items()):
            patterns = cluster_collocations[cluster_id]
            top_collocations = ", ".join([f"{word} ({count})" for word, count in list(patterns.items())[:8]])
            
            f.write(f"אשכול {cluster_id}\n")
            f.write(f"גודל: {len(cluster_sents)} משפטים\n")
            f.write(f"קולוקציות: {top_collocations}\n")
            f.write("\nדוגמאות:\n\n")
            
            for i, sent in enumerate(cluster_sents[:5], 1):
                f.write(f"{i}. {sent}\n\n")
            
            if len(cluster_sents) > 5:
                f.write(f"(ועוד {len(cluster_sents) - 5} משפטים נוספים)\n")
            
            f.write("\n" + "-" * 80 + "\n\n")
        
        f.write("=" * 80 + "\n")
        f.write("מילים נפוצות לצד הלמה\n")
        f.write("=" * 80 + "\n\n")
        for word, count in top_cooccurrences:
            f.write(f"{word:20} {count}\n")
        
        f.write("\n" + "=" * 80 + "\n")
        f.write("דוגמאות מובילות (לפי ציון GDEX)\n")
        f.write("=" * 80 + "\n\n")
        
        for i, example in enumerate(examples, 1):
            f.write(f"[{i}] ציון: {example['score']:.2f} | אשכול: {example['sense_cluster']}\n")
            f.write(f"{example['sentence']}\n\n")
    
    print(f"Saved to {output_file}")
    print(f"        {text_file}\n")


if __name__ == "__main__":
    main()
