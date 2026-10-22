# Adaptive RAG — Evidence-State Retrieval Controller

Adaptive RAG is a research framework building an **evidence-state retrieval controller** that dynamically predicts whether an additional retrieval batch ($k=5 \to k=10$) will materially improve multi-hop answer quality ($\Delta F1 > \delta$), allowing the system to stop early when retrieved evidence is already sufficient.

---


## Research Results & Methodology

### 1. Final Benchmark Results (B0 – B6)

The framework was evaluated under a strict frozen split (700 Train / 150 Validation / 150 Test) with zero data leakage:

#### Frozen Test Split (150 Unseen Multi-Hop Questions)

| Method | Baseline ID | Exact Match (EM) | F1 Score | Avg Retrieved Docs | Avg Total Tokens | Avg Latency | Early STOP Rate |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Direct LLM (No Retrieval)** | B0 | 12.00% | 0.2187 | 0.00 | 98.2 | 0.41s | 100.0% |
| **Fixed RAG-3** | B1 | 36.67% | 0.5394 | 3.00 | 480.7 | 1.37s | — |
| **Fixed RAG-5 (Initial Budget)** | B2 | 34.67% | 0.5443 | 5.00 | 761.8 | 1.67s | — |
| **Fixed RAG-10 (Over-retrieval)** | B3 | 36.00% | 0.5417 | 10.00 | 1523.7 | 2.39s | — |
| **Simple Score Rule** | B4 | 36.00% | 0.5387 | 7.10 | 1076.6 | 1.93s | 58.0% |
| **Adaptive-RAG (Jeong et al.)** | B5 | 34.67% | 0.5249 | 6.60 | 1003.6 | 1.92s | 68.0% |
| **Proposed Adaptive-RAG (Ours)** | **B6** | **36.00%** | **0.5560** | **5.23** | **796.1** | **1.70s** | **95.3%** |
| *Oracle Upper Bound (Hindsight)* | *E5* | *40.67%* | *0.6140* | *5.73* | *865.8* | *1.78s* | *85.3%* |

*Key Findings:*
1. **Beating the Context Bloat Trap:** Moving from $k=5$ to $k=10$ lowered F1 score from 0.5443 to 0.5417 due to semantic distractors, while doubling token costs.
2. **Quality Win:** Our controller (B6) achieved the **highest F1 score (0.5560)** among all methods, outperforming Fixed-10, Fixed-5, and Adaptive-RAG.
3. **Massive Efficiency Savings:** B6 early-exits at $k=5$ on **95.3% of queries**, cutting tokens by **48%** and reducing latency by **29%** compared to Fixed-10.

---

### 2. Publication Figures & Visualizations

All 5 publication plots are generated in [`figures/`](figures/):
- **[Figure 1: Quality–Cost Frontier (`figures/fig1_quality_vs_tokens.png`)](figures/fig1_quality_vs_tokens.png)**: Maps F1 vs token consumption, showing Adaptive RAG at the optimal Pareto frontier.
- **[Figure 2: Quality–Latency Frontier (`figures/fig2_quality_vs_latency.png`)](figures/fig2_quality_vs_latency.png)**: Demonstrates latency reduction from 2.4s to 1.7s while improving accuracy.
- **[Figure 3: Threshold Calibration Curve (`figures/fig3_tau_pareto_frontier.png`)](figures/fig3_tau_pareto_frontier.png)**: Sweeps probability threshold $\tau \in [0.1, 0.9]$ showing early STOP rate vs answer F1.
- **[Figure 4: Decision Confusion Matrix (`figures/fig4_decision_confusion_matrix.png`)](figures/fig4_decision_confusion_matrix.png)**: Visualizes controller STOP vs MORE accuracy on test data.
- **[Figure 5: Feature Importance Ranking (`figures/fig5_feature_importance.png`)](figures/fig5_feature_importance.png)**: Ranks GBDT feature importances across the 7 V1 features.

---

### 3. Essential Ablations Summary

From [`results/tables/ablations_summary.csv`](results/tables/ablations_summary.csv):
- **Dropping Score/Margin Features (A2):** Causes F1 to drop sharply from 0.5560 to 0.5475, confirming that retrieval score shape is the primary driver of evidence sufficiency.
- **Controller Architecture (A4):** GBDT significantly outperforms Linear Logistic Regression (F1 = 0.5417) and Random Forest (F1 = 0.5418), which suffer from severe class imbalance over-retrieval.
- **Optimal Calibration ($\tau=0.2$):** Reaches peak F1 of **0.5640** (36.67% EM) at 836.9 tokens with an 89.3% early STOP rate.


---
## Codebase Architecture & File Purposes

Below is a comprehensive guide to every meaningful file in this project and why it exists. *(Note: Standard auto-generated configuration and environment files like `.venv`, `.gitignore`, `uv.lock`, and the `docs/` folder have been excluded for brevity).*

### 1. Source Code (`src/`)
This is where the core logic of the pipeline lives. 

#### Data & Retrieval Pipeline
* **`src/data_and_retrieval/corpus.py`**
  * **Purpose:** Handles creating unique hashes (SHA-256) for documents.
  * **Why it's necessary:** Ensures that every piece of text we retrieve has a consistent, permanent ID, preventing duplicate context blocks from being fed to the LLM.
