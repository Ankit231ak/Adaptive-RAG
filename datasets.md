# Datasets

This project uses two multi-hop question-answering datasets:

1. **2WikiMultiHopQA**
2. **HotpotQA**

---

## 1. 2WikiMultiHopQA

**Dataset URL:**  
https://huggingface.co/datasets/DEAD-2/2wikimultihopqa

```yaml
dataset: 2WikiMultiHopQA

url: https://huggingface.co/datasets/DEAD-2/2wikimultihopqa

train_file: train.json
dev_file: dev.json

sample_size: 1000
random_seed: 42

embedding_model: all-MiniLM-L6-v2
initial_k: 3
maximum_k: 10

controller: LogisticRegression
```

A public 2WikiMultiHopQA dataset implementation is also available on Hugging Face. Its dataset files use JSON data containing questions, answers, and contexts.  
url2WikiMultiHopQA dataset sourcehttps://huggingface.co/datasets/DEAD-2/2wikimultihopqa

---

## 2. HotpotQA

**Dataset URL:**  
https://hotpotqa.github.io/

```yaml
dataset: HotpotQA

url: https://hotpotqa.github.io/

train_file: hotpot_train_v1.1.json
dev_file: hotpot_dev_distractor_v1.json

sample_size: 1000
random_seed: 42

embedding_model: all-MiniLM-L6-v2
initial_k: 3
maximum_k: 10

controller: LogisticRegression
```

The official HotpotQA repository provides the training and distractor development files and documents their JSON format. citeturn0search0

**Official dataset page:**  
urlHotpotQA official websitehttps://hotpotqa.github.io/

**Official GitHub repository:**  
urlHotpotQA GitHub repositoryhttps://github.com/hotpotqa/hotpot

---

## Local Directory Structure

After downloading the datasets, the project can use:

```text
data/
├── 2wikimultihopqa/
│   ├── train.json
│   └── dev.json
│
└── hotpotqa/
    ├── hotpot_train_v1.1.json
    └── hotpot_dev_distractor_v1.json
```

Do not upload the raw dataset files to GitHub. Add them to `.gitignore`:

```gitignore
data/*.json
data/*.jsonl
data/*.parquet
```

---

## Experiment Configuration

Both datasets use the same initial experimental settings:

```yaml
sample_size: 1000
random_seed: 42

embedding_model: all-MiniLM-L6-v2

initial_k: 3
maximum_k: 10

controller: LogisticRegression
```

### Meaning

- `sample_size`: Number of questions used in the initial experiment.
- `random_seed`: Makes sampling reproducible.
- `embedding_model`: Converts questions/documents into vectors for retrieval.
- `initial_k`: Number of documents retrieved in the first retrieval step.
- `maximum_k`: Maximum retrieval depth/budget used in the experiment.
- `controller`: ML model that predicts whether retrieval should stop or continue.

---

## Research Pipeline

```text
Dataset
   ↓
Question + Context
   ↓
Embedding Model
   ↓
FAISS Retriever
   ↓
Initial Retrieval (k=3)
   ↓
Evidence Features
   ↓
Logistic Regression Controller
   ↓
┌───────────────┐
│               │
STOP        NEXT HOP
│               │
↓               ↓
Answer      Retrieve More
                │
                ↓
             k ≤ 10
                │
                ↓
              Answer
```
