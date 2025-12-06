import os

class Config:
    MODEL_PATH = os.getenv("MODEL_PATH", "models/sqli_model.pkl")
    APP_NAME = "SQLi Detection System"
    VERSION = "1.0.0"