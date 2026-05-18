import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score
import os

# Load features
df = pd.read_csv('datasets/features/phiusiil_features.csv')

# Drop non-feature columns
feature_cols = [c for c in df.columns if c not in ['url', 'label']]
X = df[feature_cols].fillna(-1)
y = df['label']

print(f"Loaded {len(X)} samples with {len(feature_cols)} features.")
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
print(classification_report(y_test, y_pred, target_names=['Legitimate', 'Phishing']))
print(f"ROC-AUC: {roc_auc_score(y_test, model.predict_proba(X_test)[:,1]):.4f}")

os.makedirs('ml/real_training', exist_ok=True)
joblib.dump(model, 'ml/real_training/phishing_model_real.pkl')
with open('ml/real_training/feature_columns_real.txt', 'w') as f:
    f.write('\n'.join(feature_cols))
print("Model saved.")