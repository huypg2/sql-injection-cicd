import joblib

model = joblib.load("sqli_model.pkl")
joblib.dump(model, "../detection_api/models/sqli_model.pkl")
print("Model exported to detection_api/models/sqli_model.pkl")
