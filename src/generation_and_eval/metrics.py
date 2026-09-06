"""
Evaluation metrics and answer normalization for HotpotQA.
Owner: Member C (Generation & Evaluation - Utsav)
"""
from collections import Counter
import re
import string
from typing import Dict, List, Tuple


def normalize_answer(s: str) -> str:
    def remove_articles(text: str) -> str:
        return re.sub(r'\b(a|an|the)\b', ' ', text)

    def white_space_fix(text: str) -> str:
        return ' '.join(text.split())

    def remove_punc(text: str) -> str:
        exclude = set(string.punctuation)
        return ''.join(ch for ch in text if ch not in exclude)

    def lower(text: str) -> str:
        return text.lower()

    return white_space_fix(remove_articles(remove_punc(lower(str(s)))))


def exact_match_score(prediction: str, ground_truth: str) -> bool:
    return normalize_answer(prediction) == normalize_answer(ground_truth)


def f1_score(prediction: str, ground_truth: str) -> Tuple[float, float, float]:
    normalized_prediction = normalize_answer(prediction)
    normalized_ground_truth = normalize_answer(ground_truth)

    ZERO_METRICS = (0.0, 0.0, 0.0)

    if normalized_prediction in ['yes', 'no', 'noanswer'] and normalized_prediction != normalized_ground_truth:
        return ZERO_METRICS
    if normalized_ground_truth in ['yes', 'no', 'noanswer'] and normalized_prediction != normalized_ground_truth:
        return ZERO_METRICS

    prediction_tokens = normalized_prediction.split()
    ground_truth_tokens = normalized_ground_truth.split()

    if not prediction_tokens or not ground_truth_tokens:
        is_exact = (prediction_tokens == ground_truth_tokens)
        score = 1.0 if is_exact else 0.0
        return (score, score, score)

    common = Counter(prediction_tokens) & Counter(ground_truth_tokens)
    num_same = sum(common.values())

    if num_same == 0:
        return ZERO_METRICS

    precision = 1.0 * num_same / len(prediction_tokens)
    recall = 1.0 * num_same / len(ground_truth_tokens)
    f1 = (2 * precision * recall) / (precision + recall)
    return (f1, precision, recall)


def evaluate_predictions(predictions: List[str], ground_truths: List[str]) -> Dict[str, float]:
    if len(predictions) != len(ground_truths):
        raise ValueError(f"Mismatch in length: {len(predictions)} predictions vs {len(ground_truths)} ground truths.")

    total = len(predictions)
    if total == 0:
        return {"exact_match": 0.0, "f1": 0.0, "precision": 0.0, "recall": 0.0}

    em_total = 0.0
    f1_total = 0.0
    prec_total = 0.0
    rec_total = 0.0

    for pred, gt in zip(predictions, ground_truths):
        em_total += 1.0 if exact_match_score(pred, gt) else 0.0
        f1, prec, rec = f1_score(pred, gt)
        f1_total += f1
        prec_total += prec
        rec_total += rec

    return {
        "exact_match": round(em_total / total, 4),
        "f1": round(f1_total / total, 4),
        "precision": round(prec_total / total, 4),
        "recall": round(rec_total / total, 4),
        "total_samples": total
    }
