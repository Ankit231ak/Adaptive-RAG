"""
Oracle labelling logic for training controller.
Owner: Member A (Method & Controller - Deepak)

Computes delta-F1 = F1@10 - F1@5 and labels MORE if delta-F1 > delta_threshold, else STOP.
"""
from typing import Tuple


def compute_oracle_label(f1_d5: float, f1_d10: float, delta_threshold: float = 0.05) -> Tuple[str, float]:
    """
    Compute oracle label based on marginal improvement delta F1.
    """
    delta_f1 = f1_d10 - f1_d5
    label = "MORE" if delta_f1 > delta_threshold else "STOP"
    return label, round(delta_f1, 4)
