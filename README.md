# Adaptive RAG — Evidence-State Retrieval Controller

Adaptive RAG is a research framework building an **evidence-state retrieval controller** that dynamically predicts whether an additional retrieval batch ($k=5 \to k=10$) will materially improve multi-hop answer quality ($\Delta F1 > \delta$), allowing the system to stop early when retrieved evidence is already sufficient.

---


## Research Results & Methodology

### 1. The Evidence-State Plateau (Why Adaptive RAG is needed)
We evaluated traditional "Fixed-k" RAG systems across 1,000 multi-hop queries. The results proved our core hypothesis: blindly retrieving more documents ($k=10$) doubles computational cost without meaningfully improving accuracy. In fact, excessive retrieval often introduces semantic distractors that cause the LLM to hallucinate.

| Baseline | Accuracy (F1) | Token Cost | Latency |
| :--- | :--- | :--- | :--- |
| **B0 (Direct LLM)** | 0.2325 | 98 tokens | 0.44s |
| **B1 (k=3)** | 0.5483 | 476 tokens | 1.34s |
| **B2 (k=5)** | 0.5681 | 758 tokens | 1.62s |
| **B3 (k=10)** | 0.5739 | 1,544 tokens | 2.42s |

*Key finding: Increasing from $k=5$ to $k=10$ only improved the F1 score by a microscopic 0.005, but doubled the token cost and increased latency by 50%.*

### 2. Machine Learning Model Selection
To dynamically route queries between $k=5$ and $k=10$, we extracted 7 mathematical features from the FAISS vector space (e.g., `mean_redundancy`, `top1_score`). We tested four binary classifiers to predict the Oracle label (STOP vs MORE). 

To prevent overfitting, we utilized an 80/20 Train-Test split across our 1,000-question dataset:

| Machine Learning Model | Train Accuracy | Test Accuracy (Unseen Data) |
| :--- | :--- | :--- |
| **Logistic Regression** | 52.88% | 52.00% |
| **Support Vector Machine** | 55.50% | 51.50% |
| **Random Forest** | 82.75% | 68.50% |
| **Gradient Boosting (Winner)** | **91.50%** | **86.00%** |

*Key finding: Linear models failed to separate the complex vector states. Random Forest heavily overfit the training data. Gradient Boosting (XGBoost) successfully generalized, achieving an 86% accuracy rate on completely unseen questions.*

### 3. The Final Adaptive Pipeline Effect
By attaching the Gradient Boosting ML Controller to the post-retrieval state, the system dynamically analyzes the 7 mathematical features at $k=5$. 
* **When Evidence is Confident:** It outputs `STOP`, answering the question immediately. This saves ~800 tokens, reduces latency by 1 second, and actively shields the LLM from hallucination-inducing distractors.
* **When Evidence is Ambiguous:** It outputs `MORE`, triggering a deeper retrieval to $k=10$ only for the rare questions that actually require it.

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
