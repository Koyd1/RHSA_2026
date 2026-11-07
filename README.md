# RHSA 2026 — Russian Hotel Sentiment Analysis

English-language research reproduction and extension of Elgeldawi et al. (2021), *Hyperparameter Tuning for Machine Learning Algorithms Used for Arabic Sentiment Analysis* ([DOI](https://doi.org/10.3390/informatics8040079)).

## Dataset

- **Source:** [Yandex Geo Reviews 2023](https://huggingface.co/datasets/d0rj/geo-reviews-dataset-2023); accommodation-related reviews.
- **Task:** binary Russian sentiment classification; `label=0` for source ratings 1–2 and `label=1` for 4–5.
- **Original balanced sample:** 5,608 reviews (2,804 per class). Labels are **rating-derived proxies**, not manually validated sentiment labels.
- **Data file:** `data/russian_hotel_ML_5608.csv` with `text,label` columns.
- **Stop-words:** `data/stopWords_ru_sentiment.csv`; negation terms must be kept.
- **Privacy/provenance:** do not commit tokens, raw personally identifying data, or private sources. Verify dataset license/redistribution terms before publication.

## Notebook and outputs

- `notebooks/Russian_Hotel_Sentiment_2026.ipynb` — main research notebook, downloads CSV from this repo and runs the experiment.
- `results/figures/` — figures in PNG/SVG/PDF after running Colab and explicitly publishing outputs.
- `results/metrics/` — experiment CSV and JSON metrics.
- `results/experiments/` — run-specific metadata, seeds and versions.
- `scripts/publish_results.py` — optional publishing of generated outputs from Colab (requires a GitHub token in Colab Secrets).

## Experimental safeguards

TF-IDF is trained within each training/CV fold. The untouched test split is not used to tune hyperparameters. Report cross-validation versus test performance separately, including Macro-F1, class-wise errors and uncertainty.

The original article used another language, collection procedure and labeling method. Result differences cannot be attributed to language alone.

## Run in Colab

Open the notebook from GitHub with Google Colab and select **Runtime → Run all**. For a short smoke test, use `PROFILE='quick'`; longer benchmark: `PROFILE='full'`.

Publishing results back to this repository is **opt-in**: it requires an authorized write token stored in Colab Secrets (`GITHUB_TOKEN`), never in notebook source.
