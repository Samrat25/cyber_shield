# core/ml_detector.py
import pickle
import numpy as np
from pathlib import Path
from sklearn.ensemble import IsolationForest

MODEL_PATH = "logs/model.pkl"

def train():
    """Train the anomaly detection model on normal baseline data."""
    # Simulate normal baseline metrics
    normal_data = []
    for _ in range(200):
        normal_data.append([
            np.random.uniform(10, 30),   # cpu_percent
            np.random.uniform(40, 60),   # memory_percent
            np.random.randint(120, 160), # process_count
        ])
    
    model = IsolationForest(contamination=0.1, random_state=42)
    model.fit(normal_data)
    
    Path(MODEL_PATH).parent.mkdir(exist_ok=True)
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)

def detect(metrics: dict) -> tuple[str, float]:
    """
    Returns (verdict, score).
    verdict: 'safe' or 'anomaly'
    score: negative means anomaly
    """
    if not Path(MODEL_PATH).exists():
        train()
    
    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)
    
    features = np.array([[
        metrics["cpu_percent"],
        metrics["memory_percent"],
        metrics["process_count"],
    ]])
    
    prediction = model.predict(features)[0]
    score = model.score_samples(features)[0]
    
    verdict = "safe" if prediction == 1 else "anomaly"
    return verdict, round(score, 3)