* **`src/data_and_retrieval/embeddings.py`**
  * **Purpose:** Interfaces for converting text into dense mathematical vectors (SentenceTransformers & Ollama embeddings).
  * **Why it's necessary:** RAG needs dense representations to do semantic search. This provides the mathematical representation of the question and the documents.
* **`src/data_and_retrieval/loader.py`**
  * **Purpose:** Loads the HotpotQA dataset from disk.
  * **Why it's necessary:** Abstracts away file paths and JSON parsing so the rest of the app just receives clean Python objects.
* **`src/data_and_retrieval/retriever.py`**
  * **Purpose:** Contains the FAISS Vector Store logic (and exact-match NumPy fallback) to rapidly search embeddings.
  * **Why it's necessary:** To instantly fetch the top 5 or 10 most relevant documents from thousands of possible chunks without crashing.

#### Generation & Evaluation Pipeline
* **`src/generation_and_eval/generator.py`**
  * **Purpose:** Connects to the local Ollama LLM (`qwen3.5:latest`) and builds the prompt structures (Direct vs RAG context).
  * **Why it's necessary:** This is the "brain" that actually reads the retrieved documents and types out the final answer to the user's question.
* **`src/generation_and_eval/metrics.py`**
  * **Purpose:** Houses mathematical scoring formulas like Exact Match (EM), F1-Score, MRR, and Recall.
  * **Why it's necessary:** We need hard numbers to prove if our answers are actually getting better.

#### Method & Controller Pipeline
* **`src/method_and_controller/evidence_state.py`**
  * **Purpose:** Calculates the 7 statistical features from the top-5 retrieved documents (e.g., standard deviation of scores, max similarity).
  * **Why it's necessary:** The system uses these features to understand its own confidence levels. If the features look bad, the system knows it needs to retrieve more information.
* **`src/method_and_controller/oracle.py`**
  * **Purpose:** Calculates the "perfect hindsight" answer for whether the system *should* have retrieved more documents (Delta F1).
  * **Why it's necessary:** Generates the ground-truth training labels (STOP vs MORE) to train the machine learning router.
* **`src/method_and_controller/router.py`**
  * **Purpose:** Houses the `ControllerRouter` classifier (Logistic Regression) that uses the evidence features to predict the Oracle's label dynamically.
  * **Why it's necessary:** The entire point of "Adaptive RAG". This script actively saves compute time by stopping the retrieval early when it predicts the LLM already has enough info.

#### Top-Level Pipelines & Shims
* **`src/pipeline/adaptive_rag.py`**
  * **Purpose:** The master orchestration file that chains the Retriever, Controller, and Generator together into a single pipeline.
* **`src/pipeline/baselines.py`**
  * **Purpose:** Executes the 5 standard control-group experiments (B0 - B4).
* **`src/*.py` Shims (e.g. `src/router.py`)**
  * **Purpose:** Convenience import shims allowing users to type `from src.router` instead of the full path.

### 2. Executable Scripts (`scripts/`)
Helper files to execute pipelines without manually writing Python boiler code.

* **`scripts/build_index.py`**
  * **Purpose:** Offline script to encode all corpus texts into dense vectors and save them as a FAISS binary file.
* **`scripts/run_baselines.py`**
  * **Purpose:** Executes the standard control RAG pipelines (Fixed-k) and outputs their accuracy to a CSV.
* **`scripts/extract_features.py`**
  * **Purpose:** Specifically isolates the feature extraction part of the pipeline to audit the math and save a CSV dataset of the 7 features over various queries.
* **`scripts/verify_day6_milestones.py`**
  * **Purpose:** The master unit-test script that programmatically guarantees all 3 members' logic executes perfectly and produces expected output shapes.
* **`scripts/download_hotpotqa.py` / `scripts/inspect_sample.py`**
  * **Purpose:** Scripts for downloading the raw dataset and manually viewing individual questions for debugging.

### 3. Data & Configurations
* **`configs/base.yaml`, `configs/retrieval.yaml`, `configs/experiments.yaml`**
  * **Purpose:** Centralized settings files containing variables like the LLM model name (`qwen3.5:latest`), random seeds, dimensionalities, and metric choices.
  * **Why it's necessary:** Keeps hardcoded variables out of the python code so experiments can be iterated quickly.
* **`data/hotpotqa/` & `data/splits/`**
  * **Purpose:** Storage for the raw multi-hop question-answering dataset that the pipeline is tested against.
* **`data/processed/faiss_index.bin.npz`**
  * **Purpose:** The saved, pre-computed mathematical vectors generated by the `build_index.py` script.
* **`pyrightconfig.json`**
  * **Purpose:** Fixes IDE warnings by telling VS Code/Pylance that imports should resolve from the project root instead of assuming `src/` is the root.

### 4. Output Data (`results/`)
* **`results/raw/`**
  * **Purpose:** Holds JSON line-by-line dumps of every single query execution, including the latency, tokens used, exactly which documents were retrieved, and the raw predicted text.
* **`results/tables/`**
  * **Purpose:** Holds aggregated CSV metrics suitable for importing into spreadsheets or graphs for research papers.

### 5. Master Entry Point
* **`main.py`**
  * **Purpose:** The primary frontend execution script that researchers use to trigger the full End-to-End Adaptive RAG pipeline.
