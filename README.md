## Data Access & Preprocessing

### Data Sources
The project relies on a dataset hosted in BigQuery:

- **Project**: `master-ai-cloud`
- **Dataset**: `MoviePlatform`
- **Tables**:
  - `ratings`: user–movie ratings with timestamps
  - `movies`: movie metadata (title, genres)

### Preprocessing Strategy
All preprocessing is implemented in `src/preprocessing.py` and follows a **CTE-only** approach ensuring compatibility with viewer-only permissions.

Main preprocessing steps include:
- Computation of per-movie statistics (number of ratings, mean, standard deviation)
- Computation of per-user activity statistics
- Construction of a filtered interaction dataset `(userId, movieId, rating, timestamp)`

### Design Choices
To ensure statistical stability and reduce noise, the following thresholds are applied:
- Minimum number of ratings per user: **5**
- Minimum number of ratings per movie: **20**

These thresholds are motivated by exploratory data analysis and aim to:
- Reduce extreme cold-start effects
- Improve robustness of downstream recommendation models
- Control BigQuery query costs

### Output
The preprocessing layer outputs Pandas DataFrames that can be directly used for:
- Exploratory Data Analysis (EDA)
- Model training
- Baseline and advanced recommendation algorithms