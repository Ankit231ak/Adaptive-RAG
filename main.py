"""
Adaptive RAG — Main Pipeline Runner (Days 1 - 6 Integrated Runner).
One-command executable demonstrating end-to-end FAISS dense retrieval,
evidence-state feature extraction, Ollama model interface, and evaluation.
"""
import json
import os
import subprocess
import sys
from typing import Dict, Any

from src import load_config, set_seed
from src.data_and_retrieval import create_sample_dataset, DenseRetriever
from src import evaluate_predictions, GeneratorWrapper
from src.pipeline import AdaptiveRAGPipeline


def get_git_commit_hash() -> str:
    try:
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL).decode("utf-8").strip()
        return commit
    except Exception:
        return "git_commit_hash_unavailable"


def main():
    print("=========================================================================")
    print("        ADAPTIVE RAG — PIPELINE RUNNER (DAYS 1 - 6 INTEGRATED)           ")
    print("=========================================================================\n")

    config = load_config("configs/base.yaml")
    seed = config.get("seed", 42)
    set_seed(seed)

    commit_hash = get_git_commit_hash()
    print(f"• Git Commit Hash   : {commit_hash}")
    print(f"• Fixed Team Roles  : Member A (Deepak - Method), Member B (Ankit - Data), Member C (Utsav - Eval)")
    print(f"• Configuration Path: configs/base.yaml (Seed: {seed})")
    
    gen_model = config.get("generator", {}).get("model_name", "")
    print(f"• Ollama Generator  : {'Model: ' + gen_model if gen_model else 'Unset (Space reserved for user, using deterministic fallback)'}")
    print(f"• Vector Index      : FAISS Dense Index (Inner Product Cosine)\n")

    raw_data_path = config["paths"]["raw_dev_data"]
    sample_size = config["sample"]["tiny_sample_size"]

    print(f"Loading dataset ({sample_size} examples)...")
    examples, corpus = create_sample_dataset(raw_file_path=raw_data_path, sample_size=sample_size, seed=seed)
    print(f"✔ Dataset loaded: {len(examples)} questions, {len(corpus)} corpus documents.\n")

    print("Building dense embeddings and FAISS index...")
    retriever = DenseRetriever(corpus=corpus, config=config)
    retriever.build_index()

    generator = GeneratorWrapper(config=config)
    pipeline = AdaptiveRAGPipeline(
        corpus=corpus,
        retriever=retriever,
        generator=generator,
        activate_adaptation=True,
        config=config
    )

    results = []
    predictions = []
    ground_truths = []

    print("\nRunning end-to-end adaptive pipeline over questions...")
    for ex in examples:
        res = pipeline.run_single(ex)
        results.append(res)
        predictions.append(res.predicted_answer)
        ground_truths.append(res.gold_answer)

    overall_metrics = evaluate_predictions(predictions, ground_truths)

    avg_latency = float(sum(r.total_latency for r in results) / len(results))
    avg_tokens = float(sum(r.input_tokens + r.output_tokens for r in results) / len(results))
    avg_docs = float(sum(r.retrieved_count for r in results) / len(results))
    avg_recall = float(sum(r.recall_at_retrieved for r in results) / len(results))
    avg_mrr = float(sum(r.mrr for r in results) / len(results))

    print("\n-------------------------------------------------------------------------")
    print("                    EVALUATION METRICS SUMMARY                           ")
    print("-------------------------------------------------------------------------")
    print(f"• Total Evaluated Questions : {overall_metrics['total_samples']}")
    print(f"• Exact Match (EM)          : {overall_metrics['exact_match'] * 100:.2f}%")
    print(f"• Token-Level F1            : {overall_metrics['f1'] * 100:.2f}%")
    print(f"• Retrieval Recall          : {avg_recall:.4f}")
    print(f"• Mean Reciprocal Rank(MRR) : {avg_mrr:.4f}")
    print(f"• Average Retrieved Docs    : {avg_docs:.1f}")
    print(f"• Average Total Latency     : {avg_latency:.4f}s")
    print(f"• Average Total Tokens      : {avg_tokens:.1f}")
    print("-------------------------------------------------------------------------\n")

    sample_res = results[0]
    print("-------------------------------------------------------------------------")
    print("                   SAMPLE INPUT / OUTPUT EVIDENCE                       ")
    print("-------------------------------------------------------------------------")
    print(f"Question ID    : {sample_res.question_id}")
    print(f"Question       : {sample_res.question}")
    print(f"Gold Answer    : {sample_res.gold_answer} (Normalized: '{sample_res.normalized_gold}')")
    print(f"Predicted      : {sample_res.predicted_answer} (Normalized: '{sample_res.normalized_pred}')")
    print(f"EM Match       : {sample_res.exact_match} | F1: {sample_res.f1}")
    print(f"Retrieved Docs : {sample_res.retrieved_count} | Action: {sample_res.action_taken} (P(MORE): {sample_res.p_more})")
    print(f"7 V1 Features  : {sample_res.evidence_features}")
    print("-------------------------------------------------------------------------\n")

    results_dir = os.path.join("results", "raw")
    os.makedirs(results_dir, exist_ok=True)
    evidence_file = os.path.join(results_dir, "integrated_run_day6.json")

    evidence_data: Dict[str, Any] = {
        "commit_hash": commit_hash,
        "team_roles": {
            "Member_A": "Deepak — Method & Controller",
            "Member_B": "Ankit — Data & Retrieval",
            "Member_C": "Utsav — Generation & Evaluation"
        },
        "config": config,
        "metrics": {
            **overall_metrics,
            "avg_latency": round(avg_latency, 4),
            "avg_tokens": round(avg_tokens, 1),
            "avg_docs": round(avg_docs, 1),
            "retrieval_recall": round(avg_recall, 4),
            "mrr": round(avg_mrr, 4)
        },
        "sample_run": [r.to_dict() for r in results]
    }

    with open(evidence_file, "w", encoding="utf-8") as f:
        json.dump(evidence_data, f, indent=2)

    print(f"✔ Saved run evidence to: {evidence_file}")
    print("=========================================================================\n")


if __name__ == "__main__":
    main()
