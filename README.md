# Adaptive RAG — Evidence-State Retrieval Controller

Adaptive RAG is a research framework building an **evidence-state retrieval controller** that dynamically predicts whether an additional retrieval batch ($k=5 \to k=10$) will materially improve multi-hop answer quality ($\Delta F1 > \delta$), allowing the system to stop early when retrieved evidence is already sufficient.

---

## Codebase Architecture & File Purposes

Below is a comprehensive guide to every meaningful file in this project and why it exists. *(Note: Standard auto-generated configuration and environment files like `.venv`, `.gitignore`, `uv.lock`, and the `docs/` folder have been excluded for brevity).*

### 1. Source Code (`src/`)
This is where the core logic of the pipeline lives. It is divided among the three team members.

#### Member B (Ankit) - Data & Retrieval Pipeline
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

#### Member C (Utsav) - Generation & Evaluation Pipeline
* **`src/generation_and_eval/generator.py`**
  * **Purpose:** Connects to the local Ollama LLM (`qwen3.5:latest`) and builds the prompt structures (Direct vs RAG context).
  * **Why it's necessary:** This is the "brain" that actually reads the retrieved documents and types out the final answer to the user's question.
* **`src/generation_and_eval/metrics.py`**
  * **Purpose:** Houses mathematical scoring formulas like Exact Match (EM), F1-Score, MRR, and Recall.
  * **Why it's necessary:** We need hard numbers to prove if our answers are actually getting better.

#### Member A (Deepak) - Method & Controller Pipeline
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
  * **Purpose:** The master orchestration file that chains Ankit's Retriever, Deepak's Controller, and Utsav's Generator together into a single pipeline.
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
