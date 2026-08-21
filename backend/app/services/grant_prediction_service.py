_model = None


def _get_model():
    """Load the trained grant model only when prediction is requested."""
    global _model

    if _model is None:
        import joblib

        _model = joblib.load(
            "app/ml/grant_model.pkl"
        )

    return _model


def predict_probability(features):

    model = _get_model()

    probability = model.predict_proba(
        [features]
    )[0][1]

    return round(
        probability * 100,
        2
    )
