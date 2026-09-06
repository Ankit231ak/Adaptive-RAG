"""
V1 Post-Retrieval Evidence State Features.
Owner: Member A (Method & Controller - Deepak)

Features extracted from top-5 retrieved documents:
1. Top-1 score (s1)
2. Mean score (mean(s1..s5))
3. Score std (std(s1..s5))
4. Top-1 to Top-2 margin (s1 - s2)
5. Score range (s1 - s5)
6. Max similarity (max similarity to query)
7. Mean pairwise redundancy (mean cosine similarity across docs)
"""
from dataclasses import dataclass, asdict
from typing import Dict, List, Any
import numpy as np


@dataclass
class EvidenceFeatures:
    top1_score: float
    mean_score: float
    score_std: float
    margin_top1_top2: float
    score_range: float
    max_similarity: float
    mean_redundancy: float

    def to_dict(self) -> Dict[str, float]:
        return asdict(self)

    def to_vector(self) -> List[float]:
        return [
            self.top1_score,
            self.mean_score,
            self.score_std,
            self.margin_top1_top2,
            self.score_range,
            self.max_similarity,
            self.mean_redundancy
        ]


def extract_evidence_features(scores: List[float], max_sim: float = 0.8, mean_red: float = 0.3) -> EvidenceFeatures:
    """Extract 7 V1 evidence features from scores list."""
    if not scores:
        return EvidenceFeatures(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)

    s1 = scores[0]
    s2 = scores[1] if len(scores) > 1 else s1
    s5 = scores[-1]

    mean_sc = float(np.mean(scores))
    std_sc = float(np.std(scores))
    margin = float(s1 - s2)
    sc_range = float(s1 - s5)

    return EvidenceFeatures(
        top1_score=round(s1, 4),
        mean_score=round(mean_sc, 4),
        score_std=round(std_sc, 4),
        margin_top1_top2=round(margin, 4),
        score_range=round(sc_range, 4),
        max_similarity=round(max_sim, 4),
        mean_redundancy=round(mean_red, 4)
    )
