import joblib
import pandas as pd
from utils.metrics import evaluate_model

model = joblib.load("../detection_api/models/sqli_model.pkl")
vectorizer = joblib.load("../detection_api/models/vectorizer.pkl")

data = pd.read_csv("../datasets/processed/processed_data.csv")
X = vectorizer.transform(data['query'])
y = data['label']

y_pred = model.predict(X)
metrics = evaluate_model(y, y_pred)
print("Evaluation metrics on full dataset:", metrics)
