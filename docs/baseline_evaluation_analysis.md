# Evaluation Analysis and Model Comparison

## 1. Overview

This section presents the analysis of the offline evaluation results obtained for the movie recommendation system.  
The evaluation is based on a **time-aware user-level holdout strategy** and focuses on ranking quality metrics commonly used in recommender systems.

The objectives of this evaluation phase are:
- To assess the effectiveness of the baseline recommendation model
- To analyze performance at the user level
- To identify the limitations of non-personalized approaches
- To justify the transition toward Collaborative Filtering and hybrid (LLM-assisted) models

---

## 2. Evaluation Protocol

### 2.1 Data Split Strategy

To avoid information leakage and respect the temporal nature of user interactions, a **time-based split per user** was applied:

- Interactions are sorted chronologically for each user
- The most recent interaction (`last1`) is assigned to the test set
- All earlier interactions are used for training

This setup simulates a realistic scenario where the system predicts future user preferences based only on past behavior.

---

### 2.2 Metrics

The following ranking-based metrics were computed:

- **Recall@K**  
  Measures whether the relevant item appears in the top-K recommendations.

- **NDCG@K (Normalized Discounted Cumulative Gain)**  
  Measures both relevance and ranking position, giving higher weight to items appearing earlier in the list.

These metrics are well-suited for implicit recommendation scenarios and sparse feedback datasets.

---

## 3. Per-User Analysis

Each row in `eval_report.csv` corresponds to one evaluated user and contains:
- `userId`
- `n_relevant`: number of relevant items in the test set
- `recall@10`
- `ndcg@10`

### Observations

- Most users have `n_relevant = 1`, which is expected given the `last1` holdout strategy.
- For many users, `recall@10 = 0.0`, meaning the relevant item did not appear in the top-10 recommendations.
- A small subset of users shows positive recall and non-zero NDCG values.

### Interpretation

This behavior is **expected** for a popularity-based baseline:
- The model recommends globally popular movies
- Users whose test movie is popular may be correctly predicted
- Users with niche or personalized tastes are poorly served

This highlights the **lack of personalization** in the baseline approach.

---

## 4. Baseline Model Performance

### Model Description

The baseline recommender ranks movies using a **Bayesian-smoothed popularity score**, combining:
- Average rating
- Number of ratings
- Global mean rating

This approach is:
- Simple
- Robust
- Cold-start friendly
- Commonly used as a reference baseline in recommender system research

### Strengths

- Stable recommendations
- Low variance
- No dependency on user history
- Works for anonymous users

### Limitations

- No user personalization
- Cannot model individual preferences
- Biased toward very popular items
- Poor performance for long-tail content

The evaluation results confirm these limitations, as reflected by low Recall@10 and NDCG@10 scores.

---

## 5. Comparison: Baseline vs Collaborative Filtering

### Expected Improvements with Collaborative Filtering

Collaborative Filtering (CF) models, such as matrix factorization (SVD), leverage:
- User–item interaction patterns
- Latent representations of users and movies
- Similarities across user behaviors

Compared to the baseline:
- CF captures **personal taste**
- CF improves recall for users with sufficient history
- CF reduces popularity bias

### Empirical Justification

The baseline evaluation establishes a **lower bound** of performance.  
Any improvement observed with CF can be directly attributed to:
- Learning user-specific latent factors
- Exploiting collaborative signals unavailable to popularity-based methods

This comparison is essential to:
- Validate modeling choices
- Quantify the benefit of personalization
- Provide an objective benchmark

---

## 6. Motivation for Advanced Models

### Why Baseline Is Not Enough

- Real-world users do not share the same preferences
- Recommendation quality depends on personalization
- Popularity alone cannot explain individual choices

The baseline serves as a **control model**, not a final solution.

---

### Why Collaborative Filtering Is Necessary

Collaborative Filtering:
- Models user–item interactions explicitly
- Generalizes preferences across similar users
- Is a standard approach in both academia and industry

However, CF also has limitations:
- Cold-start users and items
- Limited use of semantic content
- Difficulty capturing contextual intent (mood, intent, constraints)

---

### Why Move Toward LLM / Hybrid Models

LLM-assisted or hybrid recommenders address these limitations by:
- Interpreting natural language inputs (e.g., mood, intent)
- Enriching items with semantic representations
- Bridging the gap between user intent and structured data

Examples of hybrid usage:
- LLM-based mood → genre mapping
- Semantic re-ranking of CF candidates
- Explanations and conversational recommendations

Thus, the progression:
**Baseline → Collaborative Filtering → Hybrid / LLM-enhanced system**
is both **scientifically grounded** and **industrially relevant**.

---

## 7. Conclusion

The evaluation results demonstrate that:
- The baseline model provides a necessary but limited reference
- Offline metrics confirm the absence of personalization
- Collaborative Filtering is a justified and required next step
- Hybrid and LLM-based approaches naturally extend the system toward richer user interaction and intent modeling

This evaluation phase validates the system design choices and motivates the subsequent modeling stages.
