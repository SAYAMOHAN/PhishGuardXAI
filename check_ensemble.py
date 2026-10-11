import pandas as pd

from models.bert.predict import predict_bert
from models.gnn.predict import predict_gnn
from backend.feature_extractor import extract_features, FEATURE_NAMES
from backend.services.prediction_service import model
from backend.services.risk_engine import risk_engine

urls = [
    "https://www.wikipedia.org/",
    "http://paypal.com.security-check.example/login",
    "http://192.168.1.10/login",
]

for url in urls:
    p_bert = float(predict_bert(url))
    p_gnn = float(predict_gnn(url))

    features = extract_features(url)
    X = pd.DataFrame(
        [[features[name] for name in FEATURE_NAMES]],
        columns=FEATURE_NAMES,
    )
    p_lgbm = float(model.predict_proba(X)[0][1])

    result = risk_engine.evaluate_risk(
        p_bert, p_lgbm, p_gnn, features=features
    )

    print("\nURL:", url)
    print("BERT phishing probability:", round(p_bert, 4))
    print("LightGBM class-1 probability:", round(p_lgbm, 4))
    print("GNN phishing probability:", round(p_gnn, 4))
    print("Risk engine result:", result)
