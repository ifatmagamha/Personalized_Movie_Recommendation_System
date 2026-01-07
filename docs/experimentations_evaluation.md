# Experimental Framework: Intent

## 1. Purpose of the Experimentation Phase

The objective of this experimentation phase is **not** to aggressively optimize model hyperparameters, but to **understand the behavior and limitations** of classical recommender system components under controlled conditions.

This phase aims to answer the following high-level questions:

- How strong is a popularity-based baseline under a realistic evaluation protocol?
- Does collaborative filtering (CF) effectively improve recommendation quality?
- What factors limit CF performance in practice (data sparsity, candidate generation, evaluation protocol)?
- Which architectural choices are worth pursuing in subsequent system iterations?

This approach follows a **hypothesis-driven experimentation strategy**, commonly adopted in applied machine learning and recommender system research.

---

## 2. Why Not a Grid Search?

Grid search and exhaustive hyperparameter tuning focus on marginal performance gains, often at the expense of interpretability and computational cost.

In contrast, the goal of this project is to:

- isolate the impact of **system-level design choices**,
- preserve **causal interpretability**,
- and ensure **reproducibility and robustness**.

Given these objectives, controlled experiments were preferred over automated optimization techniques.

---

## 3. Experimental Dimensions Explored

The experimentation framework focuses on three key dimensions:

### 3.1 Model Comparison: Baseline vs Collaborative Filtering

A popularity-based Bayesian baseline is compared against a latent-factor Collaborative Filtering (SVD) model under identical evaluation conditions.

This experiment establishes whether personalization provides measurable benefits over strong non-personalized heuristics.

---

### 3.2 Candidate Generation Capacity

Collaborative filtering models operate on a candidate set of items before ranking.
The size of this candidate pool directly affects recall and computational cost.

Experiments were conducted by varying the candidate pool size to determine whether performance limitations originate from insufficient candidate coverage.

---

### 3.3 Data Sparsity and Density

Collaborative filtering models rely on co-occurrence patterns.
To assess the impact of sparsity, experiments compare:

- CF trained and evaluated on the full interaction dataset
- CF evaluated on a denser subset of interactions (active users and popular items)

This isolates the effect of interaction density on latent factor learning.

---

## 4. Engineering and MLOps Considerations

All experiments are implemented as standalone CLI scripts, ensuring:

- reproducibility,
- separation of concerns (data building, training, evaluation),
- compatibility with automated pipelines (CI/CD, Docker).

Experimental outputs (metrics and per-user reports) are stored as versioned artifacts, enabling traceability and systematic analysis.

---

## 5. Position in the Overall System Roadmap

This experimentation phase represents the **final validation step of classical recommendation models**.

The insights obtained here serve as a foundation for motivating and designing more advanced hybrid architectures, including semantic and LLM-based components, introduced in later phases of the project.


# Analysis of Experimental Results

## 1. Overview of Conducted Experiments

Three main experimental axes were explored:

1. Baseline vs Collaborative Filtering comparison
2. Impact of candidate pool size on CF performance
3. Effect of dataset density on CF performance

All experiments use a strict time-based evaluation protocol (`last1`) and are evaluated using Recall@10 and NDCG@10.

---

## 2. Baseline vs Collaborative Filtering

### Results Summary

| Model      | Recall@10 | NDCG@10 |
|------------|-----------|---------|
| Baseline   | 0.055389  | 0.027892 |
| CF (SVD)   | 0.050898  | 0.029313 |

### Interpretation

- The popularity-based baseline achieves higher Recall@10, indicating that the target item is more frequently retrieved within the top-10 recommendations.
- Collaborative Filtering achieves higher NDCG@10, suggesting better ranking quality when a relevant item is retrieved.

This behavior highlights a common phenomenon in recommender systems: popularity-based methods perform strongly in sparse, recency-driven settings, while CF contributes personalization primarily through improved ranking rather than coverage.

---

## 3. Candidate Pool Size Experiment

### Results Summary

| Candidate Pool | Recall@10 | NDCG@10 |
|----------------|-----------|---------|
| 500            | 0.050898  | 0.029313 |
| 2000           | 0.050898  | 0.029313 |

### Interpretation

Increasing the candidate pool size does not improve performance.
This indicates that the limitation does not stem from insufficient candidate coverage, but from the model’s inability to distinguish the target item within the candidate set.

The results suggest that candidate generation based on global popularity already includes the relevant items, and that additional candidates do not provide meaningful new signal.

---

## 4. Dense vs Full Dataset for Collaborative Filtering

### Dataset Characteristics

The dense interaction subset contains:
- 70,472 interactions
- 662 users
- 1,322 movies

Users and items included in this subset satisfy minimum interaction thresholds, resulting in more stable co-occurrence patterns.

### Results Summary

| Dataset | Recall@10 | NDCG@10 |
|--------|-----------|---------|
| Full   | 0.050898  | 0.029313 |
| Dense  | 0.051360  | 0.029579 |

### Interpretation

A slight improvement is observed when evaluating on the dense dataset.
This confirms that data sparsity negatively affects CF performance.

However, the magnitude of the improvement is limited, indicating that sparsity is not the dominant bottleneck in this system.

---

## 5. Global Interpretation and Identified Bottleneck

The experiments collectively show that:

- Collaborative Filtering improves ranking quality but does not significantly improve recall under the chosen evaluation protocol.
- Neither candidate pool size nor interaction sparsity alone explains the observed performance plateau.
- The strict `last1` evaluation protocol favors popular items and short-term user behavior, which classical CF models struggle to capture.

The primary limitation is therefore not algorithmic, but informational: the lack of contextual and semantic signals required to model short-term user intent.

---

## 6. Implications for System Design

These results justify the transition toward hybrid recommendation architectures:

- Popularity-based models provide strong recall anchors.
- Collaborative Filtering contributes long-term personalization.
- Semantic and context-aware models (e.g., embeddings or LLM-based components) are required to capture user intent, mood, and transient preferences.

This layered approach enables the system to overcome the limitations observed in purely collaborative or popularity-based methods.

---

## 7. Conclusion

The experimentation phase successfully validates the classical recommendation pipeline and identifies its limitations.
Rather than pursuing further low-level optimization, the next development phase focuses on integrating semantic understanding through hybrid and LLM-assisted recommendation strategies.
