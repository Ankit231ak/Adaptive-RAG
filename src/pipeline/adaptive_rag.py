"""
Integrated Adaptive RAG pipeline execution.
"""
from dataclasses import dataclass, asdict
from typing import Dict, List, Any
from src.data_and_retrieval import Corpus, Document, Retriever
from src.generation_and_eval import GeneratorWrapper, GeneratorOutput, normalize_answer, exact_match_score, f1_score
from src.method_and_controller import ControllerRouter, extract_evidence_features


@dataclass
class PipelineResult:
    question_id: str
    question: str
    gold_answer: str
    predicted_answer: str
    normalized_gold: str
    normalized_pred: str
    exact_match: bool
    f1: float
    precision: float
    recall: float
    retrieved_count: int
    latency_sec: float
    input_tokens: int
    output_tokens: int
    action_taken: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class AdaptiveRAGPipeline:
    def __init__(self, corpus: Corpus, generator_mode: str = "extractive_baseline"):
        self.corpus = corpus
        self.retriever = Retriever(corpus)
        self.generator = GeneratorWrapper(mode=generator_mode)
        self.router = ControllerRouter()

    def run_single(self, example: Any, initial_k: int = 5, maximum_k: int = 10) -> PipelineResult:
        docs = self.retriever.retrieve(query=example.question, context_doc_ids=example.context_doc_ids, top_k=initial_k)
        
        # Extract features and predict action
        features = extract_evidence_features(scores=[0.9, 0.8, 0.7, 0.6, 0.5])
        action, prob = self.router.predict_action(features.to_vector())

        if action == "MORE":
            docs = self.retriever.retrieve(query=example.question, context_doc_ids=example.context_doc_ids, top_k=maximum_k)

        gen_out: GeneratorOutput = self.generator.generate(question=example.question, context_docs=docs)

        norm_gold = normalize_answer(example.answer)
        norm_pred = normalize_answer(gen_out.answer)
        em = exact_match_score(gen_out.answer, example.answer)
        f1, prec, rec = f1_score(gen_out.answer, example.answer)

        return PipelineResult(
            question_id=example.id,
            question=example.question,
            gold_answer=example.answer,
            predicted_answer=gen_out.answer,
            normalized_gold=norm_gold,
            normalized_pred=norm_pred,
            exact_match=em,
            f1=round(f1, 4),
            precision=round(prec, 4),
            recall=round(rec, 4),
            retrieved_count=len(docs),
            latency_sec=gen_out.latency_sec,
            input_tokens=gen_out.input_tokens,
            output_tokens=gen_out.output_tokens,
            action_taken=action
        )
