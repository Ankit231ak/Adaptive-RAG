"""
Adaptive RAG — Main Hello-World Skeleton Runner
One-command executable demonstrating modular end-to-end pipeline execution.
"""
import json
import os
import subprocess
import sys
from typing import Dict, Any

from src.common import load_config, set_seed
from src.data_and_retrieval import create_sample_dataset
from src.generation_and_eval import evaluate_predictions
from src.pipeline import AdaptiveRAGPipeline


def get_git_commit_hash() -> str:
    try:
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL).decode("utf-8").strip()
        return commit
    except Exception:
        return "git_commit_hash_unavailable"


def main():
    print("=========================================================================")
    print("        ADAPTIVE RAG — HELLO-WORLD SKELETON PIPELINE RUNNER            ")
    print("=========================================================================\n")

    config = load_config("configs/base.yaml")
    seed = config.get("seed", 42)
    set_seed(seed)

    commit_hash = get_git_commit_hash()
    print(f"• Git Commit Hash   : {commit_hash}")
    print(f"• Fixed Team Roles  : Member A (Deepak - Method), Member B (Ankit - Data), Member C (Utsav - Eval)")
    print(f"• Configuration Path: configs/base.yaml (Seed: {seed})\n")

    raw_data_path = config["paths"]["raw_dev_data"]
    sample_size = config["sample"]["tiny_sample_size"]

    print(f"Loading tiny sample dataset ({sample_size} examples)...")
    examples, corpus = create_sample_dataset(raw_file_path=raw_data_path, sample_size=sample_size, seed=seed)
    print(f"✔ Dataset loaded: {len(examples)} questions, {len(corpus)} corpus documents.\n")

    pipeline = AdaptiveRAGPipeline(corpus=corpus, generator_mode="extractive_baseline")

    results = []
    predictions = []
    ground_truths = []

    print("Running end-to-end pipeline over questions...")
    for ex in examples:
        res = pipeline.run_single(ex)
        results.append(res)
        predictions.append(res.predicted_answer)
        ground_truths.append(res.gold_answer)

    overall_metrics = evaluate_predictions(predictions, ground_truths)

    print("\n-------------------------------------------------------------------------")
    print("                    EVALUATION METRICS SUMMARY                           ")
    print("-------------------------------------------------------------------------")
    print(f"• Total Evaluated Questions : {overall_metrics['total_samples']}")
    print(f"• Exact Match (EM)          : {overall_metrics['exact_match'] * 100:.2f}%")
    print(f"• Token-Level F1            : {overall_metrics['f1'] * 100:.2f}%")
    print(f"• Token-Level Precision     : {overall_metrics['precision'] * 100:.2f}%")
    print(f"• Token-Level Recall        : {overall_metrics['recall'] * 100:.2f}%")
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
    print(f"Retrieved Docs : {sample_res.retrieved_count} | Action: {sample_res.action_taken}")
    print("-------------------------------------------------------------------------\n")

    results_dir = os.path.join("results", "raw")
    os.makedirs(results_dir, exist_ok=True)
    evidence_file = os.path.join(results_dir, "hello_world_run.json")

    evidence_data: Dict[str, Any] = {
        "commit_hash": commit_hash,
        "team_roles": {
            "Member_A": "Deepak — Method & Controller",
            "Member_B": "Ankit — Data & Retrieval",
            "Member_C": "Utsav — Generation & Evaluation"
        },
        "config": config,
        "metrics": overall_metrics,
        "sample_run": [r.to_dict() for r in results]
    }

    with open(evidence_file, "w", encoding="utf-8") as f:
        json.dump(evidence_data, f, indent=2)

    print(f"✔ Saved run evidence to: {evidence_file}")
    print("=========================================================================\n")


if __name__ == "__main__":
    main()
