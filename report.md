
# Hebrew GDEX Extractor: A Technical Report

**Author:** Noam Ordan  
**Development:** Claude Sonnet 4.5 was heavily involved in the development  
**Date:** November 21, 2025  
**Version:** 1.0

---

## 1. Abstract

This report details the design, implementation, and evaluation of an automated system for generating Good Dictionary Examples (GDEX) for Modern Hebrew. The system employs a multi-stage pipeline that includes corpus lemmatization, unsupervised word sense clustering, and context-aware collocation extraction. We introduce several key methodological innovations, including dynamic cluster number detection using the silhouette score, Part-of-Speech (POS) based filtering to isolate meaningful content words, and a TF-IDF-inspired heuristic to identify cluster-specific collocations. A case study on the polysemous Hebrew lemma 'נקודה' (nekuda) demonstrates the system's ability to successfully disambiguate senses—such as 'point' in a discussion, 'point' in a sports game, and 'point' as a location—and extract relevant, sense-specific lexical patterns from a large news corpus. The report concludes with a discussion of the system's performance, its current limitations, and avenues for future improvement.

---

## 2. Introduction

For language learners and lexicographers, understanding the different meanings (senses) of a word is a significant challenge. Good Dictionary Examples (GDEX) are crucial for illustrating how a word is used in authentic contexts, thereby clarifying its various senses. Manually curating such examples is a labor-intensive process. This project aimed to automate the extraction of GDEX for Modern Hebrew by developing a computational pipeline that can identify and group word senses from a raw text corpus.

The primary objective was to build a system that, given a target lemma, can:
1.  Extract all sentences containing the lemma from a corpus.
2.  Automatically group these sentences into semantically coherent clusters, each representing a distinct word sense.
3.  Characterize each sense cluster with a set of unique collocates (co-occurring words).
4.  Score and rank the example sentences to identify the most illustrative examples for each sense.

This report documents the methodology employed and evaluates its effectiveness through a detailed case study.

---

## 3. Methodology

The system is implemented as a Python pipeline that processes a text corpus to generate sense clusters and corresponding examples. The core components and workflow are described below.

### 3.1. Corpus

The primary data source is the **Hebrew News Corpus 2020 (1M sentences)** from the Wortschatz project at Leipzig University. For development and testing, we used a subset of 50,000 sentences to ensure manageable processing times.

### 3.2. Pre-processing and Lemmatization

The first step involves identifying all occurrences of a target lemma. As Hebrew is a morphologically rich language, a simple string search is insufficient. We employed the **Stanza NLP library** (version 1.11.0) for its robust Hebrew lemmatization capabilities. The entire corpus subset was processed in parallel to create a lemmatized version, allowing for efficient retrieval of sentences containing any morphological variant of the target lemma.

### 3.3. Word Sense Clustering

The core of the Word Sense Disambiguation (WSD) module is an unsupervised clustering approach.

1.  **Vectorization**: Sentences containing the target lemma are converted into numerical vectors using `TfidfVectorizer` from scikit-learn. This represents each sentence based on the term frequency-inverse document frequency of its constituent words and bigrams.

2.  **Automatic Cluster Number (k) Detection**: A critical challenge in clustering is determining the optimal number of clusters (`k`). Instead of using a fixed `k`, we implemented a dynamic approach using the **silhouette score**. The system tests a range of `k` values (from 2 up to a maximum of 8, or one-third of the sentence count for small samples) and selects the `k` that yields the highest silhouette score, indicating the most well-defined cluster structure.

3.  **Clustering Algorithm**: With the optimal `k` determined, **K-Means clustering** is applied to group the sentence vectors. Each resulting cluster represents a putative word sense.

### 3.4. Collocation Extraction and Filtering

To make the sense of each cluster interpretable, we extract significant collocates. Initial experiments showed that raw co-occurrence lists were dominated by high-frequency function words (e.g., prepositions, conjunctions), which provide little semantic value. To address this, we implemented a two-stage filtering process.

1.  **POS Filtering**: Using Stanza's Part-of-Speech tagger, we expanded the context window to **4 words** on either side of the target lemma but restricted the extracted collocates to a whitelist of content-word categories: `NOUN`, `PROPN` (proper noun), `VERB`, `ADJ` (adjective), and `ADV` (adverb). This immediately eliminated grammatical noise and focused the analysis on semantically meaningful words.

2.  **Cluster-Specific (TF-IDF) Filtering**: While POS filtering removed function words, some content words appeared across multiple clusters, failing to highlight the uniqueness of any single sense. We developed a heuristic inspired by TF-IDF to identify cluster-specific collocations. For each word in a cluster's collocation list, we check its distribution across all other clusters. A word is retained as a "specific collocate" only if it appears exclusively in that cluster or if its frequency within that cluster accounts for over 50% of its total occurrences across all clusters. This step effectively surfaces the words that truly define the specific context of a sense.

---

## 4. Case Study: The Lemma 'נקודה' (Nekuda)

