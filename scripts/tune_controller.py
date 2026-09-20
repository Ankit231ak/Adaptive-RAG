import sys
import os
import json
import logging
from typing import List, Dict, Any
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import GridSearchCV, train_test_split
import joblib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    print("\n" + "="*50)
    print("HYPERPARAMETER TUNING - GRADIENT BOOSTING")
    print("="*50)

    # 1. Load Oracle Labels
    oracle_path = "results/raw/oracle_labels.json"
    if not os.path.exists(oracle_path):
        print(f"Error: Could not find {oracle_path}")
        return
    with open(oracle_path, "r") as f:
        oracle_data = json.load(f)
    # create a lookup dictionary
    oracle_lookup = {r["question_id"]: r["oracle_label"] for r in oracle_data}

    # 2. Load Features
    data_path = "results/raw/evidence_features_day6.jsonl"
    if not os.path.exists(data_path):
        print(f"Error: Could not find {data_path}")
        return

    features = []
    labels = []
    
    with open(data_path, "r") as f:
        for line in f:
            record = json.loads(line)
            qid = record["question_id"]
            if qid not in oracle_lookup:
                continue
                
            feat = [
                record["top1_score"],
                record["mean_score"],
                record["score_std"],
                record["margin_top1_top2"],
                record["score_range"],
                record["max_similarity"],
                record["mean_redundancy"]
            ]
            features.append(feat)
            labels.append(1 if oracle_lookup[qid] == "MORE" else 0)

    print(f"Loaded {len(features)} queries for tuning.")

    # Split data exactly like we did before (80/20)
    X_train, X_test, y_train, y_test = train_test_split(
        features, labels, test_size=0.2, random_state=42
    )

    # Define the parameter grid to test
    param_grid = {
        'n_estimators': [50, 100, 200, 300],
        'learning_rate': [0.01, 0.05, 0.1, 0.2],
        'max_depth': [2, 3, 5],
        'min_samples_split': [2, 5, 10]
    }

    print("\nStarting Grid Search for the perfect parameters...")
    print("Testing 144 different combinations. This will only take about 15 seconds!")
    
    base_model = GradientBoostingClassifier(random_state=42)
    
    # 5-fold cross validation
    grid_search = GridSearchCV(
        estimator=base_model,
        param_grid=param_grid,
        cv=5,
        n_jobs=-1,
        scoring='accuracy',
        verbose=1
    )
    
    grid_search.fit(X_train, y_train)

    print("\n" + "="*50)
    print("TUNING COMPLETE!")
    print("="*50)
    print(f"Old Default Model Accuracy: ~86.0%")
    print(f"New Perfect Model Cross-Validation Accuracy: {grid_search.best_score_:.2%}")
    print("\nThe mathematically PERFECT parameters are:")
    for param, value in grid_search.best_params_.items():
        print(f"  -> {param}: {value}")

    best_model = grid_search.best_estimator_
    test_acc = best_model.score(X_test, y_test)
    print(f"\nFinal Accuracy on Unseen Test Data: {test_acc:.2%}")

    save_path = "results/raw/controller_router.pkl"
    joblib.dump(best_model, save_path)
    print(f"\nSuccessfully overwrote '{save_path}' with the perfectly tuned model!")

if __name__ == "__main__":
    main()
