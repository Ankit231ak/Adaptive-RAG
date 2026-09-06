"""
Adaptive RAG Package — Modular Architecture
"""
from src.common import load_config, set_seed
from src.data_and_retrieval import Corpus, Document, Retriever, create_sample_dataset
from src.generation_and_eval import GeneratorWrapper, evaluate_predictions, normalize_answer
from src.method_and_controller import ControllerRouter, EvidenceFeatures, extract_evidence_features
from src.pipeline import AdaptiveRAGPipeline

__all__ = [
    "load_config",
    "set_seed",
    "Corpus",
    "Document",
    "Retriever",
    "create_sample_dataset",
    "GeneratorWrapper",
    "evaluate_predictions",
    "normalize_answer",
    "ControllerRouter",
    "EvidenceFeatures",
    "extract_evidence_features",
    "AdaptiveRAGPipeline"
]
