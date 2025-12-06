import pandas as pd
from utils.data_loader import load_and_preprocess

csv_paths = [
    "datasets/raw/kaggle_sqli.csv",
    "datasets/raw/synthetic_payloads.csv",
    "datasets/raw/waf_logs.csv"
]

data = load_and_preprocess(csv_paths)

# Lưu processed data
data.to_csv("datasets/processed/processed_data.csv", index=False)
print("Processed data saved to datasets/processed/processed_data.csv")
