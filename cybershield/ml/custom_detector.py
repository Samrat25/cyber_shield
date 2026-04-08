# cybershield/ml/custom_detector.py
"""
Custom ML detector using your trained RandomForest model.
Features: value, rolling_mean, rolling_std, zscore, delta, delta_pct, rolling_max, max_ratio
"""

import joblib
import numpy as np
import warnings
from pathlib import Path
from collections import deque

warnings.filterwarnings('ignore')

MODEL_DIR = Path(__file__).parent / "model"
MODEL_PATH = MODEL_DIR / "cybershield_model.pkl"
SCALER_PATH = MODEL_DIR / "cybershield_scaler.pkl"
FEATURES_PATH = MODEL_DIR / "cybershield_features.pkl"


class CustomDetector:
    """
    Detector using your trained RandomForest model with rolling features.
    """
    
    def __init__(self, window_size=10):
        self.model = None
        self.scaler = None
        self.features = None
        self.window_size = window_size
        
        # History buffers for rolling statistics
        self.cpu_history = deque(maxlen=window_size)
        self.mem_history = deque(maxlen=window_size)
        self.proc_history = deque(maxlen=window_size)
        
        self._load_model()
    
    def _load_model(self):
        """Load model, scaler, and features."""
        try:
            self.model = joblib.load(MODEL_PATH)
            self.scaler = joblib.load(SCALER_PATH)
            self.features = joblib.load(FEATURES_PATH)
            return True
        except Exception as e:
            print(f"[CustomDetector] Failed to load model: {e}")
            return False
    
    def _compute_features(self, value, history):
        """
        Compute 8 features for a single metric.
        Features: value, rolling_mean, rolling_std, zscore, delta, delta_pct, rolling_max, max_ratio
        """
        history.append(value)
        
        if len(history) < 2:
            # Not enough data yet - return safe defaults
            return [value, value, 0, 0, 0, 0, value, 1.0]
        
        hist_array = np.array(history)
        
        # 1. value - current value
        val = float(value)
        
        # 2. rolling_mean - mean of window
        rolling_mean = float(np.mean(hist_array))
        
        # 3. rolling_std - std of window
        rolling_std = float(np.std(hist_array))
        if rolling_std < 0.01:
            rolling_std = 0.01  # Avoid division by zero
        
        # 4. zscore - how many std devs from mean
        zscore = (val - rolling_mean) / rolling_std
        
        # 5. delta - change from previous value
        delta = val - hist_array[-2]
        
        # 6. delta_pct - percent change from previous
        if hist_array[-2] > 0:
            delta_pct = (delta / hist_array[-2]) * 100
        else:
            delta_pct = 0
        
        # 7. rolling_max - max in window
        rolling_max = float(np.max(hist_array))
        
        # 8. max_ratio - current / max
        if rolling_max > 0:
            max_ratio = val / rolling_max
        else:
            max_ratio = 1.0
        
        return [val, rolling_mean, rolling_std, zscore, delta, delta_pct, rolling_max, max_ratio]
    
    def detect(self, metrics: dict) -> tuple:
        """
        Detect anomalies using your trained model.
        
        Returns: (verdict, confidence, model_scores)
        """
        if self.model is None:
            # Fallback if model not loaded
            return "safe", 0.5, {}
        
        try:
            # Extract CPU as primary metric (model trained on single metric)
            cpu = float(metrics.get('cpu_percent', 0))
            
            # Compute 8 features for CPU
            cpu_features = self._compute_features(cpu, self.cpu_history)
            
            # Create feature array (8 features)
            X = np.array([cpu_features])
            
            # Scale features
            X_scaled = self.scaler.transform(X)
            
            # Predict
            pred = self.model.predict(X_scaled)[0]  # 0=normal, 1=anomaly
            proba = self.model.predict_proba(X_scaled)[0]  # [P(normal), P(anomaly)]
            
            anomaly_prob = float(proba[1])
            
            # FIXED: Lower threshold for detection + extreme CPU override
            # If CPU is extremely high (>90%), always flag as anomaly
            if cpu > 90:
                verdict = "anomaly"
                confidence = 0.85  # High confidence for extreme CPU
            elif pred == 1 or anomaly_prob > 0.45:  # Lowered from 0.5 to 0.45
                verdict = "anomaly"
                confidence = max(anomaly_prob, 0.6)
            else:
                verdict = "safe"
                confidence = 1.0 - anomaly_prob
            
            model_scores = {
                'random_forest': anomaly_prob,
                'prediction': int(pred),
                'features_used': 8,
                'cpu_zscore': cpu_features[3]  # zscore feature
            }
            
            return verdict, confidence, model_scores
        
        except Exception as e:
            print(f"[CustomDetector] Detection error: {e}")
            return "safe", 0.5, {}


# Singleton instance
_custom_detector = None

def get_custom_detector() -> CustomDetector:
    """Get or create custom detector instance."""
    global _custom_detector
    if _custom_detector is None:
        _custom_detector = CustomDetector()
    return _custom_detector
