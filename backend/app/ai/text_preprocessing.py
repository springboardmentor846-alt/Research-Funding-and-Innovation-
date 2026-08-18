"""
Text preprocessing utilities for the recommendation engine.

Implements the cleaning pipeline used before TF-IDF vectorization.
"""
import re
from typing import List

import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer, PorterStemmer
from nltk.tokenize import word_tokenize

# Download minimal NLTK data on first use (idempotent)
try:
    _ = stopwords.words("english")
except LookupError:
    try:
        nltk.download("stopwords", quiet=True)
        nltk.download("punkt", quiet=True)
        nltk.download("wordnet", quiet=True)
        nltk.download("punkt_tab", quiet=True)
    except Exception:
        pass


class TextPreprocessor:
    """Reusable text-cleaning + tokenization helper."""

    def __init__(self, use_stemming: bool = True):
        self.lemmatizer = WordNetLemmatizer()
        self.stemmer = PorterStemmer()
        self.use_stemming = use_stemming
        try:
            self.stop_words = set(stopwords.words("english"))
        except Exception:
            self.stop_words = set()

    @staticmethod
    def clean(text: str) -> str:
        """Lowercase, remove URLs, digits, punctuation, extra whitespace."""
        if not text:
            return ""
        text = text.lower()
        text = re.sub(r"http\S+|www\.\S+", " ", text)  # urls
        text = re.sub(r"<.*?>", " ", text)  # html
        text = re.sub(r"[^a-z\s]", " ", text)  # punctuation/numbers
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def tokenize(self, text: str) -> List[str]:
        """Tokenize, remove stopwords, and apply lemmatization/stemming."""
        cleaned = self.clean(text)
        try:
            tokens = word_tokenize(cleaned)
        except Exception:
            tokens = cleaned.split()
        tokens = [t for t in tokens if t not in self.stop_words and len(t) > 2]
        if self.use_stemming:
            tokens = [self.stemmer.stem(t) for t in tokens]
        else:
            tokens = [self.lemmatizer.lemmatize(t) for t in tokens]
        return tokens

    def extract_keywords(self, text: str, top_n: int = 20) -> List[str]:
        """Return top-N tokens by frequency after cleaning."""
        tokens = self.tokenize(text)
        freq: dict[str, int] = {}
        for t in tokens:
            freq[t] = freq.get(t, 0) + 1
        sorted_tokens = sorted(freq.items(), key=lambda x: x[1], reverse=True)
        return [t for t, _ in sorted_tokens[:top_n]]

    def build_corpus(self, documents: List[str]) -> List[str]:
        """Return space-separated cleaned tokens for each document."""
        return [" ".join(self.tokenize(doc)) for doc in documents]
