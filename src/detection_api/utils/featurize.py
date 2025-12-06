def featurize_query(query: str):
    # Ví dụ simple feature: độ dài, số keyword nguy hiểm
    keywords = ["select", "union", "drop", "insert", "--", "'"]
    features = [len(query)]
    features.append(sum(1 for k in keywords if k in query.lower()))
    return features
