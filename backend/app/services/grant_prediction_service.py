import joblib

model = joblib.load(
    "app/ml/grant_model.pkl"
)


def predict_probability(features):

    probability = model.predict_proba(
        [features]
    )[0][1]

    return round(
        probability * 100,
        2
    )