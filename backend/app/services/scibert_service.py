from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


class SciBERTService:

    def __init__(self):

        self.model = SentenceTransformer(
            "allenai/scibert_scivocab_uncased",
            device="cpu"
        )

    def encode(self, text: str):

        embedding = self.model.encode(text)

        return embedding.tolist()

    def similarity(self, text1: str, text2: str):

        embeddings = self.model.encode([text1, text2])

        score = cosine_similarity(
            [embeddings[0]],
            [embeddings[1]]
        )[0][0]

        return float(score)