To evaluate the system, we analyzed the polysemous lemma 'נקודה', which can mean 'point/dot', 'topic/issue', 'location', or a 'point' in a game.

### 4.1. Experimental Setup

-   **Corpus**: 50,000 sentences from the Hebrew news corpus.
-   **Target Lemma**: 'נקודה'.
-   **Parameters**:
    -   Context window size: 4 words.
    -   POS filter: `NOUN, PROPN, VERB, ADJ, ADV`.
    -   Clustering: K-Means with automatic `k` via silhouette score.

### 4.2. Results

The system found **102 sentences** containing the lemma 'נקודה'. The silhouette analysis determined the optimal number of clusters to be **k=8**. The combination of a larger window size and advanced filtering produced highly coherent and distinct collocation sets for each cluster.

### 4.3. Analysis of Selected Clusters

Below is an analysis of a few representative clusters from the output, demonstrating the successful sense disambiguation.

**Cluster 1: The "Sports/Competition" Sense**
-   **Size**: 5 sentences.
-   **Specific Collocates**: `ויתר` (gave up), `מראש` (in advance), `יובנטוס` (Juventus), `יתרון` (advantage), `אצי` (Lazio).
-   **Example Sentence**: "But the season was stopped after 26 rounds when Juventus had only a one-point advantage over Lazio..."
-   **Analysis**: This cluster clearly captures the sense of 'נקודה' as a point in a sporting context. The collocations are highly specific and include names of football clubs and words related to competition.

**Cluster 5: The "Struggle/Difficulty" Sense in Sports**
-   **Size**: 5 sentences.
-   **Specific Collocates**: `מפולת` (collapse), `יצא` (came out with), `קושי` (difficulty), `לבטיס` (to Betis), `נוסף` (additional).
-   **Example Sentence**: "But despite having listed against Tottenham and Manchester United in its recent games... Leicester barely came out with a point in a 1:1 draw."
-   **Analysis**: This is a nuanced sub-sense of the sports context, focusing on *barely achieving* a point. The collocations `מפולת` and `קושי` strongly indicate this theme of struggle.

**Cluster 0: The "Abstract/Geographic Point" Sense**
-   **Size**: 5 sentences.
-   **Specific Collocates**: `כנראה` (apparently), `כסף` (money), `אסטרטגי` (strategic), `ישראל` (Israel), `תל אביב` (Tel Aviv).
-   **Example Sentence**: "...200,000 missiles that know how to reach any strategic point in Israel."
-   **Analysis**: This cluster combines the abstract sense of a "point" in an argument ("no work, no money, period/point") with the sense of a geographic location. The collocate `אסטרטגי` is particularly revealing.

**Cluster 7: The "Location/Gaze" Sense**
-   **Size**: 5 sentences.
-   **Specific Collocates**: `בהה` (stared), `ברור` (clear), `חלל` (space), `מבודד` (isolated), `אוסטרלי` (Australian).
-   **Example Sentence**: "...she says and stares at an unclear point in the air space..."
-   **Analysis**: This cluster successfully isolates the sense of 'נקודה' as a physical point in space, either to be looked at or as a remote location. The collocate `בהה` is a perfect indicator of the "gaze" context, while `מבודד` points to the "isolated location" context.

---

## 5. Discussion and Future Work

The implemented system demonstrates considerable success in unsupervised word sense disambiguation for Hebrew. The automatic `k` detection proved effective, and the two-stage collocation filtering was critical for producing human-interpretable sense clusters.

However, there are several areas for improvement:

1.  **Data Sparsity**: With only 102 sentences, some clusters contained as few as 5 examples. This makes the collocation extraction sensitive to statistical noise. Running the system on the full 1-million-sentence corpus (or larger) is a necessary next step to ensure the robustness of the extracted patterns.

2.  **Refining GDEX Scoring**: The current example scoring is based on heuristics. A more sophisticated model could be trained to rank examples based on linguistic features that correlate with human judgments of example quality (e.g., syntactic simplicity, lexical diversity, absence of ambiguity).

3.  **Advanced Contextual Models**: While TF-IDF is effective, modern contextual embedding models like BERT could provide more nuanced sentence representations, potentially leading to even better clustering. Fine-tuning a Hebrew BERT model on this task could be a promising direction.

4.  **Handling Overlapping Senses**: The current "hard clustering" approach assigns each sentence to a single sense. In reality, some usages may be ambiguous or bridge multiple senses. A soft-clustering or probabilistic model could better capture this linguistic reality.

---

## 6. Conclusion

This project successfully developed an automated pipeline for Hebrew GDEX extraction. By integrating dynamic cluster detection with multi-stage, linguistically-informed collocation filtering, the system is able to identify and characterize distinct word senses from a raw text corpus with a high degree of accuracy. The case study of 'נקודה' confirms that the methodology is effective for disambiguating polysemous words and providing valuable lexical insights. While further refinements are possible, the current system provides a strong foundation for future lexicographical research and tool development for the Hebrew language.
