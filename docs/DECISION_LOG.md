# Adaptive RAG — Project Decision Log & Ownership Register

## 1. Fixed Team Role Assignments

| Member | Name | Primary Role | Owned Modules & Components |
| :--- | :--- | :--- | :--- |
| **Member A** | Deepak | Method & Controller | `src/router.py`, `src/evidence_state.py`, `src/oracle.py`, `src/adaptive_rag.py` |
| **Member B** | Ankit | Data & Retrieval | `src/data.py`, `src/corpus.py`, `src/retriever.py`, `scripts/download_hotpotqa.py` |
| **Member C** | Utsav | Generation & Evaluation | `src/generator.py`, `src/metrics.py`, `main.py` |

---

## 2. Core Architecture Decisions

### Decision 1: Answer Normalization & Metrics
- **Decision**: Adopt official HotpotQA evaluation metrics (lowercasing, punctuation stripping, article removal, token-level F1 and EM match).
- **Owner**: Member C (Utsav)
- **Status**: Implemented in `src/metrics.py`.

### Decision 2: Fixed Prompt Template
- **Decision**: Implement a frozen instruction-tuned prompt template formatting retrieved passages concisely:
  ```text
  SYSTEM: You are an accurate question-answering assistant.
  CONTEXT: Passage [1] (Title): Text ...
  QUESTION: ...
  ANSWER:
  ```
- **Owner**: Member C (Utsav)
- **Status**: Implemented in `src/generator.py`.

### Decision 3: Deterministic Stable Document IDs
- **Decision**: Generate document IDs using SHA-256 hash:
  $$\text{doc\_id} = \text{"doc\_"} + \text{SHA256}(\text{title} + "\backslash\text{n}" + \text{text})[:12]$$
- **Owner**: Member B (Ankit)
- **Status**: Implemented in `src/corpus.py`.

### Decision 4: Hello-World Executable
- **Decision**: `python main.py` runs the skeleton pipeline end-to-end and outputs structured evidence to `results/raw/hello_world_run.json`.
- **Owner**: All Members
- **Status**: Implemented & Verified in `main.py`.

---

## 3. Milestone Completion Checklist

- [x] Generator wrapper with fixed prompt template (`src/generator.py`).
- [x] Answer normalization & EM/F1 metric functions (`src/metrics.py`).
- [x] End-to-end pipeline runner executed via single command (`python main.py`).
- [x] Fixed team roles documented with no unowned code branch.
- [x] Evidence output saved (`results/raw/hello_world_run.json` & `docs/DECISION_LOG.md`).
