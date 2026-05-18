import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import joblib
import os

# Generate synthetic dataset (replace with real data later)
np.random.seed(42)
n_samples = 2000

# Feature columns (same order as we extract)
features = [
    'domain_age_days', 'ssl_valid', 'ssl_days_remaining',
    'url_length', 'num_special_chars', 'has_ip', 'num_subdomains',
    'contains_keyword', 'using_shortener', 'tld_rank'
]

# Create synthetic data
data = pd.DataFrame()

# Legitimate (label 0) and phishing (label 1) patterns
legit = pd.DataFrame({
    'domain_age_days': np.random.randint(365, 5000, n_samples//2),
    'ssl_valid': np.random.choice([True, False], n_samples//2, p=[0.95, 0.05]),
    'ssl_days_remaining': np.random.randint(30, 365, n_samples//2),
    'url_length': np.random.randint(20, 80, n_samples//2),
    'num_special_chars': np.random.randint(1, 5, n_samples//2),
    'has_ip': np.random.choice([True, False], n_samples//2, p=[0.01, 0.99]),
    'num_subdomains': np.random.randint(0, 2, n_samples//2),
    'contains_keyword': np.random.choice([True, False], n_samples//2, p=[0.1, 0.9]),
    'using_shortener': np.random.choice([True, False], n_samples//2, p=[0.02, 0.98]),
    'tld_rank': np.random.choice([1,2,3,4,5], n_samples//2, p=[0.05,0.1,0.1,0.3,0.45])
})
legit['label'] = 0

phish = pd.DataFrame({
    'domain_age_days': np.random.randint(0, 30, n_samples//2),
    'ssl_valid': np.random.choice([True, False], n_samples//2, p=[0.2, 0.8]),
    'ssl_days_remaining': np.random.randint(0, 30, n_samples//2),
    'url_length': np.random.randint(60, 200, n_samples//2),
    'num_special_chars': np.random.randint(5, 20, n_samples//2),
    'has_ip': np.random.choice([True, False], n_samples//2, p=[0.3, 0.7]),
    'num_subdomains': np.random.randint(2, 6, n_samples//2),
    'contains_keyword': np.random.choice([True, False], n_samples//2, p=[0.8, 0.2]),
    'using_shortener': np.random.choice([True, False], n_samples//2, p=[0.5, 0.5]),
    'tld_rank': np.random.choice([1,2,3,4,5], n_samples//2, p=[0.4,0.3,0.15,0.1,0.05])
})
phish['label'] = 1

df = pd.concat([legit, phish], ignore_index=True)

# Split
X = df[features]
y = df['label']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
print("Accuracy:", accuracy_score(y_test, y_pred))
print(classification_report(y_test, y_pred))

# Save model and feature list
os.makedirs('ml', exist_ok=True)
joblib.dump(model, 'ml/phishing_model.pkl')
with open('ml/feature_columns.txt', 'w') as f:
    f.write('\n'.join(features))

print("Model saved to ml/phishing_model.pkl")