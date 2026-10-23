# 🔍 AspectSentinel — Aspect-Based Sentiment Analysis

✨ A Natural Language Processing (NLP) project that analyzes customer reviews and classifies their sentiment using a pretrained BERT model.

## 🚀 Features

* 📝 Analyze customer reviews
* ✂️ Split reviews into sentences and clauses
* 😊 Identify positive, negative, and neutral sentiment
* 📊 Display overall sentiment counts
* 🎯 Show sentiment confidence percentages
* 🤖 Use a pretrained multilingual BERT sentiment model

## 🛠️ Technologies Used

* 🐍 Python
* 🤖 Transformers
* 🔥 PyTorch
* 🧠 Natural Language Processing (NLP)

## ⚙️ How It Works

1. Enter a customer review or press Enter to use the sample review.
2. The review is split into smaller clauses.
3. The pretrained model predicts sentiment for each clause.
4. The program displays individual results, confidence percentages, and overall sentiment counts.

## ▶️ How to Run

**1. Install the required libraries**

```bash
pip install torch transformers
```

**2. Run the Python file**

```bash
python app.py
```


**3. Enter a review** when prompted, or press Enter to analyze the sample review.

## 📌 Model

`nlptown/bert-base-multilingual-uncased-sentiment`

The pretrained model predicts ratings from one to five stars, which the program groups into positive, negative, and neutral sentiment.

## 🎓 Project Purpose

📚 Created as a college NLP project to explore customer feedback analysis and sentiment classification.

---

💡 **AspectSentinel** — Turning customer reviews into sentiment insights.
