# 🔍 AspectSentinel — Streamlit NLP Project

A document-style Streamlit app for Aspect-Based Sentiment Analysis. It provides customer-review input, clause-level rule-based sentiment results, a downloadable text report, and a readable view/download of the Python source code.

## Run locally

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

## Deploy on Streamlit Community Cloud

1. Upload `app.py`, `sentiment_engine.py`, and `requirements.txt` to the root of your GitHub repository.
2. Open Streamlit Community Cloud and sign in with GitHub.
3. Choose **Create app** and select the repository, branch `main`, and main file path `app.py`.
4. Click **Deploy**.

This app uses a rule-based lexicon and phrase-matching approach ported from the project's JavaScript implementation. It is not a trained ML model and does not use a dedicated aspect-extraction model.
