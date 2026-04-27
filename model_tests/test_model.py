import os
import pytest
import joblib  # or pickle, depending on your serialization method
import numpy as np
from sklearn.metrics import accuracy_score
import pandas as pd

def test_model_loading():
    model_path = 'models/model.pkl'
    assert os.path.exists(model_path), f"Model file not found at {model_path}"
    try:
        model = joblib.load(model_path)
    except Exception as e:
        pytest.fail(f"Failed to load model: {e}")


def test_prediction_shape():
    model = joblib.load('models/model.pkl')
    sample_input = np.random.rand(5, model.n_features_in_)
    predictions = model.predict(sample_input)
    assert predictions.shape == (5,), f"Expected predictions of shape (5,), got {predictions.shape}"

def test_prediction_values():
    model = joblib.load('models/model.pkl')
    sample_input = np.random.rand(5, model.n_features_in_)
    predictions = model.predict(sample_input)
    assert set(predictions).issubset({0, 1}), f"Predictions contain unexpected classes: {set(predictions)}"

def test_model_accuracy():
    model = joblib.load('models/model.pkl')
    scaler = joblib.load('models/scaler.pkl')
    encoders = joblib.load('models/encoders.pkl')
    COLUMNS = [
        "age", "workclass", "fnlwgt", "education", "education-num", "marital-status",
        "occupation", "relationship", "race", "sex", "capital-gain", "capital-loss",
        "hours-per-week", "native-country", "income"
    ]
    test_data = pd.read_csv('data/raw/adult.test', header=None, names=COLUMNS, skipinitialspace=True, skiprows=1)
    test_data["income"] = test_data["income"].str.replace(".", "", regex=False)
    test_data = test_data.dropna()
    for col, le in encoders.items():
        test_data[col] = le.transform(test_data[col])
    test_data["income"] = test_data["income"].apply(lambda x: 1 if x == ">50K" else 0)
    X_test = test_data.drop("income", axis=1)
    y_test = test_data["income"].to_numpy()
    X_test_scaled = scaler.transform(X_test)
    predictions = model.predict(X_test_scaled)
    accuracy = accuracy_score(y_test, predictions)
    assert accuracy >= 0.80, f"Model accuracy below expected threshold: {accuracy:.2f}"