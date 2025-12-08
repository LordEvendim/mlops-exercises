import joblib
from pathlib import Path
from sentence_transformers import SentenceTransformer

MODEL_PATH = Path("ai_models/classifier.joblib")
SENTENCE_TRANSFORMER_PATH = "ai_models/sentence_transformer.model"

SENTIMENT_TO_LABEL = {0: "negative", 1: "neutral", 2: "positive"}


def load_models(
    path: Path = MODEL_PATH, sentence_transformer_path: str = SENTENCE_TRANSFORMER_PATH
) -> tuple[object, SentenceTransformer]:
    return (joblib.load(path), SentenceTransformer(sentence_transformer_path))


def predict_sentiment(lr_model, st_model, text: str) -> str:
    embedding = st_model.encode([text])
    prediction = lr_model.predict(embedding)[0]

    return SENTIMENT_TO_LABEL[prediction]
