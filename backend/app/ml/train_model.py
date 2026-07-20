import joblib
import numpy as np

from sklearn.ensemble import RandomForestClassifier

# Features
# publications
# patents
# domains
# keywords
# technology areas
# innovation score
# semantic similarity

X = np.array([
    [0,0,1,2,1,20,0.20],
    [1,0,2,3,2,35,0.35],
    [2,1,2,4,3,48,0.45],
    [4,1,3,6,3,60,0.60],
    [6,2,4,7,4,72,0.72],
    [8,2,4,8,5,80,0.80],
    [10,3,5,10,5,90,0.92],
    [12,4,5,12,6,98,0.96]
])

# 0 = Low
# 1 = High

y = np.array([
    0,
    0,
    0,
    1,
    1,
    1,
    1,
    1
])

model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

model.fit(X,y)

joblib.dump(
    model,
    "app/ml/grant_model.pkl"
)

print("Grant prediction model trained successfully.")