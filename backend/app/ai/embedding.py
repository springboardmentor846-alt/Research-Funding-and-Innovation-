# from sentence_transformers import SentenceTransformer

# # Load the model only once when the application starts
# model = SentenceTransformer("all-MiniLM-L6-v2")


# def generate_embedding(text: str):
#     """
#     Generate an embedding vector for the given text.
#     """
#     return model.encode(text, convert_to_numpy=True)

from sentence_transformers import SentenceTransformer

_model = None


def get_model():
    """
    Load the model only when it is needed for the first time.
    """
    global _model

    if _model is None:
        print("Loading embedding model...")
        _model = SentenceTransformer("all-MiniLM-L6-v2")

    return _model


def generate_embedding(text: str):
    """
    Generate an embedding vector for the given text.
    """
    model = get_model()
    return model.encode(text, convert_to_numpy=True)