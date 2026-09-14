import sys
import os
import time
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
    print("   ADAPTIVE RAG PIPELINE - MANUAL QUERY DEMO (GRADIENT BOOSTING)")
    print("="*70 + RESET + "\n")
    
    config = load_config()
    test_file = config["paths"]["raw_dev_data"]
    
    print(YELLOW + "[1] Initializing Pipeline Components..." + RESET)
    # Load 50 random unseen questions just to show the user some examples
    questions, corpus = create_sample_dataset(test_file, sample_size=50, seed=999)
    embedder = OllamaEmbeddingModel(model_name="qwen3-embedding:4b", dimension=4096)
    retriever = DenseRetriever(corpus=corpus, embedding_model=embedder)
    retriever.build_index()
    generator = GeneratorWrapper(config=config)
    router = ControllerRouter(tau=config["controller"]["tau"])
    router.load(os.path.join(config["paths"]["results_raw_dir"], "controller_router.pkl"))
    
    print(YELLOW + "\n[2] Pipeline Ready!\n" + RESET)
    print("Here are 3 example questions from the unseen dataset you can try:")
    print(f"  1. {questions[11].question}")
    print(f"  2. {questions[22].question}")
    print(f"  3. {questions[33].question}\n")
    
    user_q = input(WHITE + BOLD + "Enter your custom question (or press Enter for a random one): " + RESET).strip()
    
    if not user_q:
        q_obj = questions[44]
        user_q = q_obj.question
        print(CYAN + f"\nUsing random question: {user_q}" + RESET)
    
    print(GREEN + "\n--- STEP 1: INITIAL RETRIEVAL (k=5) ---" + RESET)
    start_time = time.time()
    query_emb = embedder.embed_query(user_q)
    # Retrieve without candidate IDs so it searches the full FAISS database
    top5_docs = retriever.retrieve(user_q, top_k=5)
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
        final_docs = retriever.retrieve(user_q, top_k=10)
        
    time.sleep(1)
    print(GREEN + "\n--- STEP 4: LLM GENERATION ---" + RESET)
    docs_only = [rd.doc for rd in final_docs]
    print(f"Sending {len(final_docs)} documents to Qwen2.5:7b...")
    
    gen_start = time.time()
    gen_out = generator.generate(user_q, docs_only)
    
    print(WHITE + BOLD + f"\n[FINAL ANSWER]: {gen_out.answer}" + RESET)
    total_tokens = gen_out.input_tokens + gen_out.output_tokens
    print(YELLOW + f"\nPipeline Complete. Total Time: {time.time() - start_time:.2f}s | Tokens Consumed: {total_tokens}" + RESET)

if __name__ == "__main__":
    run_demo()
