import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.common import load_config
from src.data_and_retrieval.loader import create_sample_dataset
from src.data_and_retrieval.embeddings import OllamaEmbeddingModel
from src.data_and_retrieval.retriever import DenseRetriever
from src.generation_and_eval.generator import GeneratorWrapper
from src.method_and_controller.router import ControllerRouter
from src.pipeline.adaptive_rag import AdaptiveRAGPipeline
import logging
logging.basicConfig(level=logging.ERROR)

def run_evaluation():
    print("Initializing Adaptive RAG Pipeline...")
    config = load_config()
    test_file = config["paths"]["raw_dev_data"]
    
    print("Loading 10 test questions from dev set...")
    questions, corpus = create_sample_dataset(raw_file_path=test_file, sample_size=50, seed=420 )
    
    print("Initializing components...")
    embedder = OllamaEmbeddingModel(model_name="qwen3-embedding:4b", dimension=4096)
    retriever = DenseRetriever(corpus=corpus, embedding_model=embedder)
    retriever.build_index()
    
    generator = GeneratorWrapper(config=config)
    
    router = ControllerRouter(tau=config["controller"]["tau"])
    router_path = os.path.join(config["paths"]["results_raw_dir"], "controller_router.pkl")
    print(router_path)
    if os.path.exists(router_path):
        router.load(router_path)
    else:
        print("Warning: ML model not found. Using untrained router.")
        
    pipeline = AdaptiveRAGPipeline(
        corpus=corpus,
        retriever=retriever,
        generator=generator,
        router=router,
        config=config
    )
    
    print(f"\nRunning Adaptive Pipeline on 20 test questions...")
    results = []
    for idx, q in enumerate(questions, 1):
        print(f"\nProcessing Q{idx}: {q.question[:50]}...")
        res = pipeline.run_single(q)
        results.append(res)
        print(f"  -> Predicted Action: {res.action_taken}")
        print(f"  -> F1 Score: {res.f1:.2f}")
    
    print("\n" + "="*50)
    print("EVALUATION RESULTS")
    print("="*50)
    
    total_f1 = sum(r.f1 for r in results)
    total_tokens = sum(r.input_tokens for r in results)
    stop_count = sum(1 for r in results if r.action_taken == "STOP")
    more_count = sum(1 for r in results if r.action_taken == "MORE")
    
    print(f"Average F1 Score:  {total_f1/len(results):.4f}")
    print(f"Total Input Tokens: {total_tokens}")
    print(f"Controller Decisions: {stop_count} STOPs, {more_count} MOREs")

if __name__ == "__main__":
    run_evaluation()
