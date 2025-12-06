import pandas as pd
from sklearn.model_selection import train_test_split

def load_and_preprocess(csv_paths):
    """
    Load multiple CSVs, merge, clean, preprocess
    """
    dfs = [pd.read_csv(path) for path in csv_paths]
    data = pd.concat(dfs, ignore_index=True)

    # Simple preprocessing
    data['query'] = data['query'].astype(str)
    data['label'] = data['label'].astype(int)

    return data

def split_data(data, test_size=0.2, random_state=42):
    X = data['query']
    y = data['label']
    return train_test_split(X, y, test_size=test_size, random_state=random_state)
