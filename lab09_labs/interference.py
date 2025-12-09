from pathlib import Path
import joblib
from sentence_transformers import SentenceTransformer
import boto3
import zipfile

SENTIMENT_TO_LABEL = {0: "negative", 1: "neutral", 2: "positive"}

BUCKET_NAME = "bartosz-s3-bucket"
CLASSIFIER_KEY = "classifier.joblib"
CLASSIFIER_PATH = Path("ai_models/classifier.joblib")

ST_ZIP_KEY = "sentence_transformer.model.zip"
ST_ZIP_PATH = Path("ai_models/sentence_transformer.model.zip")
ST_PATH = Path("ai_models/sentence_transformer.model")


def load_models() -> tuple[object, SentenceTransformer]:
    s3 = boto3.client("s3")

    ST_PATH.parent.mkdir(parents=True, exist_ok=True)

    s3.download_file(BUCKET_NAME, CLASSIFIER_KEY, str(CLASSIFIER_PATH))
    s3.download_file(BUCKET_NAME, ST_ZIP_KEY, str(ST_ZIP_PATH))

    with zipfile.ZipFile(ST_ZIP_PATH, "r") as zip_ref:
        zip_ref.extractall(ST_PATH.parent)

    ST_ZIP_PATH.unlink()

    return (
        joblib.load(CLASSIFIER_PATH),
        SentenceTransformer(str(ST_PATH)),
    )


def predict_sentiment(lr_model, st_model, text: str) -> str:
    embedding = st_model.encode([text])
    prediction = lr_model.predict(embedding)[0]

    return SENTIMENT_TO_LABEL[prediction]
