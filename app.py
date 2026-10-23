from pathlib import Path
from datetime import datetime
import streamlit as st
from sentiment_engine import analyze_review

st.set_page_config(page_title="AspectSentinel | NLP Project", page_icon="🔍", layout="centered")

st.markdown("""
<style>
.stApp {background: linear-gradient(145deg, #f8faff 0%, #f4f0ff 52%, #effbff 100%); color:#1f2937;}
.block-container {max-width: 900px; padding-top: 2rem; padding-bottom: 3rem;}
.hero {background: white; border: 1px solid #e5e7eb; border-radius: 20px; padding: 1.4rem 1.6rem; box-shadow: 0 8px 26px #25385812; margin-bottom: 1rem;}
.eyebrow {color:#6d28d9; font-size:.82rem; font-weight:700; letter-spacing:.08em; text-transform:uppercase;}
.hero h1 {margin:.25rem 0; color:#242044; font-size:2.1rem;}
.hero p {color:#526071; margin-bottom:0;}
.doc-card {background:white; border:1px solid #e5e7eb; border-radius:16px; padding:1rem 1.2rem; margin:.7rem 0;}
.small-note {color:#64748b; font-size:.9rem;}
</style>
<div class="hero">
  <div class="eyebrow">NLP Project • Rule-based Analysis</div>
  <h1>🔍 AspectSentinel</h1>
  <p>Aspect-Based Sentiment Analysis — explore customer-review text, clause-level sentiment, and readable Python code.</p>
</div>
""", unsafe_allow_html=True)

st.markdown("### 1. Enter customer feedback")
st.caption("This project uses a rule-based sentiment lexicon and phrase rules. It is not a trained machine-learning model.")
sample = "The delivery was quick, but the product stopped working the next day. The packaging was damaged."
review = st.text_area("Customer review", value=sample, height=125, placeholder="Type or paste a customer review...")
col1, col2 = st.columns([1, 1])
with col1:
    analyze_clicked = st.button("⚡ Analyze review", type="primary", use_container_width=True)
with col2:
    clear_clicked = st.button("Clear results", use_container_width=True)

if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None
if clear_clicked:
    st.session_state.analysis_result = None
if analyze_clicked:
    if review.strip():
        st.session_state.analysis_result = {"review": review.strip(), **analyze_review(review.strip())}
    else:
        st.warning("Enter a review before analyzing it.")

result = st.session_state.analysis_result
if result:
    st.markdown("### 2. Analysis output")
    a, b, c, d = st.columns(4)
    a.metric("Overall", result["overall"].title())
    b.metric("😊 Positive", result["counts"]["positive"])
    c.metric("😞 Negative", result["counts"]["negative"])
    d.metric("😐 Neutral", result["counts"]["neutral"])
    st.markdown("#### Sentence / clause results")
    for i, (sentence, prediction) in enumerate(zip(result["sentences"], result["predictions"]), start=1):
        label = prediction["sentiment"].title()
        with st.container(border=True):
            left, right = st.columns([5, 1])
            left.markdown(f"**Part {i}**  \n{sentence}")
            right.markdown(f"**{label}**  \nScore: `{prediction['score']}`")
    report_lines = [
        "AspectSentinel — Customer Review Sentiment Report",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", "",
        "Review:", result["review"], "", f"Overall sentiment: {result['overall'].title()}",
        f"Positive: {result['counts']['positive']}", f"Negative: {result['counts']['negative']}",
        f"Neutral: {result['counts']['neutral']}", "", "Sentence / clause analysis:"
    ]
    for i, (sentence, prediction) in enumerate(zip(result["sentences"], result["predictions"]), start=1):
        report_lines.append(f"Part {i} [{prediction['sentiment']}; score {prediction['score']}]: {sentence}")
    st.download_button("⬇️ Download sentiment report (.txt)", "\n".join(report_lines),
                       file_name="sentiment-report.txt", mime="text/plain")

st.divider()
st.markdown("### 3. Python code document")
st.markdown("The sections below show the actual Python source code, like code cells in a notebook. They are not HTML frontend code.")
engine_path = Path(__file__).with_name("sentiment_engine.py")
engine_code = engine_path.read_text(encoding="utf-8") if engine_path.exists() else "Source file not found."
with st.expander("View complete sentiment_engine.py", expanded=False):
    st.code(engine_code, language="python", line_numbers=True)
st.download_button("📄 Download Python source code", engine_code,
                   file_name="sentiment_engine.py", mime="text/x-python")

st.markdown("#### How the analysis works")
with st.container(border=True):
    st.markdown("**Step 1 — Text normalization**")
    st.code('clean = normalize(sentence)', language="python")
    st.markdown("Convert text to lowercase, expand common contractions, and remove punctuation before matching words.")
with st.container(border=True):
    st.markdown("**Step 2 — Sentiment scoring**")
    st.code('prediction = score_sentence(sentence)', language="python")
    st.markdown("Use positive and negative word weights, phrase patterns, negation, and intensifiers to calculate a rule-based score.")
with st.container(border=True):
    st.markdown("**Step 3 — Overall sentiment**")
    st.code('result = analyze_review(review)', language="python")
    st.markdown("Count positive, negative, and neutral clauses. If the highest counts tie, the overall label is Mixed.")

st.markdown("---")
st.caption("AspectSentinel • College NLP project • Rule-based sentiment analysis")
