"""
Logistic Regression STOP/MORE Controller Router.
Owner: Member A (Method & Controller - Deepak)
"""
from typing import Dict, List, Tuple, Any
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
import numpy as np


class ControllerRouter:
    """Logistic Regression classifier predicting P(MORE | evidence_features)."""
    def __init__(self, tau: float = 0.5):
        self.tau = tau
        self.scaler = StandardScaler()
        self.model = LogisticRegression(class_weight="balanced", max_iter=500)
        self.is_trained = False

    def train(self, feature_vectors: List[List[float]], labels: List[str]):
        """Train scaler + Logistic Regression model."""
        X = np.array(feature_vectors)
        y = np.array([1 if lbl == "MORE" else 0 for lbl in labels])
        
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled, y)
        self.is_trained = True

    def predict_action(self, feature_vector: List[float]) -> Tuple[str, float]:
        """Predict STOP or MORE based on probability threshold tau."""
        if not self.is_trained:
            # Untrained fallback: STOP action
            return "STOP", 0.0

        X = np.array([feature_vector])
        X_scaled = self.scaler.transform(X)
        p_more = float(self.model.predict_proba(X_scaled)[0][1])
        action = "MORE" if p_more >= self.tau else "STOP"
        return action, round(p_more, 4)
