from functools import lru_cache
from pathlib import Path

import joblib
import pandas as pd


MODEL_PATH = (
    Path(__file__).resolve().parent
    / "pcos_clinical_model_v1.joblib"
)

#Singleton design pattern
@lru_cache
def load_model_bundle() -> dict:
    bundle = joblib.load(MODEL_PATH)

    required_keys = {"model", "threshold", "features"}

    if not required_keys.issubset(bundle):
        raise RuntimeError("Invalid PCOS model bundle")

    return bundle


def predict_pcos_risk(
    features: pd.DataFrame,
) -> tuple[float, str]:
    bundle = load_model_bundle()

    expected_features = bundle["features"]
    missing = set(expected_features) - set(features.columns)

    if missing:
        raise ValueError(
            f"Missing model features: {sorted(missing)}"
        )

    model_input = features[expected_features]
    model = bundle["model"]

    classes = list(model.classes_)

    if 1 not in classes:
        raise RuntimeError("Model has no positive PCOS class")

    positive_class_index = classes.index(1)

    probability = float(
        model.predict_proba(model_input)[0][positive_class_index]
    )

    threshold = float(bundle["threshold"])

    prediction_class = (
        "High Risk"
        if probability >= threshold
        else "Low Risk"
    )

    return probability, prediction_class