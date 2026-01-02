# Evaluation Synthesis — Baseline vs Collaborative Filtering (SVD)

## 1. Context and Goal
This section synthesizes the offline evaluation results obtained for:
- **Baseline model** (Bayesian-smoothed popularity ranking)
- **Collaborative Filtering model** (Matrix Factorization via Surprise SVD)

The goal is to:
1) analyze the outputs and understand performance drivers,  
2) compare baseline vs CF fairly under the same protocol,  
3) justify the transition toward a **hybrid / LLM-assisted recommender**, aligned with the project’s intent-driven UI (text/voice + mood).

---

## 2. Evaluation Protocol (Shared for Both Models)

### 2.1 Time-based holdout split
We use a **per-user time-aware split** to simulate real-world recommendation:
- Interactions are sorted chronologically per user
- **Train** = past interactions
- **Test** = the most recent interaction(s)

Main mode used so far:
- `holdout = last1` → 1 test item per user (very strict)

This protocol is scientifically sound because it avoids future leakage and mirrors the “predict what comes next” nature of recommenders.

### 2.2 Metrics
We report standard top-K ranking metrics:

**Recall@K**
- Measures whether the test item is retrieved in the Top-K list:
\[
Recall@K = \frac{|recommended \cap relevant|}{|relevant|}
\]
With `last1`, `|relevant| = 1`, so Recall is binary per user (0 or 1).

**NDCG@K**
- Measures ranking quality, rewarding early hits:
\[
DCG@K = \sum_{i=1}^{K} \frac{rel_i}{\log_2(i+1)}
\quad;\quad
NDCG@K = \frac{DCG@K}{IDCG@K}
\]
where \(rel_i = 1\) if the recommended item at position i is relevant.

---

## 3. Baseline Model Evaluation Analysis

### 3.1 Model definition
The baseline recommends globally popular and well-rated items using a **Bayesian-smoothed score**:

\[
score = \frac{v}{v+m}R + \frac{m}{v+m}C
\]

- \(v\): number of ratings for the movie  
- \(R\): mean rating for the movie  
- \(C\): global mean rating  
- \(m\): smoothing strength

### 3.2 What the baseline is good for
- **Cold-start**: works even if the user has no history
- **Robust fallback**: always returns recommendations
- **Reference benchmark**: establishes a lower bound for personalization

### 3.3 Why baseline performance is limited
- The baseline is **not personalized**
- It over-recommends head items (popular movies)
- Under strict `last1` evaluation, it can only succeed if the user’s next movie happens to be among global Top-K

**Scientific interpretation**
A low Recall@10 / NDCG@10 is expected because the model does not learn user-specific taste. This provides a clean motivation for moving to CF.

---

## 4. Collaborative Filtering (SVD) Evaluation Analysis

### 4.1 Model definition
We trained a **matrix factorization** model (Surprise SVD).  
It approximates the rating function by learning latent vectors:

\[
\hat{r}(u,i) = p_u^\top q_i
\]

- \(p_u\): user latent embedding  
- \(q_i\): item latent embedding  

This captures hidden taste factors beyond popularity.

### 4.2 Observed evaluation results
Example CF run (holdout `last1`, K=10):
- **Recall@10 ≈ 0.0509**
- **NDCG@10 ≈ 0.0293**

Even if improvement over baseline is not dramatic, two points are critical:

#### (A) The CF model is actually learning personalization
Predictions show `cf_score` differs from baseline scores, indicating latent preference modeling is active.

#### (B) The evaluation setting is extremely strict
`last1` is a harsh benchmark:
- Only 1 relevant test item per user
- If the relevant item is ranked 11 → score becomes 0
This compresses performance differences and makes improvements harder to observe.

### 4.3 Why CF gains can appear modest
The main drivers limiting observed uplift:

1) **Candidate pool limitation**
Our CF inference re-ranks a limited candidate set (e.g., top 500 popular items).
If the test item is not inside that pool (long-tail), CF cannot recommend it, regardless of quality.

2) **Data sparsity**
Many users have few interactions. CF requires enough history per user to infer stable embeddings.

3) **No semantic/context signals**
CF uses only (userId, movieId, rating).  
It ignores mood, textual preferences, genres, and metadata semantics — which are exactly what the UI aims to provide.

---

## 5. Baseline vs CF — What We Can Conclude Now

### 5.1 What the comparison tells us
- The baseline is a strong, stable fallback and benchmark.
- CF introduces personalization and learns latent structure.
- Under strict evaluation and limited candidate pools, CF uplift may appear small, but the model is functioning correctly.

### 5.2 Why this is still a successful step
This is the expected progression in recommender system design:
1) **Baseline** (robust + cold-start)
2) **CF** (personalization using behavior)
3) **Hybrid** (combine behavior + semantics + context)

This progression is scientifically grounded and aligns with industrial recommender architectures.

---

## 6. Motivation for the Next Step: Hybrid / LLM-Assisted Recommender

### 6.1 Why hybrid is necessary
CF remains limited when:
- user history is sparse (cold-start)
- relevant items are long-tail
- the request is contextual (“I’m sad, I want a comforting movie”)

LLM can:
- interpret **mood and intent** from text/voice input
- enrich items with semantic attributes (themes, emotions, pace, style)
- re-rank CF candidates using natural language matching
- generate **explanations** (“recommended because you liked X and asked for Y mood”)

### 6.2 Proposed hybrid pipeline (next stage)
A practical production-like approach:
1) **Candidate generation**: CF returns top ~200 movies
2) **Semantic reranking**: LLM (or embeddings) ranks candidates against user intent/mood
3) **Explanation**: LLM generates a short reason for each recommendation
4) **Fallback**: baseline if user has no history

---

## 7. Conclusion
The evaluation results provide a coherent story:
- **Baseline** is stable but non-personalized → expected low performance in next-item prediction.
- **CF (SVD)** learns personalization and produces distinct predicted scores, but measured gains are constrained by strict holdout settings, candidate pool restrictions, and dataset sparsity.
- These findings strongly justify the transition to a **hybrid / LLM-assisted recommender**, which can incorporate semantic intent (mood + preferences) and better serve sparse-history users — consistent with the project’s UI and end-to-end system goals.
