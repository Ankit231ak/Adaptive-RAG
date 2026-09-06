# Adaptive RAG — Evidence-State Retrieval Controller

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3110/)
[![Package Manager: uv](https://img.shields.io/badge/package_manager-uv-astral.svg)](https://github.com/astral-sh/uv)

Adaptive RAG is a research repository building a post-retrieval evidence-state controller that dynamically predicts whether an additional retrieval batch (e.g. $k=5 \to k=10$) will materially improve answer quality.

---

## Table of Contents
- [Quick Start & Environment Setup](#quick-start--environment-setup)
- [Project Architecture & Modular Structure](#project-architecture--modular-structure)
  - [Role-Based Module Directories (`src/`)](#role-based-module-directories-src)
  - [Version-Controlled Files](#version-controlled-files)
  - [Gitignored / Local Files](#gitignored--local-files)
- [Core Workflows & Commands](#core-workflows--commands)

---

## Quick Start & Environment Setup

This project uses [`uv`](https://github.com/astral-sh/uv) for fast, reproducible Python 3.11 dependency management.

```bash
# 1. Clone the repository
git clone https://github.com/Ankit231ak/Adaptive-RAG.git
cd Adaptive-RAG

# 2. Create Python 3.11 virtual environment using uv
uv venv --python 3.11

# 3. Activate the virtual environment
source .venv/bin/activate

# 4. Sync dependencies
uv sync
```

---

## Project Architecture & Modular Structure

The codebase is organized into clean, isolated subfolders by team roles to prevent overlapping or meshed modules:

```text
Adaptive-RAG/
├── configs/
│   └── base.yaml                 # Configuration (paths, seeds, sample targets)
├── src/
│   ├── common/                   # Shared utilities (config loading, seed setting)
│   │   ├── utils.py
│   │   └── __init__.py
│   ├── data_and_retrieval/       # [Member B - Ankit] Data loading & FAISS retrieval
│   │   ├── corpus.py             # Document schema & SHA-256 stable IDs
│   │   ├── loader.py             # HotpotQA parser & sample set generator
│   │   ├── retriever.py          # Retriever interface
│   │   └── __init__.py
│   ├── generation_and_eval/      # [Member C - Utsav] Generator & evaluation metrics
│   │   ├── generator.py          # GeneratorWrapper & frozen prompt template
│   │   ├── metrics.py            # Answer normalization, EM & F1 metrics
│   │   └── __init__.py
│   ├── method_and_controller/    # [Member A - Deepak] Controller & evidence features
│   │   ├── evidence_state.py     # V1 post-retrieval 7 evidence features
│   │   ├── oracle.py             # Delta-F1 threshold oracle labeller
│   │   ├── router.py             # Logistic Regression STOP/MORE controller
│   │   └── __init__.py
│   └── pipeline/                 # End-to-end integration pipeline
│       ├── adaptive_rag.py       # Adaptive RAG pipeline runner
│       └── __init__.py
├── scripts/
│   ├── download_hotpotqa.py      # HotpotQA dataset download script
│   └── inspect_sample.py        # Sample inspection & ID determinism verification
├── docs/
│   └── DECISION_LOG.md           # Ownership register & project decision log
├── results/
│   └── raw/hello_world_run.json  # Saved skeleton run output evidence
├── pyproject.toml                # uv dependency declarations
├── uv.lock                       # Locked dependency graph
├── .python-version               # Python version pin (3.11)
├── .gitignore                    # Local artifact exclusion rules
├── requirements.txt              # Standard pip requirements export
└── README.md                     # Project documentation
```

### Role-Based Module Directories (`src/`)

| Directory | Owner / Role | Primary Responsibility |
| :--- | :--- | :--- |
| `src/common/` | Shared | Cross-module helpers (`load_config`, `set_seed`). |
| `src/data_and_retrieval/` | **Member B (Ankit)** | Raw data loading, stable document IDs, corpus representation, retrieval. |
| `src/generation_and_eval/` | **Member C (Utsav)** | Prompt formatting, generator wrapper, HotpotQA normalization, EM/F1. |
| `src/method_and_controller/` | **Member A (Deepak)** | Post-retrieval evidence feature extraction, oracle labels, router classifier. |
| `src/pipeline/` | Integration | End-to-end pipeline linking Retriever, Controller, and Generator. |

---

### Gitignored / Local Files

| File / Pattern | Reason for Exclusion |
| :--- | :--- |
| `.venv/` | Local Python virtual environment directory. |
| `adaptive_rag_complete_master_project_plan_FINAL.pdf` | Local project reference PDF document. |
| `data/hotpotqa/*.json` | Raw HotpotQA dataset files (~670 MB total). |
| `data/processed/*.json` | Generated local corpus JSON caches. |
| `data/splits/*.json` | Generated local dataset sample splits. |
| `src/**/__pycache__/` | Compiled Python bytecode files. |

---

## Core Workflows & Commands

### 1. Environment Setup
```bash
uv venv --python 3.11
source .venv/bin/activate
uv sync
```

### 2. Download HotpotQA Dataset
```bash
python scripts/download_hotpotqa.py
```

### 3. Run Sample Inspection
```bash
python scripts/inspect_sample.py
```

### 4. Run One-Command Hello-World Skeleton
```bash
python main.py
```
