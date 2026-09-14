import sys
import os
import time
import json
import logging
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.common import load_config
from src.data_and_retrieval import create_sample_dataset, DenseRetriever, OllamaEmbeddingModel
from src.generation_and_eval import GeneratorWrapper
from src.method_and_controller import ControllerRouter, extract_evidence_features

logging.basicConfig(level=logging.ERROR)

CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
MAGENTA = "\033[95m"
WHITE = "\033[97m"
RESET = "\033[0m"
BOLD = "\033[1m"

def run_demo():
    print(CYAN + BOLD + "\n" + "="*70)
    print("   ADAPTIVE RAG PIPELINE VISUALIZATION DEMO (GRADIENT BOOSTING)")
    print("="*70 + RESET + "\n")
    
    config = load_config()
    test_file = config["paths"]["raw_dev_data"]
    
    print(YELLOW + "[1] Initializing Pipeline Components..." + RESET)
    questions, corpus = create_sample_dataset(test_file, sample_size=10, seed=123)
    embedder = OllamaEmbeddingModel(model_name="qwen3-embedding:4b", dimension=4096)
    retriever = DenseRetriever(corpus=corpus, embedding_model=embedder)
    retriever.build_index()
    generator = GeneratorWrapper(config=config)
    router = ControllerRouter(tau=config["controller"]["tau"])
    router.load(os.path.join(config["paths"]["results_raw_dir"], "controller_router.pkl"))
    
    print(YELLOW + "\n[2] Pipeline Ready! Processing a random query:\n" + RESET)
    q = questions[4]
    print(WHITE + BOLD + f"USER QUERY: {q.question}\n" + RESET)
    
    time.sleep(1)
    print(GREEN + "--- STEP 1: INITIAL RETRIEVAL (k=5) ---" + RESET)
    start_time = time.time()
    query_emb = embedder.embed_query(q.question)
    top5_docs = retriever.retrieve(q.question, top_k=5, candidate_doc_ids=q.context_doc_ids)
    print(f"Retrieved 5 documents in {time.time() - start_time:.2f} seconds.")
    
    time.sleep(1)
    print(GREEN + "\n--- STEP 2: EVIDENCE STATE EXTRACTION ---" + RESET)
    scores = [rd.score for rd in top5_docs]
    doc_embs = np.array([rd.embedding for rd in top5_docs if rd.embedding is not None], dtype=np.float32)
    feat = extract_evidence_features(scores, doc_embs, query_emb)
    
    print(WHITE + "Mathematical Feature State:")
    print(f"  • Top-1 Score:      {feat.top1_score:.4f}")
    print(f"  • Mean Score:       {feat.mean_score:.4f}")
    print(f"  • Score Range:      {feat.score_range:.4f}")
    print(f"  • Mean Redundancy:  {feat.mean_redundancy:.4f}" + RESET)
    
    time.sleep(1)
    print(MAGENTA + BOLD + "\n--- STEP 3: ML CONTROLLER ROUTING ---" + RESET)
    features_list = [feat.top1_score, feat.mean_score, feat.score_std, feat.margin_top1_top2, feat.score_range, feat.max_similarity, feat.mean_redundancy]
    action, prob = router.predict_action(features_list)
    
    print(MAGENTA + f"Gradient Boosting Model analyzing 7 features..." + RESET)
    time.sleep(1)
    
    if action == "STOP":
        print(CYAN + BOLD + f"-> PREDICTION: [STOP] (Confidence: {1.0 - prob:.1%})")
        print("-> REASON: Evidence is highly confident. Skipping deep retrieval to prevent distractors and save tokens." + RESET)
        final_docs = top5_docs
    else:
        print(RED + BOLD + f"-> PREDICTION: [MORE] (Confidence: {prob:.1%})")
        print("-> REASON: Evidence is weak or ambiguous. Triggering deeper retrieval (k=10)." + RESET)
        print(GREEN + "\n--- STEP 3.5: DEEP RETRIEVAL (k=10) ---" + RESET)
        final_docs = retriever.retrieve(q.question, top_k=10, candidate_doc_ids=q.context_doc_ids)
        
    time.sleep(1)
    print(GREEN + "\n--- STEP 4: LLM GENERATION ---" + RESET)
    pass # context = "\n".join([f"Doc {i+1}: {d.doc.text}" for i, d in enumerate(final_docs)])
    print(f"Sending {len(final_docs)} documents to Qwen2.5:7b...")
    
    gen_start = time.time()
    docs_only = [rd.doc for rd in final_docs]
    gen_out = generator.generate(q.question, docs_only)
    
    print(WHITE + BOLD + f"\n[FINAL ANSWER]: {gen_out.answer}" + RESET)
    print(YELLOW + f"\nPipeline Complete. Total Time: {time.time() - start_time:.2f}s | Tokens Consumed: {gen_out.input_tokens + gen_out.output_tokens}" + RESET)

if __name__ == "__main__":
    run_demo()
