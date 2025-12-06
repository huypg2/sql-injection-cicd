from utils.featurize import featurize_query

def test_features():
    query = "SELECT * FROM users"
    features = featurize_query(query)
    assert len(features) == 2
    assert features[0] == len(query)
