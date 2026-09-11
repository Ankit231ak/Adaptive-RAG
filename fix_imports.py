import os

files_to_fix = [
    "src/pipeline/adaptive_rag.py",
    "src/pipeline/baselines.py"
]

for file_path in files_to_fix:
    with open(file_path, "r") as f:
        content = f.read()
    
    # Replace the data_and_retrieval imports
    content = content.replace(
        "from src import Corpus, Document, DenseRetriever, RetrievedDoc",
        "from src.data_and_retrieval import Corpus, Document, DenseRetriever, RetrievedDoc"
    )
    
    # Replace the generation_and_eval imports
    content = content.replace(
        "from src import (\n    GeneratorWrapper,\n    GeneratorOutput,\n    normalize_answer,\n    exact_match_score,\n    f1_score,\n    recall_at_k,\n    mrr_at_k,\n    supporting_fact_coverage\n)",
        "from src.generation_and_eval import (\n    GeneratorWrapper,\n    GeneratorOutput,\n    normalize_answer,\n    exact_match_score,\n    f1_score,\n    recall_at_k,\n    mrr_at_k,\n    supporting_fact_coverage\n)"
    )
    content = content.replace(
        "from src import GeneratorWrapper, evaluate_predictions",
        "from src.generation_and_eval import GeneratorWrapper, evaluate_predictions"
    )
    
    # Replace method_and_controller imports
    content = content.replace(
        "from src import ControllerRouter, extract_evidence_features",
        "from src.method_and_controller import ControllerRouter, extract_evidence_features"
    )
    
    with open(file_path, "w") as f:
        f.write(content)

print("Fixed")
