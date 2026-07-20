from sentence_transformers import SentenceTransformer

# Load the model only once when the application starts
model = SentenceTransformer("all-MiniLM-L6-v2")


def generate_embedding(text: str):
    """
    Generate an embedding vector for the given text.
    """
    return model.encode(text, convert_to_numpy=True)