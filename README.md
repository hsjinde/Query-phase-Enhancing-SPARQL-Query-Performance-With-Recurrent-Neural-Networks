# End-to-End Knowledge Graph Question Answering over DBpedia

An end-to-end **Knowledge Graph Question Answering (KGQA)** system that answers
natural-language questions by translating them into SPARQL queries and executing
them against [DBpedia](https://www.dbpedia.org/). Developed as a master's thesis
project and evaluated on the **LC-QuAD** and **QALD-7/8/9** benchmarks.

Given a question such as *“In which films did Julia Roberts as well as Richard
Gere play?”*, the system tags the semantic role of each token, links the tokens
to DBpedia entities / properties / classes, classifies the question into a SPARQL
structural template, generates and runs candidate queries, and filters the
results by the expected answer type.

## Pipeline

```
Question
   │
   ├─► Template classification   (BERT classifier ensemble + SVM)   → template code
   │
   ├─► ERC sequence tagging       (BiLSTM + CRF, GloVe or BERT)      → E / R / C / V tags
   │
   ├─► Token merge & parse        (lemmatize, POS, span-merge)       → Word objects
   │
   ├─► Role extraction            (group tokens by tag)              → E, R, RR, C lists
   │
   ├─► URI resolution             (DBpedia SPARQL + local SQLite)    → DBpedia URIs
   │
   ├─► SPARQL generation          (template → triple patterns)       → candidate queries
   │
   └─► Answer-type filtering      (Boolean/Number/Person/Place/…)    → final answers
```

**ERC tagging scheme:** each token is labelled with a role — `E` (named entity),
`R` (relation / property), `C` (class), `V` (query variable / question word),
plus combined tags (`ER`, `CR`, `RR`, …).

**Template codes:** the classifier emits a short code (e.g. `A`, `AAB`, `BBB`,
`D`), where each character maps to one triple-pattern builder in
[`SPARQLgeneration.py`](SPARQLgeneration.py). `D` denotes the boolean (`ASK`)
template.

## Repository layout

| Path | Purpose |
|------|---------|
| `EndtoEnd.py` | Main pipeline entry point (LC-QuAD end-to-end run) |
| `QA_withDBpedia.py` | Pipeline entry point for the QALD datasets |
| `ERC_Tagger.py`, `CRF.py` | BiLSTM+CRF semantic-role tagger |
| `Preprocessor*.py`, `Word.py`, `CaculateEntityTag.py` | Tokenization, lemmatization, tag merging |
| `EntityFinder.py`, `AnswerTypeExtractor.py` | Role extraction & answer-type inference |
| `DBpediaQueries.py`, `LocalDbrMatcher.py` | DBpedia SPARQL + local SQLite URI resolution |
| `SPARQLgeneration.py` | Template-driven SPARQL query construction |
| `end2end/end2end_eval.py` | Precision / Recall / F1 scorer |

> **Note:** trained models, embeddings, dictionaries and datasets (≈26 GB) are
> **not** included in this repository — they exceed GitHub's file-size limits and
> are excluded via `.gitignore`. The expected local layout is `model/`, `data/`,
> `Embedding/`, `SQLite/`, `tagger/`, and `answer/`. See
> [`CLAUDE.md`](CLAUDE.md) for the full architecture and data-layout reference.

## Setup

Developed on **Python 3.7 (CPU)**.

```bash
pip install -r requirements.txt

# One-time NLTK data
python -c "import nltk; nltk.download('punkt'); nltk.download('wordnet'); nltk.download('averaged_perceptron_tagger')"
```

Running the pipeline additionally requires:
- network access to the public endpoint `http://dbpedia.org/sparql`
- the trained models and local dictionaries in place (see note above)

## Usage

Scripts run from the repository root (paths are resolved relative to it):

```bash
python EndtoEnd.py            # LC-QuAD end-to-end pipeline
python QA_withDBpedia.py      # QALD pipeline
python end2end/end2end_eval.py   # score a produced result spreadsheet
```

There is no CLI: the questions to run and the output filename are configured
inline in each script's `main()`.

## Datasets

- **LC-QuAD** — Large-Scale Complex Question Answering Dataset
- **QALD-7 / 8 / 9** — Question Answering over Linked Data challenge sets

## Tech stack

TensorFlow / Keras · TensorFlow Addons (CRF) · HuggingFace Transformers
(`bert-base-cased`) · GloVe embeddings · scikit-learn · NLTK · SPARQLWrapper ·
SQLite · pandas
