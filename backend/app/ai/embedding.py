_model = None


def get_model():
    """
    Load the embedding model only when it is needed for the first time.

    The SentenceTransformer import is intentionally inside this function so
    that PyTorch/Transformers are not loaded when FastAPI starts.
    """
    global _model

    if _model is None:
        print("Loading embedding model...")

        from sentence_transformers import SentenceTransformer

        _model = SentenceTransformer("all-MiniLM-L6-v2")

    return _model


def generate_embedding(text: str):
    """
    Generate an embedding vector for the given text.
    """
    model = get_model()
    return model.encode(text, convert_to_numpy=True)
