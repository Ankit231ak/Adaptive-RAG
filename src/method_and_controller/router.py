"""
Logistic Regression STOP/MORE Controller Router.
"""
import os
import pickle
from typing import Dict, List, Optional, Tuple, Any
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler


class ControllerRouter:
    """
    Binary Controller predicting P(MORE | X_5).
    Decides STOP (generate from top-5) or MORE (retrieve documents 6-10).
    """

    def __init__(self, tau: float = 0.5):
        self.tau = tau
        self.scaler = StandardScaler()
        self.model = GradientBoostingClassifier(n_estimators=100, max_depth=3, random_state=42)
        self.is_trained = False

    def train(self, feature_vectors: List[List[float]], labels: List[str]):
        """Train scaler + Logistic Regression model on training feature vectors and oracle labels."""
        if len(feature_vectors) == 0:
            return

        X = np.array(feature_vectors, dtype=np.float32)
        y = np.array([1 if lbl.upper() == "MORE" else 0 for lbl in labels], dtype=np.int32)

        # Check if single class present
        if len(np.unique(y)) < 2:
            # Not enough class diversity; skip fitting model, default to prior
            self.is_trained = False
            return

        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled, y)
        self.is_trained = True

    def predict_action(self, feature_vector: List[float]) -> Tuple[str, float]:
        """Predict STOP or MORE based on probability threshold tau."""
        if not self.is_trained:
            # Default to STOP when untrained
            return "STOP", 0.0

        X = np.array([feature_vector], dtype=np.float32)
        X_scaled = self.scaler.transform(X)
        p_more = float(self.model.predict_proba(X_scaled)[0][1])
        action = "MORE" if p_more >= self.tau else "STOP"
        return action, round(p_more, 4)

    def save(self, filepath: str):
        """Save model and scaler to disk."""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "wb") as f:
            pickle.dump({"scaler": self.scaler, "model": self.model, "tau": self.tau, "is_trained": self.is_trained}, f)

    def load(self, filepath: str):
        """Load model and scaler from disk."""
        with open(filepath, "rb") as f:
            data = pickle.load(f)
            self.scaler = data["scaler"]
            self.model = data["model"]
            self.tau = data.get("tau", 0.5)
            self.is_trained = data.get("is_trained", True)
