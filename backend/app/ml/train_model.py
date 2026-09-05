import joblib
import numpy as np

from sklearn.ensemble import RandomForestClassifier

# Features (in this exact order):
# [publications_count, patents_count, domains_count, keywords_count,
#  technology_areas_count, innovation_score, text_similarity]
#
# text_similarity is a 0-1 TF-IDF cosine similarity between the
# researcher's profile text and the funding opportunity's text.

X = np.array([
    [0, 0, 1, 1, 0, 10, 0.05],
    [0, 0, 1, 2, 1, 18, 0.15],
    [1, 0, 1, 2, 1, 22, 0.20],
    [1, 0, 2, 3, 1, 28, 0.25],
    [1, 0, 2, 3, 2, 32, 0.30],
    [2, 0, 2, 4, 2, 38, 0.32],
    [2, 1, 2, 4, 2, 42, 0.38],
    [2, 1, 3, 4, 3, 45, 0.40],
    [3, 1, 3, 5, 3, 50, 0.45],
    [3, 1, 3, 5, 3, 52, 0.48],
    [4, 1, 3, 6, 3, 58, 0.52],
    [4, 2, 4, 6, 3, 60, 0.55],
    [5, 2, 4, 7, 4, 65, 0.58],
    [5, 2, 4, 7, 4, 68, 0.60],
    [6, 2, 4, 7, 4, 70, 0.62],
    [6, 2, 4, 8, 5, 72, 0.65],
    [7, 3, 5, 8, 5, 76, 0.68],
    [8, 3, 5, 9, 5, 80, 0.70],
    [8, 3, 5, 10, 5, 82, 0.72],
    [9, 3, 5, 10, 6, 85, 0.75],
    [10, 4, 5, 11, 6, 88, 0.78],
    [10, 4, 6, 12, 6, 90, 0.80],
    [11, 4, 6, 12, 6, 92, 0.83],
    [12, 5, 6, 13, 7, 95, 0.87],
    [13, 5, 6, 14, 7, 97, 0.90],
    [14, 6, 7, 15, 8, 98, 0.93],
    [15, 6, 7, 16, 8, 99, 0.95],
    [16, 7, 8, 17, 9, 100, 0.97],
])

# 0 = Low probability of success, 1 = High probability of success
y = np.array([
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    1, 1, 1, 1, 1, 1, 1, 1,
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
])

model = RandomForestClassifier(
    n_estimators=150,
    max_depth=6,
    random_state=42,
)

model.fit(X, y)

joblib.dump(model, "grant_model.pkl")

print("Grant prediction model trained successfully.")
print("Feature importances:")
feature_names = [
    "publications_count", "patents_count", "domains_count",
    "keywords_count", "technology_areas_count", "innovation_score",
    "text_similarity",
]
for name, importance in zip(feature_names, model.feature_importances_):
    print(f"  {name}: {importance:.3f}")