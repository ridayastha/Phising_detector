import pandas as pd
from celery import shared_task
from .feature_extractor import extract_features
import joblib
import os
from .models import PredictionLog

# Paths to real model
MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'ml', 'real_training', 'phishing_model_real.pkl')
FEATURES_PATH = os.path.join(os.path.dirname(__file__), '..', 'ml', 'real_training', 'feature_columns_real.txt')

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
def analyze_url_task(url):
    features_dict = extract_features(url)
    model, feature_cols = load_model()
    X = pd.DataFrame([[features_dict[col] for col in feature_cols]], columns=feature_cols)
    prediction = model.predict(X)[0]
    confidence = model.predict_proba(X)[0].max()

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