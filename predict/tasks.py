import pandas as pd
from celery import shared_task
from .feature_extractor import extract_features
import joblib
import os
import numpy as np
from .models import PredictionLog


#load model once worker starts
MODEL_PATH = os.path.join(os.path.dirname(__file__),'..','ml', 'phishing_model.pkl')
FEATURES_PATH = os.path.join(os.path.dirname(__file__),'..','ml', 'feature_columns.txt')


model = None
feature_columns = None

def load_model():
    global model, feature_columns
    if model is None:
        model = joblib.load(MODEL_PATH)
        with open(FEATURES_PATH, 'r') as f:
            feature_columns = [line.strip() for line in f.readlines()]
    return model, feature_columns

@shared_task
def test_task(url):
    # Just a placeholder – later this will do WHOIS, SSL, ML
    return f"Received URL: {url} – task executed successfully"

@shared_task
def analyze_url_task(url):
    """Extract features and return prediction (phase 2: just return features)"""
    features_dict = extract_features(url)

    model, feature_cols = load_model()
    X = pd.DataFrame([[features_dict[col] for col in feature_cols]], columns=feature_cols)

    # Predict
    prediction = model.predict(X)[0]  # 0 = legitimate, 1 = phishing
    confidence = model.predict_proba(X)[0].max()

    # Save prediction to database
    PredictionLog.objects.create(
        task_id=analyze_url_task.request.id,
        url=url,
        prediction='phishing' if prediction == 1 else 'legitimate',
        confidence=float(confidence),
        features=features_dict
    )

    return {
        'url': url,
        'features': features_dict,
        'prediction': 'phishing' if prediction == 1 else 'legitimate',
        'confidence': float(confidence),
        'status': 'completed',
    }
