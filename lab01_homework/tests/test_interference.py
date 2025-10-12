from pydantic import ValidationError
import pytest
from fastapi.testclient import TestClient

from interference import load_models, predict_sentiment
from api.models.sentiment import PredictRequest
import app


@pytest.fixture(scope="session")
def client():
    return TestClient(app.app)


def test_predict_request_rejects_empty():
    with pytest.raises(ValidationError):
        PredictRequest(text="")


def test_load_models():
    lr_model, st_model = load_models()

    assert lr_model is not None
    assert st_model is not None


def test_predict_sentiment():
    lr_model, st_model = load_models()

    expected = ["negative", "neutral", "positive"]
    samples = [
        "This is a negative message.",
        "This is a neutral message.",
        "This is a positive message.",
    ]

    for i in range(len(expected)):
        exp = expected[i]
        sample = samples[i]
        prediction = predict_sentiment(lr_model, st_model, sample)
        assert prediction == exp


def test_predict_endpoint_validation(client):
    response = client.post("/predict", json={"text": "This is positive."})

    assert response.json()["prediction"] == "positive"


def test_predict_endpoint_validation_error(client):
    response = client.post("/predict", json={"text": ""})

    assert response.status_code == 422

    payload = response.json()
    assert payload["detail"]
