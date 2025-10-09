import joblib
from pathlib import Path
from typing import Tuple
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier

MODEL_PATH = Path("model.joblib")


def load_data() -> Tuple[list, list]:
    data = load_iris()

    return data.data, data.target


def train_model(X, y) -> RandomForestClassifier:
    model = RandomForestClassifier(random_state=42)
    model.fit(X, y)

    return model


def save_model(model, path: Path = MODEL_PATH) -> Path:
    joblib.dump(model, path)

    return path


if __name__ == "__main__":
    X, y = load_data()
    model = train_model(X, y)
    save_model(model)
