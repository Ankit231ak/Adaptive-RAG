import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.common import load_config
from src.method_and_controller import ControllerRouter

def train_controller():
    print("Training ML Controller Router...")
    config = load_config()
    raw_dir = config["paths"]["results_raw_dir"]
    
    # Load Oracle Labels
    oracle_path = os.path.join(raw_dir, "oracle_labels.json")
    with open(oracle_path, "r") as f:
        oracle_data = {item["question_id"]: item["oracle_label"] for item in json.load(f)}
        
    # Load Evidence Features (Day 6)
    features_path = os.path.join(raw_dir, "evidence_features_day6.jsonl")
    
    feature_vectors = []
    labels = []
    
    with open(features_path, "r") as f:
        for line in f:
            data = json.loads(line)
            q_id = data["question_id"]
            if q_id in oracle_data:
                # Extract the 7 features in the exact order documented in FEATURE_DICTIONARY.md
                features = [
                    data["top1_score"],
                    data["mean_score"],
                    data["score_std"],
                    data["margin_top1_top2"],
                    data["score_range"],
                    data["max_similarity"],
                    data["mean_redundancy"]
                ]
                feature_vectors.append(features)
                labels.append(oracle_data[q_id])
                
    print(f"Loaded {len(feature_vectors)} feature vectors.")
    
    # Initialize and Train Router
    tau = config["controller"]["tau"]
    router = ControllerRouter(tau=tau)
    router.train(feature_vectors, labels)
    
    if router.is_trained:
        print(f"Gradient Boosting Model successfully trained!")
        
        # Calculate Train Accuracy
        correct = 0
        for features, true_label in zip(feature_vectors, labels):
            pred_label, _ = router.predict_action(features)
            if pred_label == true_label:
                correct += 1
                
        print(f"Training Accuracy: {(correct/len(labels))*100:.2f}%")
        
        # Save Model
        model_path = os.path.join(raw_dir, "controller_router.pkl")
        router.save(model_path)
        print(f"Model saved to {model_path}")
    else:
        print("Failed to train model. Ensure class diversity (both STOP and MORE labels exist).")

if __name__ == "__main__":
    train_controller()
