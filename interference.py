import joblib
import numpy as np
from pathlib import Path
from typing import Iterable, Sequence
from sklearn.datasets import load_iris

MODEL_PATH = Path("model.joblib")


def load_model(path: Path = MODEL_PATH):
    return joblib.load(path)


def predict(model, features: Sequence[float] | Iterable[float]) -> str:
    features_array = np.asarray(list(features), dtype=float).reshape(1, -1)
    target_names = load_iris().target_names
    pred_idx = model.predict(features_array)[0]
    return target_names[pred_idx]
