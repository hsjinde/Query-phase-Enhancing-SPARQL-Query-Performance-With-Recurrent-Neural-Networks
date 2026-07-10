# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Research/thesis codebase for an **end-to-end Knowledge Graph Question Answering (KGQA)** system over DBpedia. It takes a natural-language question, tags its tokens with semantic roles, resolves them to DBpedia URIs, classifies the question into a SPARQL structural template, generates and executes candidate SPARQL queries against the live DBpedia endpoint, and filters answers by expected answer type. Comments and prints are in Traditional Chinese; identifiers are in English.

There is **no build system, no test suite, and no packaging** — scripts are run directly with `python <script>.py` from the repo root. `requirements.txt` holds a verified-compatible dependency set (Python 3.9); `demo.py` is a minimal end-to-end runner. Import paths are relative to the repo root, and model/data paths are hardcoded as `./model/...`, `./data/...`, `./answer/...`, so scripts must be run with the working directory set to the repo root.

## Running

```bash
# End-to-end LCQUAD evaluation (main pipeline entry point)
python EndtoEnd.py

# QALD-7/8 variant of the pipeline
python QA_withDBpedia.py

# Score a produced end-to-end result spreadsheet (precision/recall/F1)
python end2end/end2end_eval.py
```

Both pipeline entry points force CPU (`CUDA_VISIBLE_DEVICES=-1`). There is **no CLI/argument interface**: the set of questions to run and the output `.xlsx` filename are edited inline in `main()` (e.g. `EndtoEnd.py` iterates a hardcoded list of row indices and writes `LCQUADendtoendnew_380.xlsx`). To change what runs, edit those literals rather than passing flags.

### Runtime dependencies (install manually)

`tensorflow`, `tensorflow_addons`, `transformers` (HuggingFace, uses `bert-base-cased`), `SPARQLWrapper`, `nltk` (needs `punkt`, `wordnet`, `averaged_perceptron_tagger`), `pandas`, `numpy`, `scikit-learn`/`joblib`, `openpyxl`, `sklearn-crfsuite`. Running also requires **network access to `http://dbpedia.org/sparql`** and the local SQLite dictionaries under `SQLite/`.

## Pipeline architecture

The flow in `EndtoEnd.py` / `QA_withDBpedia.py` chains these components (each is its own top-level module):

1. **Template classification** — `Preprocessor_Bert.py` (`LCQUAD`, `QALD_7`) / `Preprocessor_Glove.py`. An ensemble of ~13 per-position BERT binary classifiers (`model/<dataset>/Bert_*.h5`) produces a feature vector, then a loaded SVM (`model/LCQUAD/svm_LCQUAD`) maps it to a template index.
2. **ERC tagging** — `ERC_Tagger.py`. A BiLSTM+CRF sequence tagger (`CRF.py` provides the CRF layer) labels each token with an **ERC scheme**: `V` (query variable / question word), `E` (named entity), `R` (relation/property), `C` (class), plus `RR` and combined tags (`ER`, `CR`, ...). Two interchangeable feature backends selected by `use_bert`: GloVe (`data/embedding/`, `glove.6B.100d.txt`) or BERT. Model weights in `model/ERC/`.
3. **Token merge & parse** — `Preprocessor.py` merges multi-token entities using tag spans, lemmatizes, and POS-tags, producing a list of `Word` objects (`Word.py`: word/lemma/pos/erc). `CaculateEntityTag.py` holds the tag-combining / tag-accuracy helpers.
4. **Role extraction** — `EntityFinder.py` groups the tagged `Word`s into `V`, `E`, `R`, `RR`, `C` lists.
5. **URI resolution** — `DBpediaQueries.py`. Resolves entity strings to DBpedia URIs (`NamedEntityExtracting`), classes (`classExtracting`), and properties (`propertyExtracting`) via SPARQL against DBpedia plus **local SQLite lookup** through `LocalDbrMatcher.py` (`SQLite/DictAB.sqlite`, `SQLite/DictP.sqlite`, `SQLite/dbo_class.txt`).
6. **SPARQL generation** — `SPARQLgeneration.py`. Given the resolved URIs and a **template string**, builds triple patterns per character and assembles them into candidate `SELECT`/`ASK` queries (`C1`/`C2`/`C3` combinators), executes them via `DBpediaQueries`, and returns the answer set.
7. **Answer-type filtering** — `AnswerTypeExtractor.py`. Infers expected type (Boolean/Number/Person/Place/Date/Thing) from the question word and filters/normalizes the raw answers.

### The template code system

The classifier outputs an integer index into a `dictionary` list of short **template codes** (e.g. `'A'`, `'AA'`, `'AAB'`, `'BBB'`, `'D'`, `'abc'`, ...). In `SPARQLgeneration.SPARQLgeneration`, each character is dispatched to a triple-builder (`FunA`/`Funa`/`FunB`/`Funb`/`FunC`/`Func`/`FunD`). Uppercase vs lowercase encodes a variant of the same triple shape; `D` is the boolean/`ASK` template. `EndtoEnd.py` also carries an `ORG_dictionary` (older letter scheme) kept in parallel with the current `dictionary` — keep both index-aligned if you change one. When touching SPARQL output, treat the template code as the contract between the classifier and the generator.

## Layout

- Top-level `.py` files = pipeline modules (imported by relative name — keep them at repo root).
- `model/` — pretrained weights per dataset: `ERC/`, `LCQUAD/`, `QALD-7/`, `QALD-8/`, `QALD-9/` (`.h5` Keras models + the `svm_LCQUAD` joblib model).
- `data/` — `embedding/` (GloVe), `vocab/` (`lcquad-word.vocab`, `lcquad-pos.vocab`), `lcquad/`, `qald/` training/annotation spreadsheets.
- `tagger/` — pickled CRF models and feature/label vocabularies for the tagger.
- `answer/` — gold-answer spreadsheets per dataset (`LCQUAD-test.xlsx`, `QALD-7/8/9.xlsx`), the pipeline's input question sets.
- `end2end/` — produced end-to-end result spreadsheets and the `end2end_eval.py` / `newi_end2end_eval.py` scorers.
- `SQLite/` — local DBpedia dictionaries for URI matching.
- `Embedding/` — raw embedding text files (`glove.6B.100d.txt`, `pos_emb_*`).

Data (spreadsheets), inputs, and outputs are all Excel (`.xlsx`) handled with pandas/openpyxl. Evaluation joins gold vs. system answers with fuzzy string matching (`difflib.SequenceMatcher`, ratio > 0.9) and reports precision/recall/F1.

## Notes for editing

- The canonical runners are `EndtoEnd.py` (LC-QuAD) and `QA_withDBpedia.py` (QALD). Earlier scratch/duplicate experiment scripts have been removed; prefer editing the named pipeline modules above rather than reintroducing one-off copies.
- Large blocks of hand-written example inputs are parked in top-of-file triple-quoted strings (see `Preprocessor_Bert.py`, `SPARQLgeneration.py`) — useful as concrete examples of the `NamedEntity`/`Property`/`Class`/`E`/`R`/`C`/`template` data shapes each stage passes along.
- `DBpediaQueries` accumulates results in class-level (`__queryResult`) state; the pipeline calls `dbq.clearResult()` between questions. Preserve that reset if you add new query paths.
